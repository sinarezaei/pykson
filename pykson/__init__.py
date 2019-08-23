from enum import Enum
from typing import Dict, Any, List, Optional, TypeVar, Union, Type, Set, Sized, Generic
import six
import pytz
import json
import datetime

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


class Field(JsonSerializable):
    # noinspection PyMethodMayBeStatic
    def get_json_formatted_value(self, value):
        return value

    # noinspection PyProtectedMember
    def __get__(self, instance, owner):
        if instance is None:
            raise Exception('Cannot access field without instance')
        return instance._data.get(self.serialized_name, None)

    # noinspection PyProtectedMember
    def __set__(self, instance, value):
        if not self.null:
            assert value is not None, "Null value passed for not nullable field \'" + self.name + "\' in class " + str(type(instance))
        if instance is None:
            raise Exception('Cannot access field without instance')
        instance._data[self.serialized_name] = value

    def __init__(self, field_type: FieldType, serialized_name: Optional[str] = None, null: bool = True):
        self.field_type = field_type
        self.serialized_name = serialized_name  # field name in serialized json
        self.name = None  # field name in the defined class
        self.null = null


class IntegerField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(IntegerField, self).__init__(field_type=FieldType.INTEGER, serialized_name=serialized_name, null=null)


class FloatField(Field):
    def __set__(self, instance, value):
        if value is not None and isinstance(value, int):
            value = float(value)
        if value is not None and not isinstance(value, float):
            raise TypeError(instance, self.name, float, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(FloatField, self).__init__(field_type=FieldType.FLOAT, serialized_name=serialized_name, null=null)


class BooleanField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, bool):
            raise TypeError(instance, self.name, bool, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(BooleanField, self).__init__(field_type=FieldType.BOOLEAN, serialized_name=serialized_name, null=null)


class StringField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(StringField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)


class MultipleChoiceStringField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in options ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, options: Union[List[str], Set[str]], serialized_name: Optional[str] = None, null: bool = True):
        super(MultipleChoiceStringField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)
        if options is None:
            raise Exception("Null options passed for multiple choice string field")
        if not (isinstance(options, list) or isinstance(options, set)):
            raise Exception("Invalid type for options passed for multiple choice string field, must be either set or list but found " + str(type(options)))
        if len(options) == 0:
            raise Exception("Empty options passed for enum string field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of multiple choice string field")
        for option in options:
            if not isinstance(option, str):
                raise Exception("Invalid value in options of multiple choice string field, " + str(option) + ', expected str value but found ' + str(type(option)))
        self.options = set(options)


class EnumStringField(Field):
    def __set__(self, instance, value):
        if value is not None and value in self.enum_options:
            value = value.value
        if value is not None and not isinstance(value, str):
            raise TypeError(instance, self.name, str, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in enum values ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, enum, serialized_name: Optional[str] = None, null: bool = True):
        super(EnumStringField, self).__init__(field_type=FieldType.STRING, serialized_name=serialized_name, null=null)
        if enum is None:
            raise Exception("Null enum passed for enum string field")
        if not issubclass(enum, Enum):
            raise Exception("Passed enum class must be a subclass of Enum")
        options = [e.value for e in enum]
        if len(options) == 0:
            raise Exception("Enum with no values for enum string field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of enum string field")
        for option in options:
            if not isinstance(option, str):
                raise Exception("Invalid value in enum string field, " + str(option) + ', expected str value but found ' + str(type(option)))
        self.enum_options = [e for e in enum]
        self.options = set(options)


class MultipleChoiceIntegerField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in options ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, options: Union[List[int], Set[int]], serialized_name: Optional[str] = None, null: bool = True):
        super(MultipleChoiceIntegerField, self).__init__(field_type=FieldType.INTEGER, serialized_name=serialized_name, null=null)
        if options is None:
            raise Exception("Null options passed for multiple choice integer field")
        if not (isinstance(options, list) or isinstance(options, set)):
            raise Exception("Invalid type for options passed for multiple choice integer field, must be either set or list but found " + str(type(options)))
        if len(options) == 0:
            raise Exception("Empty options passed for multiple choice integer field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of multiple choice integer field")
        for option in options:
            if not isinstance(option, int):
                raise Exception("Invalid value in options of multiple choice integer field, " + str(option) + ', expected int value but found ' + str(type(option)))
        self.options = set(options)


class EnumIntegerField(Field):
    def __set__(self, instance, value):
        if value is not None and value in self.enum_options:
            value = value.value
        if value is not None and not isinstance(value, int):
            raise TypeError(instance, self.name, int, value)
        if value is not None and not (value in self.options):
            raise ValueError('Invalid value ' + str(value) + ' not present in enum values ' + str(self.options))
        super().__set__(instance, value)

    def __init__(self, enum, serialized_name: Optional[str] = None, null: bool = True):
        super(EnumIntegerField, self).__init__(field_type=FieldType.INTEGER, serialized_name=serialized_name, null=null)
        if enum is None:
            raise Exception("Null enum passed for enum string field")
        if not issubclass(enum, Enum):
            raise Exception("Passed enum class must be a subclass of Enum")
        options = [e.value for e in enum]
        if len(options) == 0:
            raise Exception("Enum with no values passed for enum integer field")
        if len(options) != len(set(options)):
            raise Exception("Duplicate values passed for options of enum integer field")
        for option in options:
            if not isinstance(option, int):
                raise Exception("Invalid value in enum integer field, " + str(option) + ', expected int value but found ' + str(type(option)))
        self.enum_options = [e for e in enum]
        self.options = set(options)


class DateField(Field):
    def get_json_formatted_value(self, value):
        return datetime.date.strftime(value, self.date_format)

    def __set__(self, instance, value):
        if value is not None and isinstance(value, str):
            try:
                value = datetime.datetime.strptime(value, self.date_format).date()
            except:
                raise Exception('Error parsing date ' + str(value) + ' with given format ' + str(self.date_format))
        if value is not None and not isinstance(value, datetime.date):
            raise TypeError(instance, self.name, datetime.date, value)
        super().__set__(instance, value)

    def __init__(self, date_format: str = '%Y-%m-%d', serialized_name: Optional[str] = None, null: bool = True):
        super(DateField, self).__init__(field_type=FieldType.DATE, serialized_name=serialized_name, null=null)
        self.date_format = date_format


class TimeField(Field):
    def get_json_formatted_value(self, value):
        return datetime.time.strftime(value, self.time_format)

    def __set__(self, instance, value):
        if value is not None and isinstance(value, str):
            try:
                value = datetime.datetime.strptime(value, self.time_format).time()
            except:
                raise Exception('Error parsing time ' + str(value) + ' with given format ' + str(self.time_format))
        if value is not None and not isinstance(value, datetime.time):
            raise TypeError(instance, self.name, datetime.time, value)
        super().__set__(instance, value)

    def __init__(self, time_format: str = '%H:%M:%S', serialized_name: Optional[str] = None, null: bool = True):
        super(TimeField, self).__init__(field_type=FieldType.TIME, serialized_name=serialized_name, null=null)
        self.time_format = time_format


class DateTimeField(Field):
    def get_json_formatted_value(self, value):
        if value is None:
            return None
        return datetime.datetime.strftime(value, self.datetime_format)

    def __set__(self, instance, value):
        if value is not None and isinstance(value, str):
            try:
                value = pytz.timezone(self.datetime_timezone).localize(datetime.datetime.strptime(value, self.datetime_format))
            except:
                raise Exception('Error parsing date ' + str(value) + ' with given format ' + str(self.datetime_format))
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(instance, self.name, datetime.datetime, value)
        super().__set__(instance, value)

    def __init__(self, datetime_format: str = '%Y-%m-%d %H:%M:%S', datetime_timezone: str = 'UTC', serialized_name: Optional[str] = None, null: bool = True):
        super(DateTimeField, self).__init__(field_type=FieldType.DATETIME, serialized_name=serialized_name, null=null)
        self.datetime_format = datetime_format
        self.datetime_timezone = datetime_timezone


class TimestampSecondsField(Field):
    def get_json_formatted_value(self, value):
        return int(value.replace(tzinfo=pytz.timezone(self.datetime_timezone)).timestamp())

    def __set__(self, instance, value):
        if value is not None and isinstance(value, int):
            try:
                value = pytz.timezone(self.datetime_timezone).localize(datetime.datetime.fromtimestamp(float(value)))
            except:
                raise Exception('Error parsing timestamp (in seconds) ' + str(value))
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(instance, self.name, datetime.datetime, value)
        super().__set__(instance, value)

    def __init__(self, datetime_timezone: str = 'UTC', serialized_name: Optional[str] = None, null: bool = True):
        super(TimestampSecondsField, self).__init__(field_type=FieldType.DATETIME, serialized_name=serialized_name, null=null)
        self.datetime_timezone = datetime_timezone


class TimestampMillisecondsField(Field):
    def get_json_formatted_value(self, value):
        return int(value.replace(tzinfo=pytz.timezone(self.datetime_timezone)).timestamp() * 1000.0)

    def __set__(self, instance, value):
        if value is not None and isinstance(value, int):
            try:
                value = pytz.timezone(self.datetime_timezone).localize(datetime.datetime.fromtimestamp(float(value / 1000.0)))
            except:
                raise Exception('Error parsing timestamp (in milliseconds) ' + str(value))
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(instance, self.name, datetime.datetime, value)
        super().__set__(instance, value)

    def __init__(self, datetime_timezone: str = 'UTC', serialized_name: Optional[str] = None, null: bool = True):
        super(TimestampMillisecondsField, self).__init__(field_type=FieldType.DATETIME, serialized_name=serialized_name, null=null)
        self.datetime_timezone = datetime_timezone


class JsonField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, dict):
            raise TypeError(instance, self.name, dict, value)
        super().__set__(instance, value)

    def __init__(self, serialized_name: Optional[str] = None, null: bool = True):
        super(JsonField, self).__init__(field_type=FieldType.DICT, serialized_name=serialized_name, null=null)


F = TypeVar('F', bound=Field)


class ListField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, list):
            raise TypeError(instance, self.name, list, value)
        if value is None:
            value = []
        for item in value:
            assert item is not None, "Null item passed to ListField"
            assert isinstance(item, self.item_type), "ListField items must be of " + str(self.item_type) + ", found " + str(type(item))
        super().__set__(instance, value)

    def __init__(self, item_type: Type, serialized_name: Optional[str] = None, null: bool = True):
        super(ListField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        valid_types = [int, str, bool, float]
        assert item_type in valid_types, 'Invalid list item type ' + str(item_type) + 'must be in ' + str(valid_types)
        self.item_type = item_type


class JsonObjectMeta(type):
    @staticmethod
    def __get_class_hierarchy_field_names(cls) -> List[str]:
        tmp_class_dict = cls.__dict__
        model_field_names = [k for k in tmp_class_dict.keys() if (isinstance(tmp_class_dict.get(k), JsonSerializable))]  # type: List[str]
        for base in cls.__bases__:
            if issubclass(base, JsonSerializable):
                model_field_names.extend(JsonObjectMeta.__get_class_hierarchy_field_names(base))
        return model_field_names

    def __new__(cls, name, bases, attrs: Dict[str, Any]):
        m_module = attrs.pop('__module__')
        new_attrs = {'__module__': m_module}
        class_cell = attrs.pop('__classcell__', None)
        if class_cell is not None:
            new_attrs['__classcell__'] = class_cell

        new_class = super(JsonObjectMeta, cls).__new__(cls, name, bases, new_attrs)

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
                        raise Exception('Duplicate serialized names \'' + str(field.serialized_name) + '\' found in ' + str(name) + ' class')
                    serialized_names.append(field.serialized_name)
                    field.name = field_name
                    setattr(new_class, field.name, field)
                else:
                    if field_name in serialized_names:
                        raise Exception('Duplicate serialized names \'' + str(field_name) + '\' found in ' + str(name) + ' class')
                    serialized_names.append(field_name)
                    field.serialized_name = field_name
                    setattr(new_class, field_name, field)
            else:
                setattr(new_class, field_name, field)

        # noinspection PyUnusedLocal
        def my_custom_init(instance_self, accept_unknown: bool = False, extra_attributes: Optional[List[str]] = None, *init_args, **init_kwargs):
            instance_self._data = {}  # dict.fromkeys(attrs.keys())
            _setattr = setattr

            _setattr(instance_self, 'serialized_name', None)

            model_field_names = JsonObjectMeta.__get_class_hierarchy_field_names(instance_self.__class__)

            for field_key in model_field_names:
                if field_key not in init_kwargs.keys():
                    _setattr(instance_self, field_key, None)

            for key, value in init_kwargs.items():
                if key in model_field_names:
                    _setattr(instance_self, key, value)
                elif extra_attributes is not None and key in extra_attributes:
                    _setattr(instance_self, key, value)
                elif not accept_unknown:
                    raise Exception("value given in instance initialization but was not defined in model as Field. key:" + str(key) +
                                    " val:" + str(value) + " type(value):" + str(type(value)))

        new_class.__init__ = my_custom_init
        return new_class


class JsonObject(six.with_metaclass(JsonObjectMeta, JsonSerializable)):
    # noinspection PyUnusedLocal
    def __init__(self, accept_unknown: bool = False, extra_attributes: Optional[List[str]] = None, *args, **kwargs):
        # Empty init will be replaced by meta class
        super(JsonObject, self).__init__()


T = TypeVar('T', bound=JsonObject)


class ObjectField(Field):
    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.item_type):
            raise TypeError(instance, self.name, self.item_type, value)
        super().__set__(instance, value)

    def __init__(self, item_type: Type[T], serialized_name: Optional[str] = None, null: bool = True):
        super(ObjectField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        self.item_type = item_type


class ObjectListField(Field, List[T], Generic[T]):

    def __len__(self) -> int:
        raise Exception("Must use len on instance value not on field")

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, list):
            raise TypeError(instance, self.name, list, value)
        if value is None:
            value = []
        for item in value:
            assert item is not None, "Null item passed to ObjectListField"
            assert isinstance(item, self.item_type), "ObjectListField items must be of " + str(self.item_type) + ", found " + str(type(item))
        super(ObjectListField, self).__set__(instance, value)

    def __init__(self, item_type: Type[T], serialized_name: Optional[str] = None, null: bool = True):
        super(ObjectListField, self).__init__(field_type=FieldType.LIST, serialized_name=serialized_name, null=null)
        self.item_type = item_type


class TypeHierarchyAdapter:

    def __init__(self,
                 base_class: Type[T],
                 type_key: str,
                 subtype_key_values: Dict[str, Type[T]]):
        self.base_class = base_class
        self.type_key = type_key
        self.subtype_key_values = subtype_key_values


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
    def __get_field_and_child_values_as_dict(json_object) -> Dict[str, Any]:
        fields_dict = {}
        type_dicts = type(json_object).__dict__
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
        for base in type(json_object).__bases__:
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
            if type_hierarchy_adapter.base_class == cls:
                subtype_key = data.get(type_hierarchy_adapter.type_key, None)
                if subtype_key is None:
                    raise Exception('No sub-type key provided in class of type ' + str(cls) + ' for type key ' + str(type_hierarchy_adapter.type_key))
                sub_type = type_hierarchy_adapter.subtype_key_values.get(subtype_key, None)
                if sub_type is None:
                    raise Exception('No sub-type provided in type hierarchy adapter for base class of ' + str(cls) + ' for sub-type key ' + str(subtype_key))
                extra_attributes.append(type_hierarchy_adapter.type_key)

        children_mapped_by_serialized_names = Pykson.__get_children_mapped_by_serialized_names(sub_type)
        fields_mapped_by_serialized_names = Pykson.__get_fields_mapped_by_serialized_names(sub_type)
        field_names_mapped_by_serialized_names = Pykson.__get_field_names_mapped_by_serialized_names(sub_type)
        data_copy = {}
        for data_key, data_value in data.items():
            if isinstance(data_value, list) and (data_key in fields_mapped_by_serialized_names.keys()) and isinstance(fields_mapped_by_serialized_names[data_key],
                                                                                                                      ObjectListField):
                data_list_value = []
                for data_value_item in data_value:
                    # noinspection PyUnresolvedReferences
                    data_list_value.append(
                        self.from_json(data_value_item, fields_mapped_by_serialized_names[data_key].item_type, accept_unknown=accept_unknown)
                    )
                data_copy[field_names_mapped_by_serialized_names[data_key]] = data_list_value
            elif data_key in children_mapped_by_serialized_names.keys() and isinstance(data_value, dict):
                data_copy[data_key] = self.from_json(data_value, type(children_mapped_by_serialized_names[data_key]), accept_unknown=accept_unknown)
            elif data_key in fields_mapped_by_serialized_names.keys() and isinstance(fields_mapped_by_serialized_names[data_key], ObjectField):
                # noinspection PyUnresolvedReferences
                data_copy[field_names_mapped_by_serialized_names[data_key]] = self.from_json(data_value, fields_mapped_by_serialized_names[data_key].item_type,
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

    def from_json(self, data: Union[str, Dict, List], cls: Type[T], accept_unknown: bool = False) -> Optional[Union[T, List[T]]]:
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

    def _to_json(self, item: Union[T, List[T]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if isinstance(item, list):
            final_list = []
            for i in item:
                final_list.append(self._to_json(i))
            return final_list
        else:
            fields_dict = Pykson.__get_field_and_child_values_as_dict(item)
            final_dict = {}
            # check if item type exists in type hierarchi adapters
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
                        raise Exception('No sub-type key was entered for item of type ' + str(type(item)) + ' in type hierarchy of base type ' +
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
