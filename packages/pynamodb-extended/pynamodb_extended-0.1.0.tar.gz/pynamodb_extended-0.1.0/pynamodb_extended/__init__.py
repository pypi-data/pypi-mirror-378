import base64
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TypeVar, Generic
from datetime import datetime, timezone
from enum import StrEnum
from functools import cached_property
from concurrent.futures import ThreadPoolExecutor, as_completed

from pynamodb.models import Model, _KeyType
from pynamodb.attributes import _T, Attribute, MapAttribute
from pynamodb.expressions.condition import Condition
from pynamodb.expressions.update import Action
from pynamodb.expressions.operand import Path

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def current_datetime():
    return datetime.now(tz=timezone.utc)


def compound_id(*ids):
    return "#".join(str(i) for i in ids)


@dataclass
class DDBStreamImage:
    keys: dict
    sequence_number: str
    size_bytes: int
    stream_view_type: str
    old_image: dict = None
    new_image: dict = None

    def serialized(self):
        return {
            "Keys": self.keys,
            "OldImage": self.old_image,
            "NewImage": self.new_image,
            "SequenceNumber": self.sequence_number,
            "SizeBytes": self.size_bytes,
            "StreamViewType": self.stream_view_type,
        }

    @classmethod
    def from_raw(cls, image):
        return cls(
            keys=image.get("Keys"),
            old_image=image.get("OldImage"),
            new_image=image.get("NewImage"),
            sequence_number=image.get("SequenceNumber"),
            size_bytes=image.get("SizeBytes"),
            stream_view_type=image.get("StreamViewType"),
        )

    @property
    def key_values(self):
        vals = []
        for val in self.keys.values():
            for k, v in val.items():
                match k:
                    case "B" | "S":
                        vals.append(v)
                    case "N":
                        vals.append(float(v) if "." in str(v) else int(v))
        return tuple(vals)


ModelT = TypeVar("ModelT", bound=Model)


@dataclass
class DDBStreamRecord(Generic[ModelT]):
    event_id: str
    event_name: str
    event_version: str
    event_source: str
    aws_region: str
    dynamodb: DDBStreamImage
    event_source_arn: str
    keys: tuple = None
    old_model: ModelT = None
    new_model: ModelT = None

    def serialized(self):
        return {
            "eventId": self.event_id,
            "eventName": self.event_name,
            "eventVersion": self.event_version,
            "eventSource": self.event_source,
            "awsRegion": self.aws_region,
            "dynamodb": self.dynamodb,
            "eventSourceArn": self.event_source_arn,
        }

    @classmethod
    def from_raw(cls, record: dict, model_type: type[Model]):
        ddb = record.get("dynamodb")
        ddb = ddb if isinstance(ddb, DDBStreamImage) else DDBStreamImage.from_raw(ddb)
        return cls(
            event_id=record.get("eventId"),
            event_name=record.get("eventName"),
            event_version=record.get("eventVersion"),
            event_source=record.get("eventSource"),
            aws_region=record.get("awsRegion"),
            dynamodb=ddb,
            event_source_arn=record.get("eventSourceArn"),
            keys=ddb.key_values,
            old_model=(
                model_type.from_raw_data(ddb.old_image)
                if ddb.stream_view_type
                in [StreamType.old_image, StreamType.new_and_old_images]
                and ddb.old_image
                else None
            ),
            new_model=(
                model_type.from_raw_data(ddb.new_image)
                if ddb.stream_view_type
                in [StreamType.new_image, StreamType.new_and_old_images]
                and ddb.new_image
                else None
            ),
        )


class StreamType(StrEnum):
    keys_only = "KEYS_ONLY"
    new_image = "NEW_IMAGE"
    old_image = "OLD_IMAGE"
    new_and_old_images = "NEW_AND_OLD_IMAGES"


class StreamEventName(StrEnum):
    insert = "INSERT"
    modify = "MODIFY"
    remove = "REMOVE"


@dataclass
class StreamHandler:
    handler: Callable
    stream_view_type: str


class StreamableModel(Model):
    stream_handlers = None
    old_serialized = None

    @cached_property
    def _capture_old(self):
        return self.__class__.stream_handlers and any(
            [
                sh
                for sh in self.stream_handlers
                if sh.stream_view_type
                in [StreamType.old_image, StreamType.new_and_old_images]
            ]
        )

    def capture_old(self):
        if self.__class__.stream_handlers and self._capture_old:
            self.old_serialized = self.serialize()

    @classmethod
    def stream_handler(
        cls,
        test_local=False,
        stream_view_type: str = StreamType.new_image,
        event_names: list[StreamEventName] = None,
    ):
        if event_names is None:
            event_names = [
                StreamEventName.insert,
                StreamEventName.remove,
                StreamEventName.modify,
            ]

        def decorator(func: Callable):
            # logger.info(f"Registering {func.__name__} with local: {test_local}")
            if test_local:
                handler = StreamHandler(func, stream_view_type)
                if cls.stream_handlers is None:
                    cls.stream_handlers = [handler]
                else:
                    cls.stream_handlers.append(handler)

            def wrapper(event, context):
                # logger.info("Received stream event", extra=event)
                records = event.get("Records", [])
                records = [r for r in records if r.get("eventName") in event_names]
                func([DDBStreamRecord[cls].from_raw(r, cls) for r in records])

            return wrapper

        return decorator

    def send_stream(self, event_name: str):
        if self.__class__.stream_handlers:
            for handler in self.__class__.stream_handlers:
                handler.handler(
                    [self.__generate_record(handler.stream_view_type, event_name)]
                )

    def __generate_record(
        self, stream_view_type: str, event_name: str
    ) -> DDBStreamRecord:
        hash_key_attr_name = self._hash_key_attribute().attr_name
        range_key_attr_name = None
        if self._range_key_attribute() is not None:
            range_key_attr_name = self._range_key_attribute().attr_name
        keys = {
            k: v
            for k, v in self.serialize().items()
            if k in [hash_key_attr_name, range_key_attr_name]
        }
        image = DDBStreamImage(
            keys=keys,
            sequence_number="1",
            size_bytes=len(json.dumps(keys)),
            stream_view_type=stream_view_type,
        )
        if stream_view_type in [StreamType.new_image, StreamType.new_and_old_images]:
            new_image = self.serialize()
            image.size_bytes += len(json.dumps(new_image))
            image.new_image = new_image
        if (
            stream_view_type in [StreamType.old_image, StreamType.new_and_old_images]
            and self.old_serialized
        ):
            image.size_bytes += len(json.dumps(self.old_serialized))
            image.old_image = self.old_serialized
        record = DDBStreamRecord[self.__class__](
            event_id=str(uuid.uuid4()),
            event_name=event_name,
            event_version="1.0",
            event_source="aws:dynamodb",
            aws_region="us-east-1",
            event_source_arn="stream-ARN",
            dynamodb=image,
            keys=self._get_serialized_keys(),
        )
        if stream_view_type in [StreamType.new_image, StreamType.new_and_old_images]:
            record.new_model = self
        if (
            stream_view_type in [StreamType.old_image, StreamType.new_and_old_images]
            and self.old_serialized
        ):
            record.old_model = self.from_raw_data(self.old_serialized)
        return record

    def save(
        self,
        condition: Optional[Condition] = None,
        *,
        add_version_condition: bool = True,
    ) -> Dict[str, Any]:
        # TODO: This approach to capturing old is going to give us the same data as new
        self.capture_old()
        data = super().save(
            condition=condition, add_version_condition=add_version_condition
        )
        self.send_stream(StreamEventName.insert)
        return data

    def update(
        self,
        actions: List[Action],
        condition: Optional[Condition] = None,
        *,
        add_version_condition: bool = True,
    ) -> Any:
        self.capture_old()
        result = super().update(
            actions=actions,
            condition=condition,
            add_version_condition=add_version_condition,
        )
        self.send_stream(StreamEventName.modify)
        return result

    def delete(
        self,
        condition: Optional[Condition] = None,
        *,
        add_version_condition: bool = True,
    ) -> Any:
        self.capture_old()
        result = super().delete(
            condition=condition, add_version_condition=add_version_condition
        )
        self.send_stream(StreamEventName.remove)
        return result


def watched(
    cls: type[Attribute], set_hook: Callable = None, update_hook: Callable = None
) -> type:
    def set_(
        attr: Attribute, instance: "WatchedUpdateModel", value: Optional[_T]
    ) -> None:
        cls.__set__(attr, instance, value)
        if instance.init_complete and set_hook is not None:
            set_hook(attr, value, instance)

    cls_attrs = dict(
        __set__=set_,
        watched=True,
        update_hook=update_hook,
        set_hook=set_hook,
    )
    return type(f"Watched{cls.__name__}", (cls,), cls_attrs)


class WatchedUpdateModel(Model):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__watched = [
            (k, v)
            for k, v in cls.__dict__.items()
            if isinstance(v, Attribute) and hasattr(v, "watched") and v.watched
        ]
        cls.__watched_attr = [v for k, v in cls.__watched]

    def __init__(
        self,
        hash_key: Optional[_KeyType] = None,
        range_key: Optional[_KeyType] = None,
        _user_instantiated: bool = True,
        **attributes: Any,
    ) -> None:
        self.init_complete = False
        super().__init__(
            hash_key=hash_key,
            range_key=range_key,
            _user_instantiated=_user_instantiated,
            **attributes,
        )
        for attr_name, attribute in self.__watched:
            if attribute.set_hook is not None:
                attribute.set_hook(getattr(self, attr_name), self)
        self.init_complete = True

    def update(
        self,
        actions: List[Action],
        condition: Optional[Condition] = None,
        *,
        add_version_condition: bool = True,
    ) -> Any:
        additional_actions = []
        for action in actions:
            op = action.values[0]
            if isinstance(op, Path):
                if hasattr(op.attribute, "watched") and op.attribute.watched:
                    if op.attribute.update_hook is not None:
                        additional = op.attribute.update_hook(action, self)
                        if additional:
                            additional_actions.extend(additional)
        actions.extend(additional_actions)
        return super().update(
            actions=actions,
            condition=condition,
            add_version_condition=add_version_condition,
        )


class StorageBackedModel(Model):
    CUSTOM_ATTRIBUTES = []

    def __init__(
        self,
        hash_key: Optional[_KeyType] = None,
        range_key: Optional[_KeyType] = None,
        _user_instantiated: bool = True,
        **attributes: Any,
    ) -> None:
        attrs = {k: v for k, v in attributes.items() if k not in self.CUSTOM_ATTRIBUTES}
        super().__init__(
            hash_key=hash_key,
            range_key=range_key,
            _user_instantiated=_user_instantiated,
            **attrs,
        )
        for attr in self.CUSTOM_ATTRIBUTES:
            if attributes.get(attr):
                setattr(self, attr, attributes[attr])

    @property
    def loaded_attribute_values(self):
        attrs = self.attribute_values.copy()
        with ThreadPoolExecutor() as executor:
            future_tasks = [
                executor.submit(load_attribute, self, attrs, attr)
                for attr in self.CUSTOM_ATTRIBUTES
            ]
            for future in as_completed(future_tasks):
                pass
        return attrs


def load_attribute(model: Model, attrs: dict, attr_name: str):
    uri = attrs.pop(f"{attr_name}_uri", None)
    if uri:
        attrs[attr_name] = getattr(model, attr_name)


class DateTimeAttribute(Attribute[datetime]):
    """
    An attribute for storing a Datetime in ISO format adjusted to UTC
    Refactored from Pynamodb UTCDateTimeAttribute as of version 6.0
    Key difference is dropping the +0000 fixed offset that doesn't add any value
    """

    attr_type = "S"

    def serialize(self, value):
        """
        Takes a datetime object and returns a string
        """
        if value.tzinfo is None:
            # Assign a timezone based on src device if not present
            value = value.astimezone()
        fmt = value.astimezone(timezone.utc).strftime(DATETIME_FORMAT).zfill(26)
        return fmt

    def deserialize(self, value):
        """
        Takes a datetime string and returns a datetime object
        """
        return fast_parse_utc_date_string(value)


def fast_parse_utc_date_string(date_string: str) -> datetime:
    # Method to quickly parse strings formatted with '%Y-%m-%dT%H:%M:%S.%f+0000'.
    # This is ~5.8x faster than using strptime and 38x faster than dateutil.parser.parse.
    _int = int  # Hack to prevent global lookups of int, speeds up the function ~10%
    try:
        # Fix pre-1000 dates serialized on systems where strftime doesn't pad w/older PynamoDB versions.
        date_string = date_string.zfill(26)
        if (
            len(date_string) != 26
            or date_string[4] != "-"
            or date_string[7] != "-"
            or date_string[10] != "T"
            or date_string[13] != ":"
            or date_string[16] != ":"
            or date_string[19] != "."
        ):
            raise ValueError(
                "Datetime string '{}' does not match format '{}'".format(
                    date_string, DATETIME_FORMAT
                )
            )
        return datetime(
            _int(date_string[0:4]),
            _int(date_string[5:7]),
            _int(date_string[8:10]),
            _int(date_string[11:13]),
            _int(date_string[14:16]),
            _int(date_string[17:19]),
            _int(date_string[20:26]),
            timezone.utc,
        )
    except (TypeError, ValueError):
        raise ValueError(
            "Datetime string '{}' does not match format '{}'".format(
                date_string, DATETIME_FORMAT
            )
        )


class DatedModel(Model):
    created_datetime = DateTimeAttribute(
        attr_name="createdDatetime", default=current_datetime
    )
    updated_datetime = DateTimeAttribute(
        attr_name="updatedDatetime", default=current_datetime
    )

    # TODO: Investigate what method is called on batch_write, this isn't called
    def save(
        self,
        condition: Optional[Condition] = None,
        *,
        add_version_condition: bool = True,
    ) -> Dict[str, Any]:
        self.updated_datetime = current_datetime()
        return super().save(
            condition=condition, add_version_condition=add_version_condition
        )


def as_dict(value, use_alias=False, serializable=True):
    if isinstance(value, MapAttribute) or isinstance(value, Model):
        value_dict = value.to_simple_dict() if use_alias else value.attribute_values
        return {k: as_dict(v) for k, v in value_dict.items()}
    elif isinstance(value, list) or isinstance(value, set):
        return [as_dict(v) for v in value]
    elif isinstance(value, datetime) and serializable:
        return value.isoformat()
    elif isinstance(value, bytes) and serializable:
        return base64.b64encode(value).decode("utf-8")
    else:
        return value
