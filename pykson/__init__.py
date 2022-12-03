import uuid
import decimal
from enum import Enum
from typing import Dict, Any, List, Optional, TypeVar, Union, Type, Set, Generic
import six
import csv
import copy
import pytz
import json
import datetime
import jdatetime
# noinspection PyPackageRequirements
from dateutil import parser


# name = "pykson"


class JsonSerializable:
    pass


class FieldType(Enum):
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3
    STRING = 4
    LIST = 5
    DATE = 6
    TIME = 7
    DATETIME = 8
    DICT = 9
    BYTES = 10
    BYTE_ARRAY = 11
    FUNCTION = 12


class Field(JsonSerializable):
    # noinspection PyMethodMayBeStatic
    def get_json_formatted_value(self, value):
        return value

    # noinspection PyProtectedMember
    def __get__(self, instance, owner):
        if instance is None:
            raise Exception('Cannot access field without instance')
        return instance._data.get(self.serialized_name, self.default_value)

    # noinspection PyProtectedMember
    def __set__(self, instance, value, test: bool = False):
        if not self.null:
            assert value is not None, "Null value passed for not nullable field \'" + self.name + "\' in class " + str(
                type(instance))
        if test is False:
            if instance is None:
                raise Exception('Cannot access field without instance')
            instance._data[self.serialized_name] = value

    def __init__(self,
                 field_type: FieldType,
                 serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[Any] = None):
        self.field_type = field_type
        self.serialized_name = serialized_name  # field name in serialized json
        self.name = None  # field name in the defined class
        self.null = null
        self.default_value = default_value


# noinspection DuplicatedCode,PyBroadException
class IntegerField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str) and value != '' and self.accepts_string:
            try:
                value = int(value)
            except Exception:
                pass
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if self.min_value is not None:
            assert value >= self.min_value
        if self.max_value is not None:
            assert value <= self.max_value
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[int] = None,
                 accepts_string: bool = False,
                 min_value: Optional[int] = None, max_value: Optional[int] = None):
        super(IntegerField, self).__init__(field_type=FieldType.INTEGER,
                                           serialized_name=serialized_name,
                                           null=null,
                                           default_value=default_value)
        self.accepts_string = accepts_string
        assert default_value is None or isinstance(default_value, int)
        assert min_value is None or isinstance(min_value, int)
        assert max_value is None or isinstance(max_value, int)
        if min_value is not None and max_value is not None:
            assert min_value <= max_value
        self.min_value = min_value
        self.max_value = max_value


# noinspection DuplicatedCode
class FloatField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str) and value != '' and self.accepts_string:
            try:
                value = float(value)
            except ValueError:
                pass
        if value is not None and isinstance(value, int) and self.accepts_int:
            value = float(value)
        if value is not None and not isinstance(value, float):
            raise TypeError(instance, self.name, float, value)
        if self.min_value is not None:
            assert value >= self.min_value
        if self.max_value is not None:
            assert value <= self.max_value
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[float] = None,
                 accepts_string: bool = False,
                 accepts_int: bool = True,
                 min_value: Optional[float] = None, max_value: Optional[float] = None):
        super(FloatField, self).__init__(field_type=FieldType.FLOAT,
                                         serialized_name=serialized_name,
                                         null=null,
                                         default_value=default_value)
        self.accepts_string = accepts_string
        self.accepts_int = accepts_int
        assert default_value is None or isinstance(default_value, float)
        assert min_value is None or isinstance(min_value, float)
        assert max_value is None or isinstance(max_value, float)
        if min_value is not None and max_value is not None:
            assert min_value <= max_value
        self.min_value = min_value
        self.max_value = max_value


class BooleanField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str) and value in ['True', 'False', 'true',
                                                                      'false'] and self.accepts_string:
            if value in ['True', 'true']:
                value = True
            elif value in ['False', 'false']:
                value = False
        if value is not None and not isinstance(value, bool):
            raise TypeError(instance, self.name, bool, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[float] = None,
                 accepts_string: bool = False,
                 ):
        super(BooleanField, self).__init__(field_type=FieldType.BOOLEAN,
                                           serialized_name=serialized_name,
                                           null=null,
                                           default_value=default_value)
        self.accepts_string = accepts_string
        assert default_value is None or isinstance(default_value, bool)


class StringField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, str) and self.accepts_non_string:
            value = str(value)
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[str] = None,
                 accepts_non_string: bool = False,
                 ):
        super(StringField, self).__init__(field_type=FieldType.STRING,
                                          serialized_name=serialized_name,
                                          null=null,
                                          default_value=default_value)
        self.accepts_non_string = accepts_non_string
        assert default_value is None or isinstance(default_value, str)


class BytesField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, bytes):
            raise TypeError(instance, self.name, bytes, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[bytes] = None):
        super(BytesField, self).__init__(field_type=FieldType.BYTES,
                                         serialized_name=serialized_name,
                                         null=null,
                                         default_value=default_value
                                         )
        assert default_value is None or isinstance(default_value, bytes)


class ByteArrayField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, bytearray):
            raise TypeError(instance, self.name, bytearray, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[bytearray] = None):
        super(ByteArrayField, self).__init__(field_type=FieldType.BYTE_ARRAY,
                                             serialized_name=serialized_name,
                                             null=null,
                                             default_value=default_value)
        assert default_value is None or isinstance(default_value, bytearray)


# noinspection DuplicatedCode
class MultipleChoiceStringField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in options ' + str(self.options))
        super().__set__(instance, value, test)

    def __init__(self, options: Union[List[str], Set[str]],
                 serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[str] = None
                 ):
        super(MultipleChoiceStringField, self).__init__(field_type=FieldType.STRING,
                                                        serialized_name=serialized_name,
                                                        default_value=default_value,
                                                        null=null)
        if options is None:
            raise Exception("Null options passed for multiple choice string field")
        if not (isinstance(options, list) or isinstance(options, set)):
            raise Exception(
                "Invalid type for options passed for multiple choice string field, must be either set or list but "
                "found " + str(type(options)))
        if len(options) == 0:
            raise Exception("Empty options passed for enum string field")
        for option in options:
            if not isinstance(option, str):
                raise Exception("Invalid value in options of multiple choice string field, " + str(
                    option) + ', expected str value but found ' + str(type(option)))
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of multiple choice string field")
        self.options = set(options)
        assert default_value is None or (isinstance(default_value, str) and default_value in self.options)


# noinspection DuplicatedCode
class EnumStringField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and value in self.enum_options:
            if not isinstance(value, str):
                value = value.value
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in enum values ' + str(self.options))
        super().__set__(instance, value, test)

    def __init__(self, enum, serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[str] = None):
        super(EnumStringField, self).__init__(field_type=FieldType.STRING,
                                              serialized_name=serialized_name,
                                              null=null,
                                              default_value=default_value)
        if enum is None:
            raise Exception("Null enum passed for enum string field")
        if not issubclass(enum, Enum):
            raise Exception("Passed enum class must be a subclass of Enum")
        options = [e.value for e in enum]
        if len(options) == 0:
            raise Exception("Enum with no values for enum string field")
        for option in options:
            if not isinstance(option, str):
                raise Exception(
                    "Invalid value in enum string field, " + str(option) + ', expected str value but found ' + str(
                        type(option)))
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of enum string field")
        self.enum_options = [e for e in enum]
        self.options = set(options)
        assert default_value is None or (isinstance(default_value, str) and default_value in self.options)


# noinspection DuplicatedCode
class MultipleChoiceIntegerField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in options ' + str(self.options))
        super().__set__(instance, value, test)

    def __init__(self, options: Union[List[int], Set[int]], serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[int] = None):
        super(MultipleChoiceIntegerField, self).__init__(field_type=FieldType.INTEGER,
                                                         serialized_name=serialized_name,
                                                         null=null,
                                                         default_value=default_value)
        if options is None:
            raise Exception("Null options passed for multiple choice integer field")
        if not (isinstance(options, list) or isinstance(options, set)):
            raise Exception(
                "Invalid type for options passed for multiple choice integer field, must be either set or list but "
                "found " + str(type(options)))
        if len(options) == 0:
            raise Exception("Empty options passed for multiple choice integer field")
        for option in options:
            if not isinstance(option, int):
                raise Exception("Invalid value in options of multiple choice integer field, " + str(
                    option) + ', expected int value but found ' + str(type(option)))
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of multiple choice integer field")
        self.options = set(options)
        assert default_value is None or (isinstance(default_value, int) and default_value in self.options)


class EnumIntegerField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and value in self.enum_options:
            if not isinstance(value, int):
                value = value.value
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in enum values ' + str(self.options))
        super().__set__(instance, value, test)

    def __init__(self, enum, serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[int] = None):
        super(EnumIntegerField, self).__init__(field_type=FieldType.INTEGER,
                                               serialized_name=serialized_name,
                                               null=null,
                                               default_value=default_value)
        if enum is None:
            raise Exception("Null enum passed for enum string field")
        if not issubclass(enum, Enum):
            raise Exception("Passed enum class must be a subclass of Enum")
        options = [e.value for e in enum]
        if len(options) == 0:
            raise Exception("Enum with no values passed for enum integer field")
        for option in options:
            if not isinstance(option, int):
                raise Exception(
                    "Invalid value in enum integer field, " + str(option) + ', expected int value but found ' + str(
                        type(option)))
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of enum integer field")
        self.enum_options = [e for e in enum]
        self.options = set(options)
        assert default_value is None or (isinstance(default_value, int) and default_value in self.options)


# noinspection DuplicatedCode
class DateField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return datetime.date.strftime(value, self.date_format)

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str):
            try:
                value = datetime.datetime.strptime(value, self.date_format).date()
            except ValueError:
                raise Exception('Error parsing date ' + str(value) + ' with given format ' + str(self.date_format))
        if value is not None and not isinstance(value, datetime.date):
            raise TypeError(instance, self.name, datetime.date, value)
        super().__set__(instance, value, test)

    def __init__(self, date_format: str = '%Y-%m-%d', serialized_name: Optional[str] = None,
                 null: bool = True, default_value: Optional[datetime.date] = None):
        super(DateField, self).__init__(field_type=FieldType.DATE,
                                        serialized_name=serialized_name,
                                        null=null,
                                        default_value=default_value)
        self.date_format = date_format
        assert default_value is None or isinstance(default_value, datetime.date)


class TimeField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return datetime.time.strftime(value, self.time_format)

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str):
            try:
                value = datetime.datetime.strptime(value, self.time_format).time()
            except ValueError:
                raise Exception('Error parsing time ' + str(value) + ' with given format ' + str(self.time_format))
        if value is not None and not isinstance(value, datetime.time):
            raise TypeError(instance, self.name, datetime.time, value)
        super().__set__(instance, value, test)

    def __init__(self, time_format: str = '%H:%M:%S', serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[datetime.time] = None):
        super(TimeField, self).__init__(field_type=FieldType.TIME,
                                        serialized_name=serialized_name,
                                        null=null,
                                        default_value=default_value)
        self.time_format = time_format
        assert default_value is None or isinstance(default_value, datetime.time)


class DateTimeField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return datetime.datetime.strftime(value, self.datetime_format)

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str):
            if self.datetime_format:
                try:
                    dt = datetime.datetime.strptime(value, self.datetime_format)
                except ValueError:
                    raise Exception(
                        'Error parsing date ' + str(value) + ' with given format ' + str(self.datetime_format))
            else:
                dt = parser.parse(value)
            value = pytz.timezone(self.datetime_timezone).localize(dt) if dt.tzinfo is None or dt.tzinfo.utcoffset(
                dt) is None else dt
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(instance, self.name, datetime.datetime, value)
        super().__set__(instance, value, test)

    def __init__(self, datetime_format: Optional[str] = '%Y-%m-%d %H:%M:%S',
                 datetime_timezone: str = 'UTC',
                 serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[datetime.datetime] = None):
        super(DateTimeField, self).__init__(field_type=FieldType.DATETIME,
                                            serialized_name=serialized_name,
                                            null=null,
                                            default_value=default_value)
        self.datetime_format = datetime_format
        self.datetime_timezone = datetime_timezone
        assert default_value is None or isinstance(default_value, datetime.datetime)


class JDateField(Field):
    def get_json_formatted_value(self, value):
        return jdatetime.date.strftime(value, self.date_format)

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str):
            try:
                value = jdatetime.datetime.strptime(value, self.date_format).date()
            except Exception as ex:
                raise Exception('Error parsing date ' + str(value) + ' with given format ' +
                                str(self.date_format) + ', error: ' + str(ex))
        if value is not None and not isinstance(value, jdatetime.date):
            raise TypeError(instance, self.name, jdatetime.date, value)
        super().__set__(instance, value)

    def __init__(self, date_format: str = '%Y-%m-%d', serialized_name: Optional[str] = None, null: bool = True):
        super(JDateField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)
        self.date_format = date_format


class JDateTimeField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return jdatetime.datetime.strftime(value, self.datetime_format)

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str):
            try:
                dt = jdatetime.datetime.strptime(value, self.datetime_format)
            except ValueError:
                raise Exception(
                    'Error parsing date ' + str(value) + ' with given format ' + str(self.datetime_format))
            value = pytz.timezone(self.datetime_timezone).localize(dt) \
                if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None else dt
        if value is not None and not isinstance(value, jdatetime.datetime):
            raise TypeError(instance, self.name, jdatetime.datetime, value)
        super().__set__(instance, value, test)

    def __init__(self,
                 datetime_format: str = '%Y-%m-%d %H:%M:%S',
                 datetime_timezone: str = 'UTC',
                 serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[datetime.datetime] = None):
        super(JDateTimeField, self).__init__(field_type=FieldType.STRING,
                                             serialized_name=serialized_name,
                                             null=null,
                                             default_value=default_value)
        self.datetime_format = datetime_format
        self.datetime_timezone = datetime_timezone
        assert default_value is None or isinstance(default_value, jdatetime.datetime)


class TimestampSecondsField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return int(value.replace(tzinfo=pytz.timezone(self.datetime_timezone)).timestamp())

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, int):
            try:
                value = pytz.timezone(self.datetime_timezone).localize(datetime.datetime.fromtimestamp(float(value)))
            except Exception:
                raise Exception('Error parsing timestamp (in seconds) ' + str(value))
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(instance, self.name, datetime.datetime, value)
        super().__set__(instance, value, test)

    def __init__(self, datetime_timezone: str = 'UTC', serialized_name: Optional[str] = None, null: bool = True,
                 default_value: Optional[datetime.datetime] = None):
        super(TimestampSecondsField, self).__init__(field_type=FieldType.DATETIME,
                                                    serialized_name=serialized_name,
                                                    null=null,
                                                    default_value=default_value)
        self.datetime_timezone = datetime_timezone
        assert default_value is None or isinstance(default_value, datetime.datetime)


class TimestampMillisecondsField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return int(value.replace(tzinfo=pytz.timezone(self.datetime_timezone)).timestamp() * 1000.0)

    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, int):
            try:
                value = pytz.timezone(self.datetime_timezone).localize(
                    datetime.datetime.fromtimestamp(float(value / 1000.0)))
            except Exception:
                raise Exception('Error parsing timestamp (in milliseconds) ' + str(value))
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(instance, self.name, datetime.datetime, value)
        super().__set__(instance, value, test)

    def __init__(self,
                 datetime_timezone: str = 'UTC',
                 serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[datetime.datetime] = None):
        super(TimestampMillisecondsField, self).__init__(field_type=FieldType.DATETIME,
                                                         serialized_name=serialized_name,
                                                         null=null,
                                                         default_value=default_value)
        self.datetime_timezone = datetime_timezone
        assert default_value is None or isinstance(default_value, datetime.datetime)


class DecimalField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str) and self.accepts_string:
            value = decimal.Decimal(value)
        if value is not None and not isinstance(value, decimal.Decimal):
            raise TypeError(instance, self.name, decimal.Decimal, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[decimal.Decimal] = None,
                 accepts_string: bool = False,
                 ):
        super(DecimalField, self).__init__(field_type=FieldType.STRING,
                                           serialized_name=serialized_name,
                                           null=null,
                                           default_value=default_value)
        self.accepts_string = accepts_string
        assert default_value is None or isinstance(default_value, str)


class UUIDField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and isinstance(value, str):
            try:
                value = uuid.UUID(value, version=self.version)
            except ValueError:
                raise Exception(f'Provided string value {value} is not a valid UUID of chosen version {self.version}')
        if value is not None and not isinstance(value, uuid.UUID):
            raise TypeError(instance, self.name, uuid.UUID, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None,
                 null: bool = True,
                 default_value: Optional[uuid.UUID] = None,
                 accepts_string: bool = False,
                 version: int = 4,
                 ):
        super(UUIDField, self).__init__(field_type=FieldType.STRING,
                                        serialized_name=serialized_name,
                                        null=null,
                                        default_value=default_value)
        self.accepts_string = accepts_string
        self.version = version
        assert default_value is None or isinstance(default_value, str)


class JsonField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, dict):
            raise TypeError(instance, self.name, dict, value)
        super().__set__(instance, value, test)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(JsonField, self).__init__(field_type=FieldType.DICT, serialized_name=serialized_name, null=null)


class FunctionField(Field):
    def __get__(self, instance, owner):
        if instance is None:
            raise Exception('Cannot access field without instance')
        func = getattr(instance, self.function_name)
        return func()

    def __set__(self, instance, value, test: bool = False):
        raise Exception(f'Function field is not settable. trying to set function {self.function_name} '
                        f'of class {type(instance)} to value {value}')

    def __init__(self, function_name, serialized_name: Optional[str] = None, null: bool = True):
        self.function_name = function_name
        super(FunctionField, self).__init__(field_type=FieldType.FUNCTION, serialized_name=serialized_name, null=null)


F = TypeVar('F', bound=Field)


# noinspection PyProtectedMember
class ListField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, list):
            raise TypeError(instance, self.name, list, value)
        if value is None:
            value = []
        values = []
        for item in value:
            assert item is not None, "Null item passed to ListField"
            if isinstance(self.item_type, Field):
                inst = JsonObject()
                inst._data = {}
                self.tmp = copy.deepcopy(self.item_type)
                self.tmp.serialized_name = 'tmp'
                self.tmp.__set__(instance=inst, value=item)
                del self.tmp
                values.append(inst._data['tmp'])
            else:
                assert isinstance(item, self.item_type), "ListField items must be of " + str(self.item_type) + \
                                                         ", found " + str(type(item))
                values.append(item)
        super().__set__(instance, values, test)

    def __init__(self, item_type: Union[Type, Field], serialized_name: Optional[str] = None, null: bool = True):
        super(ListField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        valid_types = [int, str, bool, float]
        if not isinstance(item_type, Field):
            assert item_type in valid_types, 'Invalid list item type ' + str(item_type) + 'must be in ' + str(
                valid_types)
        else:
            assert item_type.serialized_name is None, 'List item type should not have serialized name'
        self.item_type = item_type


class JsonObjectMeta(type):

    @staticmethod
    def __get_class_hierarchy_field_names(cls) -> List[str]:
        tmp_class_dict = cls.__dict__
        model_field_names = [k for k in tmp_class_dict.keys() if
                             (isinstance(tmp_class_dict.get(k), JsonSerializable))]  # type: List[str]
        for base in cls.__bases__:
            if issubclass(base, JsonSerializable):
                model_field_names.extend(JsonObjectMeta.__get_class_hierarchy_field_names(base))
        return model_field_names

    # noinspection DuplicatedCode
    @staticmethod
    def __get_fields(cls) -> List[Field]:
        fields_list = []
        type_dicts = cls.__dict__  # type(self).__dict__
        for n, field in type_dicts.items():
            if isinstance(field, Field):
                fields_list.append(field)
        for base in cls.__bases__:
            base_type_dicts = base.__dict__  # type(self).__dict__
            for n, field in base_type_dicts.items():
                if isinstance(field, Field):
                    fields_list.append(field)
        return fields_list

    @staticmethod
    def __get_fields_mapped_by_names(cls) -> Dict[str, Field]:
        result_dict = {}
        fields_list = JsonObjectMeta.__get_fields(cls)
        for field_item in fields_list:
            result_dict[field_item.name] = field_item
        return result_dict

    def __new__(mcs, name, bases, attrs: Dict[str, Any]):
        m_module = attrs.pop('__module__')
        new_attrs = {'__module__': m_module}
        class_cell = attrs.pop('__classcell__', None)
        if class_cell is not None:
            new_attrs['__classcell__'] = class_cell

        new_class = super(JsonObjectMeta, mcs).__new__(mcs, name, bases, new_attrs)

        # attr_meta = attrs.pop('Meta', None)
        # if not attr_meta:
        #     meta = getattr(new_class, 'Meta', None)
        # else:
        #     meta = attr_meta

        serialized_names = []
        for field_name, field in attrs.items():
            if isinstance(field, JsonSerializable):
                if isinstance(field, Field):
                    if field.serialized_name is None:
                        field.serialized_name = field_name
                    if field.serialized_name in serialized_names:
                        raise Exception(
                            'Duplicate serialized names \'' + str(field.serialized_name) + '\' found in ' + str(
                                name) + ' class')
                    serialized_names.append(field.serialized_name)
                    field.name = field_name
                    setattr(new_class, field.name, field)
                else:
                    if field_name in serialized_names:
                        raise Exception(
                            'Duplicate serialized names \'' + str(field_name) + '\' found in ' + str(name) + ' class')
                    serialized_names.append(field_name)
                    field.serialized_name = field_name
                    setattr(new_class, field_name, field)
            else:
                setattr(new_class, field_name, field)

        user_defined_init = new_class.__init__

        # noinspection PyUnusedLocal
        def my_custom_init(instance_self, accept_unknown: bool = False, extra_attributes: Optional[List[str]] = None,
                           *init_args, **init_kwargs):
            instance_self._data = {}  # dict.fromkeys(attrs.keys())
            _setattr = setattr

            _setattr(instance_self, 'serialized_name', None)

            model_field_names = JsonObjectMeta.__get_class_hierarchy_field_names(instance_self.__class__)
            model_fields_by_name = JsonObjectMeta.__get_fields_mapped_by_names(instance_self.__class__)

            # print(model_fields_by_name)

            for field_key in model_field_names:
                if field_key not in init_kwargs.keys():
                    if field_key in model_fields_by_name.keys():
                        if isinstance(model_fields_by_name[field_key], FunctionField):
                            continue
                        _setattr(instance_self, field_key, model_fields_by_name[field_key].default_value)
                    else:
                        _setattr(instance_self, field_key, None)

            # if extra_attributes is not None:
            #     print(extra_attributes)
            #     init_kwargs.update(extra_attributes)

            for key, value in init_kwargs.items():
                if key in model_field_names:
                    if isinstance(model_fields_by_name[key], FunctionField):
                        raise Exception(f'Cannot set value of a FunctionField, field name: {key}, value {value}')
                    _setattr(instance_self, key, value)
                elif extra_attributes is not None and key in extra_attributes:
                    _setattr(instance_self, key, value)
                elif not accept_unknown:
                    raise Exception("value given in instance initialization but was not defined in model class (" + str(
                        type(instance_self)) + ")as Field. key:" + str(key) +
                                    " val:" + str(value) + " type(value):" + str(type(value)))

                # if user_defined_init != JsonObject.__init__:
                #     user_defined_init(instance_self)

        # if the user has not defined the default init, or the name is JsonObject, override the init
        if user_defined_init == object.__init__ or name == "JsonObject":
            new_class.__init__ = my_custom_init
        return new_class


class JsonObject(six.with_metaclass(JsonObjectMeta, JsonSerializable)):
    # noinspection PyUnusedLocal
    def __init__(self, accept_unknown: bool = False, extra_attributes: Optional[List[str]] = None, *args, **kwargs):
        # Empty init will be replaced by meta class
        super(JsonObject, self).__init__()


T = TypeVar('T', bound=JsonObject)


class ObjectField(Field):
    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, self.item_type):
            raise TypeError(instance, self.name, self.item_type, value)
        super().__set__(instance, value, test)

    def __init__(self, item_type: Type[T], serialized_name: Optional[str] = None, null: bool = True):
        super(ObjectField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        self.item_type = item_type


class ObjectListField(Field, List[T], Generic[T]):
    def __len__(self) -> int:
        raise Exception("Must use len on instance value not on field")

    def __set__(self, instance, value, test: bool = False):
        if value is not None and not isinstance(value, list):
            raise TypeError(instance, self.name, list, value)
        if value is None and self.null is False:
            raise Exception(f'Null value passed for not nullable ObjectListField \'{self.name}\' in class '
                            f'{type(instance)}')
        for item in value:
            assert item is not None, "Null item passed to ObjectListField"
            assert isinstance(item, self.item_type), "ObjectListField items must be of " + str(
                self.item_type) + ", found " + str(type(item))
        super(ObjectListField, self).__set__(instance, value, test)

    def __init__(self, item_type: Type[T], serialized_name: Optional[str] = None, null: bool = True):
        super(ObjectListField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        self.item_type = item_type


class TypeHierarchyAdapter:
    def __init__(self,
                 base_class: Type[T],
                 type_key: str,
                 subtype_key_values: Dict[str, Type[T]],
                 accept_sub_type: bool = False):
        self.base_class = base_class
        self.type_key = type_key
        self.accept_sub_type = accept_sub_type
        self.subtype_key_values = subtype_key_values


# noinspection DuplicatedCode
class Pykson:
    @staticmethod
    def __get_fields_mapped_by_names(cls) -> Dict[str, Field]:
        result_dict = {}
        fields_list = Pykson.__get_fields(cls)
        for field_item in fields_list:
            result_dict[field_item.name] = field_item
        return result_dict

    @staticmethod
    def __get_fields_mapped_by_serialized_names(cls) -> Dict[str, Field]:
        result_dict = {}
        fields_list = Pykson.__get_fields(cls)
        for field_item in fields_list:
            if field_item.serialized_name is not None:
                result_dict[field_item.serialized_name] = field_item
            else:
                result_dict[field_item.name] = field_item
        return result_dict

    @staticmethod
    def __get_children_mapped_by_serialized_names(cls) -> Dict[str, JsonObject]:
        result_dict = {}
        child_list = Pykson.__get_child_objects(cls)
        for child in child_list:
            result_dict[child.serialized_name] = child
        return result_dict

    @staticmethod
    def __get_field_names_mapped_by_serialized_names(cls) -> Dict[str, str]:
        result_dict = {}
        fields_list = Pykson.__get_fields(cls)
        for field_item in fields_list:
            if field_item.serialized_name is not None:
                result_dict[field_item.serialized_name] = field_item.name
        return result_dict

    @staticmethod
    def __get_fields(cls) -> List[Field]:
        fields_list = []
        type_dicts = cls.__dict__  # type(self).__dict__
        for n, field in type_dicts.items():
            if isinstance(field, Field):
                fields_list.append(field)
        for base in cls.__bases__:
            base_type_dicts = base.__dict__  # type(self).__dict__
            for n, field in base_type_dicts.items():
                if isinstance(field, Field):
                    fields_list.append(field)
        return fields_list

    # @staticmethod
    # def get_field_names(cls: Type[T]) -> List[str]:
    #     fields_nams = []
    #     type_dicts = cls.__dict__  # type(self).__dict__
    #     for n, field in type_dicts.items():
    #         if isinstance(field, Field):
    #             fields_nams.append(field.serialized_name)
    #     return fields_nams

    @staticmethod
    def __get_child_objects(cls) -> List[JsonObject]:
        child_list = []
        type_dicts = cls.__dict__  # type(self).__dict__
        for n, child in type_dicts.items():
            if isinstance(child, JsonObject):
                child_list.append(child)
        for base in cls.__bases__:
            base_type_dicts = base.__dict__  # type(self).__dict__
            for n, child in base_type_dicts.items():
                if isinstance(child, JsonObject):
                    child_list.append(child)
        return child_list

    @staticmethod
    def __get_json_object_bases(cls_type: type, include_type: bool = False) -> List[type]:
        list_items: List[type] = []
        if include_type and issubclass(cls_type, JsonObject) and cls_type != JsonObject:
            list_items.append(
                cls_type
            )
        for base in cls_type.__bases__:
            if issubclass(base, JsonObject) and base != JsonObject:
                list_items.append(base)
                for base_2 in base.__bases__:
                    list_items.extend(
                        Pykson.__get_json_object_bases(base_2, include_type=True)
                    )
        return list_items

    @staticmethod
    def __get_field_and_child_values_as_dict(json_object, serialized_keys_based: bool) -> Dict[str, Any]:
        fields_dict = {}
        type_dicts = type(json_object).__dict__
        for n, field in type_dicts.items():
            if isinstance(field, Field):
                field_name = field.name
                field_serialized_name = field.serialized_name
                field_value = json_object.__getattribute__(field_name)
                fields_dict[field_serialized_name if serialized_keys_based else field_name] = \
                    field.get_json_formatted_value(field_value)
            elif isinstance(field, JsonObject):
                field_name = n
                field_serialized_name = n
                field_value = json_object.__getattribute__(field_name)
                fields_dict[field_serialized_name if serialized_keys_based else field_name] = field_value

        bases_list: List[type] = Pykson.__get_json_object_bases(cls_type=type(json_object))
        # for base in type(json_object).__bases__:
        #     if issubclass(base, JsonObject):
        #         print('base json object')
        #         print(base)

        # for base in type(json_object).__bases__:
        for base in bases_list:
            type_dicts = base.__dict__
            for n, field in type_dicts.items():
                if isinstance(field, Field):
                    field_name = field.name
                    field_serialized_name = field.serialized_name
                    field_value = json_object.__getattribute__(field_name)
                    fields_dict[field_serialized_name] = field.get_json_formatted_value(field_value)
                elif isinstance(field, JsonObject):
                    field_name = n
                    field_serialized_name = n
                    field_value = json_object.__getattribute__(field_name)
                    fields_dict[field_serialized_name] = field_value

        return fields_dict

    def __init__(self):
        self.type_hierarchy_adapters = []  # type: List[TypeHierarchyAdapter]

    def register_type_hierarchy_adapter(self, type_hierarchy_adapter: TypeHierarchyAdapter):
        self.type_hierarchy_adapters.append(type_hierarchy_adapter)

    # noinspection PyCallingNonCallable
    def _from_json_dict(self, data: Dict, cls: Type[T], accept_unknown: bool = False) -> T:
        sub_type = cls
        extra_attributes = []  # type: List[str]

        for type_hierarchy_adapter in self.type_hierarchy_adapters:
            # if type_hierarchy_adapter.base_class == cls:
            if (type_hierarchy_adapter.accept_sub_type is True and issubclass(cls, type_hierarchy_adapter.base_class)) \
                    or type_hierarchy_adapter.base_class == cls:
                subtype_key = data.get(type_hierarchy_adapter.type_key, None)
                if subtype_key is None:
                    raise Exception('No sub-type key provided in class of type ' + str(cls) + ' for type key ' + str(
                        type_hierarchy_adapter.type_key))
                sub_type = type_hierarchy_adapter.subtype_key_values.get(subtype_key, None)
                if sub_type is None:
                    raise Exception('No sub-type provided in type hierarchy adapter for base class of ' + str(
                        cls) + ' for sub-type key ' + str(subtype_key))
                extra_attributes.append(type_hierarchy_adapter.type_key)

        children_mapped_by_serialized_names = Pykson.__get_children_mapped_by_serialized_names(sub_type)
        fields_mapped_by_serialized_names = Pykson.__get_fields_mapped_by_serialized_names(sub_type)
        field_names_mapped_by_serialized_names = Pykson.__get_field_names_mapped_by_serialized_names(sub_type)
        data_copy = {}
        for data_key, data_value in data.items():
            if isinstance(data_value, list) and (data_key in fields_mapped_by_serialized_names.keys()) and \
                    isinstance(fields_mapped_by_serialized_names[data_key], ObjectListField):
                data_list_value = []
                for data_value_item in data_value:
                    # noinspection PyUnresolvedReferences
                    data_list_value.append(
                        self.from_json(data_value_item, fields_mapped_by_serialized_names[data_key].item_type,
                                       accept_unknown=accept_unknown)
                    )
                data_copy[field_names_mapped_by_serialized_names[data_key]] = data_list_value
            # elif isinstance(data_value, list) and (data_key in fields_mapped_by_serialized_names.keys()) and \
            #         isinstance(fields_mapped_by_serialized_names[data_key], ListField) and \
            #         isinstance(fields_mapped_by_serialized_names[data_key].item_type, Field):
            #     if fields_mapped_by_serialized_names[data_key].item_type:
            #         if data_key in field_names_mapped_by_serialized_names.keys():
            #             data_copy[field_names_mapped_by_serialized_names[data_key]] = data_value
            #         else:
            #             data_copy[data_key] = data_value
            elif data_key in children_mapped_by_serialized_names.keys() and isinstance(data_value, dict):
                data_copy[data_key] = self.from_json(data_value, type(children_mapped_by_serialized_names[data_key]),
                                                     accept_unknown=accept_unknown)
            elif data_key in fields_mapped_by_serialized_names.keys() and isinstance(
                    fields_mapped_by_serialized_names[data_key], ObjectField):
                # noinspection PyUnresolvedReferences
                data_copy[field_names_mapped_by_serialized_names[data_key]] = \
                    self.from_json(data_value,
                                   fields_mapped_by_serialized_names[data_key].item_type,
                                   accept_unknown=accept_unknown)
            else:
                if data_key in field_names_mapped_by_serialized_names.keys():
                    data_copy[field_names_mapped_by_serialized_names[data_key]] = data_value
                else:
                    data_copy[data_key] = data_value
        return sub_type(accept_unknown=accept_unknown, extra_attributes=extra_attributes, **data_copy)

    # noinspection PyCallingNonCallable
    def _from_json_list(self, data: List, cls: Type[T], accept_unknown: bool = False) -> List[T]:
        list_result = []  # type: List[T]
        for data_value_item in data:
            # noinspection PyUnresolvedReferences
            list_result.append(self.from_json(data_value_item, cls, accept_unknown))
        return list_result

    def from_csv(self, data: str, cls: Type[T], line_separator: str = '\n', first_row_as_field_names: bool = True,
                 accept_unknown: bool = False) -> List[T]:
        data_items = data.split(line_separator)
        if first_row_as_field_names:
            reader_list = csv.DictReader(data_items)
        else:
            field_names = Pykson.__get_fields_mapped_by_serialized_names(cls=cls).keys()
            reader_list = csv.DictReader(data_items, fieldnames=field_names)
        rows = [r for r in reader_list]
        return self._from_json_list(rows, cls=cls, accept_unknown=accept_unknown)

    def from_json(self, data: Union[str, Dict, List], cls: Type[T], accept_unknown: bool = False
                  ) -> Optional[Union[T, List[T]]]:
        if isinstance(data, str):
            data = json.loads(data)
        if isinstance(data, dict):
            return self._from_json_dict(data, cls, accept_unknown)
        elif isinstance(data, list):
            return self._from_json_list(data, cls, accept_unknown)
        elif isinstance(data, type(None)):
            return None
        else:
            raise Exception('Unable to parse data of type ' + str(type(data)))

    # def __item_to_dict(self, item: T) -> Dict[str, Any]:
    #     fields_dict = Pykson.__get_field_and_child_values_as_dict(item)
    #     final_dict = {}
    #     for field_key, field_value in fields_dict.items():
    #         if isinstance(field_value, JsonObject):
    #             final_dict[field_key] = self._to_json(field_value)
    #         elif isinstance(field_value, list):
    #             list_value = []
    #             for sub_item in field_value:
    #                 if isinstance(sub_item, JsonObject):
    #                     list_value.append(self._to_json(sub_item))
    #                 else:
    #                     list_value.append(sub_item)
    #             final_dict[field_key] = list_value
    #         elif isinstance(field_value, dict):
    #             final_dict[field_key] = field_value
    #         else:
    #             final_dict[field_key] = field_value
    #     return final_dict

    def _to_json(self, item: Union[T, List[T]], serialized_keys_based: bool = True) -> \
            Union[Dict[str, Any], List[Dict[str, Any]]]:
        if isinstance(item, list):
            final_list = []
            for i in item:
                final_list.append(self._to_json(i))
            return final_list
        else:
            fields_dict = Pykson.__get_field_and_child_values_as_dict(item, serialized_keys_based)
            final_dict = {}
            # check if item type exists in type hierarchy adapters
            for type_hierarchy_adapter in self.type_hierarchy_adapters:
                if isinstance(item, type_hierarchy_adapter.base_class):
                    # find type from dictionary
                    type_found = False
                    for subtype_key, subtype_class in type_hierarchy_adapter.subtype_key_values.items():
                        if isinstance(item, subtype_class):
                            type_found = True
                            final_dict[type_hierarchy_adapter.type_key] = subtype_key
                            break
                    if not type_found:
                        raise Exception('No sub-type key was entered for item of type ' + str(
                            type(item)) + ' in type hierarchy of base type ' +
                                        str(type_hierarchy_adapter.base_class))

            for field_key, field_value in fields_dict.items():
                if isinstance(field_value, JsonObject):
                    final_dict[field_key] = self._to_json(field_value)
                elif isinstance(field_value, list):
                    list_value = []
                    for val in field_value:
                        if isinstance(val, JsonObject):
                            list_value.append(self._to_json(val))
                        else:
                            list_value.append(val)
                    final_dict[field_key] = list_value
                elif isinstance(field_value, dict):
                    final_dict[field_key] = field_value
                else:
                    final_dict[field_key] = field_value
            return final_dict

    def to_json(self, item: Union[T, List[T]]) -> str:
        return json.dumps(self._to_json(item))

    def to_dict_or_list(self, item: Union[T, List[T]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        return self._to_json(item)
