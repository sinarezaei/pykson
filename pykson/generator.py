import re
import _io
import json
from dateutil import parser
from typing import List, Optional, Tuple, Dict, Set, Any


class PyksonGenerator:
    _initial_letter_replacements = {
        '0': 'zero',
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine.',
        '.': 'dot',
        ':': 'colon',
        ';': 'semicolon',
        '"': 'quote',
        '#': 'sharp',
        '%': 'percent',
        '!': 'danger',
        '?': 'question',
        '&': 'and',
        '*': 'star',
    }
    _reserved_words = [
        'from', 'class', 'for', 'if', 'in', 'def', 'return', 'break', 'continue', 'pass', 'id', 'else', 'elif',
        'object',
    ]

    class ValidationError(Exception):
        pass

    @staticmethod
    def _null_or_equal_type_strings(a: str, b: str):
        return a == 'NoneType' or b == 'NoneType' or a == b

    @staticmethod
    def _null_or_equal(a: str, b: str):
        return a is None or b is None or a == b

    class SchemaProperty:
        def __init__(
                self,
                name: str,
                type_str: str,
                item_type_str: Optional[str] = None,
                nullable: bool = False,
                values: Optional[Set[Any]] = None
        ):
            self.name = name
            self.type_str = type_str
            self.item_type_str = item_type_str
            self.nullable = nullable
            self.values = values

        def json_repr(self):
            js = {'name': self.name, 'type': self.type_str, 'null': self.nullable}
            if self.item_type_str:
                js['item_type'] = self.item_type_str
            if self.values:
                js['values'] = list([str(v) for v in self.values])
            return js

        def __str__(self):
            json_obj = self.json_repr()
            return json.dumps(json_obj, indent=2)

    class Schema:
        def __init__(
                self,
                name: str,
                properties: List['PyksonGenerator.SchemaProperty'],
        ):
            self.name = name
            self.properties = properties

        def json_repr(self):
            return {'name': self.name, 'properties': [p.json_repr() for p in self.properties]}

        def __str__(self):
            json_obj = self.json_repr()
            return json.dumps(json_obj, indent=2)

        def get_properties_by_name(self) -> Dict[str, 'PyksonGenerator.SchemaProperty']:
            return {
                p.name: p for p in self.properties
            }

        def is_similar(self, other_schema: 'PyksonGenerator.Schema'):
            prop_by_name = self.get_properties_by_name()
            other_prop_by_name = other_schema.get_properties_by_name()
            return prop_by_name.keys() == other_prop_by_name.keys() and all([
                PyksonGenerator._null_or_equal_type_strings(prop_by_name[n].type_str, other_prop_by_name[n].type_str)
                and
                (
                    True if prop_by_name[n].type_str != list.__name__
                    else PyksonGenerator._null_or_equal(
                        prop_by_name[n].item_type_str, other_prop_by_name[n].item_type_str
                    )
                )
                for n in prop_by_name.keys()
            ])

        def update_from(self, other_schema: 'PyksonGenerator.Schema'):
            assert self.is_similar(other_schema), 'Cannot update from non-similar schema'
            properties = self.properties
            other_props = other_schema.get_properties_by_name()
            for prop in properties:
                other_prop: PyksonGenerator.SchemaProperty = other_props[prop.name]
                if prop.type_str == 'NoneType' and other_prop.type_str != 'NoneType':
                    prop.type_str = other_prop.type_str
                if prop.type_str == list.__name__ and other_prop.type_str == list.__name__:
                    if prop.item_type_str is None and other_prop.item_type_str is not None:
                        prop.item_type_str = other_prop.item_type_str
                else:
                    if other_prop.values is not None and len(other_prop.values) > 0:
                        if prop.values is None:
                            prop.values = set()
                        prop.values.update(other_prop.values)
            self.properties = properties

    @staticmethod
    def _is_primitive(element) -> bool:
        if any([isinstance(element, cls) for cls in [int, str, float, bool, bytes]]):
            return True
        elif isinstance(element, list):
            list_of_primitives = all([
                any([isinstance(list_item, cls) for cls in [int, str, float, bool, bytes]])
                for list_item in element
            ])
            if list_of_primitives:
                if len(set([type(list_item) for list_item in element])) <= 1:
                    return True
                else:
                    raise Exception(f'List of non-similar items is not supported {element}')
            else:
                return False
        else:
            return False

    @staticmethod
    def _is_list_of_primitives(element) -> bool:
        if not isinstance(element, list):
            return False
        return all([
            any([isinstance(list_item, cls) for cls in [int, str, float, bool, bytes]])
            for list_item in element
        ])

    @staticmethod
    def _is_list_of_similar_items(element) -> bool:
        if not isinstance(element, list):
            return False
        return len(set([type(list_item) for list_item in element])) <= 1

    @staticmethod
    def _add_schema_to_list_if_does_not_exist(
            schema_list: List['PyksonGenerator.Schema'], new_schema: 'PyksonGenerator.Schema'
    ) -> Optional['PyksonGenerator.Schema']:
        found_new_schema: bool = False
        duplicate_schema: Optional[PyksonGenerator.Schema] = None
        for s in schema_list:
            if new_schema.is_similar(s):
                found_new_schema = True
                s.update_from(new_schema)
                duplicate_schema = s
                break
        if found_new_schema is False:
            schema_list.append(new_schema)
        return duplicate_schema

    @staticmethod
    def generate_schema(
            json_object: dict,
            name: str,
            sub_schemas: Optional[List['PyksonGenerator.Schema']] = None
    ) -> Tuple['PyksonGenerator.Schema', List['PyksonGenerator.Schema']]:
        if sub_schemas is None:
            sub_schemas: List[PyksonGenerator.Schema] = []
        properties: List[PyksonGenerator.SchemaProperty] = []
        for key, value in json_object.items():
            if PyksonGenerator._is_primitive(value):
                properties.append(PyksonGenerator.SchemaProperty(
                    name=key, type_str=type(value).__name__, values={value}
                ))
            elif value is None:
                properties.append(
                    PyksonGenerator.SchemaProperty(
                        name=key, type_str=type(value).__name__, nullable=True
                    )
                )
            elif isinstance(value, list):
                pass
                if not PyksonGenerator._is_list_of_similar_items(value):
                    raise PyksonGenerator.ValidationError(
                        f'Cannot generate schema for list of non-similar items {[type(t) for t in value]}'
                    )
                else:
                    if len(value) == 0:
                        properties.append(PyksonGenerator.SchemaProperty(
                            name=key, type_str=list.__name__, item_type_str=type(None).__str__
                        ))
                    elif PyksonGenerator._is_list_of_primitives(value):
                        properties.append(
                            PyksonGenerator.SchemaProperty(
                                name=key, type_str=list.__name__, item_type_str=type(value[0]).__str__
                            )
                        )
                    else:
                        assert all([isinstance(v, dict) for v in value]), f'List with unknown type {type(value[0])} ' \
                                                                          f'found {value}'
                        list_item_name = f'{name}.{key}'
                        value_0_schema, value_0_sub_schemas = PyksonGenerator.generate_schema(
                            value[0], list_item_name, sub_schemas
                        )
                        dup_schema = PyksonGenerator._add_schema_to_list_if_does_not_exist(sub_schemas, value_0_schema)
                        value_0_schema_name = (dup_schema or value_0_schema).name

                        for i in range(1, len(value)):
                            value_i_schema, value_i_sub_schemas = PyksonGenerator.generate_schema(
                                value[i], list_item_name, sub_schemas
                            )
                            if not value_0_schema.is_similar(value_i_schema):
                                raise Exception(f'Non similar list schemas {value_0_schema} AND {value_i_schema} '
                                                f'in list {list_item_name}')
                            else:
                                value_0_schema.update_from(value_i_schema)
                        properties.append(PyksonGenerator.SchemaProperty(
                            name=key, type_str=list.__name__, item_type_str=value_0_schema_name
                        ))

            elif isinstance(value, dict):
                value_schema, value_sub_schemas = PyksonGenerator.generate_schema(value, f'{name}.{key}', sub_schemas)
                duplicate_schema = PyksonGenerator._add_schema_to_list_if_does_not_exist(sub_schemas, value_schema)
                value_schema_name = (duplicate_schema or value_schema).name
                properties.append(PyksonGenerator.SchemaProperty(
                    name=key, type_str=value_schema_name
                ))
            else:
                raise Exception(f"Unsupported value {value} of type {type(value)} in {name}")

        for i in range(0, len(sub_schemas)):
            for j in range(i + 1, len(sub_schemas)):
                if sub_schemas[i].is_similar(sub_schemas[j]):
                    raise Exception(
                        f'Found duplicate schemas in final sub schemas {sub_schemas[i]} AND {sub_schemas[j]}'
                    )
        return PyksonGenerator.Schema(name=name, properties=properties), sub_schemas

    @staticmethod
    def _schema_name_to_class_name(schema_name: str) -> str:
        for i in PyksonGenerator._initial_letter_replacements.keys():
            if schema_name.startswith(i):
                schema_name = PyksonGenerator._initial_letter_replacements[i] + '.' + schema_name[1:]
                break
        components = schema_name.split('.')
        return ''.join(x[0].upper() + x[1:] for x in components)

    @staticmethod
    def _to_snake_case(text: str) -> str:
        text = re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
        for i in PyksonGenerator._initial_letter_replacements.keys():
            if text.startswith(i):
                text = PyksonGenerator._initial_letter_replacements[i] + '_' + text[1:]
                break
        for w in PyksonGenerator._reserved_words:
            if text == w:
                text = text + '_'
                break
        return text

    @staticmethod
    def _is_datetime(value: str):
        if value is None:
            return True
        if len(value) < 8:
            return False
        # noinspection PyBroadException
        try:
            parser.parse(value)
            return True
        except Exception:
            return False

    @staticmethod
    def _are_all_datetime(values: Set[str]) -> bool:
        if values is None:
            return False
        if len(values) == 0:
            return False
        if all([v is None for v in values]):
            return False
        return all([
            PyksonGenerator._is_datetime(v) for v in values
        ])

    @staticmethod
    def write_pykson_class(
            schema: 'PyksonGenerator.Schema',
            file_writer: _io.TextIOWrapper,
            indent: str,
            include_todos: bool
    ):
        file_writer.write(f'class {PyksonGenerator._schema_name_to_class_name(schema.name)}(pykson.JsonObject):\n')
        for p in schema.properties:
            primitive_field_to_pykson_class = {
                int.__name__: 'IntegerField',
                # we exclude string to check for datetimes
                # str.__name__: 'StringField',
                float.__name__: 'FloatField',
                bool.__name__: 'BooleanField',
                bytes.__name__: 'BytesField',
            }
            primitive_field_to_pykson_field_type = {
                int.__name__: int,
                str.__name__: str,
                float.__name__: float,
                bool.__name__: bool,
                bytes.__name__: bytes,
            }
            if p.type_str in primitive_field_to_pykson_class.keys():
                file_writer.write(
                    f'{indent}{PyksonGenerator._to_snake_case(p.name)} = '
                    f'pykson.{primitive_field_to_pykson_class[p.type_str]}'
                    f'(serialized_name="{p.name}", null={p.nullable})'
                )
            elif p.type_str == str.__name__:
                if p.values is not None and len(p.values) > 0 and PyksonGenerator._are_all_datetime(p.values):
                    file_writer.write(
                        f'{indent}{PyksonGenerator._to_snake_case(p.name)} = '
                        f'pykson.DateTimeField(datetime_format=None, serialized_name="{p.name}", null={p.nullable})'
                    )
                else:
                    file_writer.write(
                        f'{indent}{PyksonGenerator._to_snake_case(p.name)} = '
                        f'pykson.StringField(serialized_name="{p.name}", null={p.nullable})'
                    )
            elif p.type_str == 'NoneType':
                if include_todos:
                    file_writer.write(f'{indent}# todo: Fix this line, value was always None!\n')
                # file_writer.write(f'{indent}{_to_snake_case(p.name)} = None')
                file_writer.write(f'{indent}{PyksonGenerator._to_snake_case(p.name)} = pykson.StringField'
                                  f'(serialized_name="{p.name}", null=True)')
            # elif p.type_str == datetime.datetime.__name__:
            #     file_writer.write(f'{indent}{PyksonGenerator._to_snake_case(p.name)} = pykson.StringField'
            #                       f'(serialized_name="{p.name}", null=True)')
            elif p.type_str == list.__name__:
                if p.item_type_str is None:
                    if include_todos:
                        file_writer.write(
                            f'{indent}# todo: Fix this line, list was empty and cannot detect item type!\n')
                    file_writer.write(f'{indent}{PyksonGenerator._to_snake_case(p.name)} = pykson.ListField'
                                      f'(item_type=Any, serialized_name="{p.name}", null={p.nullable})')
                elif p.item_type_str in primitive_field_to_pykson_field_type.keys():
                    file_writer.write(f'{indent}{PyksonGenerator._to_snake_case(p.name)} = pykson.ListField'
                                      f'(item_type={primitive_field_to_pykson_field_type[p.item_type_str]}, '
                                      f'serialized_name="{p.name}", null={p.nullable})')
                else:
                    file_writer.write(f'{indent}{PyksonGenerator._to_snake_case(p.name)} = pykson.ObjectListField'
                                      f'(item_type={PyksonGenerator._schema_name_to_class_name(p.item_type_str)}, '
                                      f'serialized_name="{p.name}", null={p.nullable})')
            else:
                file_writer.write(f'{indent}{PyksonGenerator._to_snake_case(p.name)} = pykson.ObjectField('
                                  f'item_type={PyksonGenerator._schema_name_to_class_name(p.type_str)}, '
                                  f'serialized_name="{p.name}", null={p.nullable})')
            file_writer.write('\n')

    # noinspection PyTypeChecker
    @staticmethod
    def generate_pykson_classes(
            json_object: dict,
            base_name: str,
            indent: str = '    ',
            generate_test: bool = False,
            include_todos: bool = True,
    ):
        schema, sub_schemas = PyksonGenerator.generate_schema(json_object, name=base_name)
        with open(f'pykson_{PyksonGenerator._to_snake_case(base_name)}.generated.py', 'w') as f:
            f.write('import pykson\n')
            f.write('\n\n')
            for s_c in sub_schemas:
                PyksonGenerator.write_pykson_class(s_c, f, indent, include_todos=include_todos)
                f.write('\n')
                f.write('\n')
            PyksonGenerator.write_pykson_class(schema, f, indent, include_todos=include_todos)
            if generate_test is True:
                f.write('\n')
                f.write('\n')
                f.write('if __name__ == "__main__":\n')
                dumped_string = json.dumps(json_object, indent=indent).replace('\n', f'\n{indent}')
                dumped_string = dumped_string.replace(': null\n', ': None\n')
                dumped_string = dumped_string.replace(': false\n', ': False\n')
                dumped_string = dumped_string.replace(': true\n', ': True\n')
                dumped_string = dumped_string.replace(': null,\n', ': None,\n')
                dumped_string = dumped_string.replace(': false,\n', ': False,\n')
                dumped_string = dumped_string.replace(': true,\n', ': True,\n')
                f.write(indent + 'test_json = ' + dumped_string)
                f.write(f'{indent}\n')
                f.write(f'{indent}obj = pykson.Pykson().from_json(test_json, {schema.name})')
                f.write('\n')
