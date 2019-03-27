![alt text][pypi_version] ![alt text][licence_version]

# Pykson: A JSON Serializer/Deserializer for Python

Pykson is a JSON serializer/deserializer in python.

Tested with:
* Python 3.6+

Use the following command to install using pip:
```
pip install pykson
```

## Usage example
### Create Object Models
First, create your object model which extends `JsonObject`
```python
from pykson import JsonObject, IntegerField, StringField, ObjectListField


class Course(JsonObject):
    name = StringField()
    teacher = StringField()


class Score(JsonObject):
    score = IntegerField()
    course = Course()


class Student(JsonObject):

    first_name = StringField()
    last_name = StringField()
    age = IntegerField()
    scores = ObjectListField(Score)

```

### Deserialize json strings
Use `Pykson` class to deserialize json string to `JsonObject`s
```python
from pykson import Pykson

json_text = '{"first_name":"John", "last_name":"Smith", "age": 25, "scores": [ {"course": {"name": "Algebra", "teacher" :"Mr. Schmidt"}, "score": 100}, {"course": {"name": "Statistics", "teacher": "Mrs. Lee"}, "score": 90} ]}'
student = Pykson.from_json(json_text, Student)
```

### Serialize objects
Use `Pykson` class to serialize `JsonObject`s to string
```python
Pykson.to_json(student)
```
## Fields
It's possible to use `IntegerField`, `FloatField`, `BooleanField`, `StringField`, `ListField` and `ObjectListField`.
There are four other types of fields which help with storing fields with specific integer or string values. To create a field with multiple choice integer values, use `MultipleChoiceIntegerField` or `EnumIntegerField` classes. To create a field with multiple choice string values, use `MultipleChoiceStringField` or `EnumStringField` classes.

Example for `MultipleChoiceStringField`:
```python
from pykson import MultipleChoiceStringField

class WeatherInfo(JsonObject):

  condition = MultipleChoiceStringField(options=['sunny','cloudy','rainy'], null=False)

```

Example for `EnumStringField`:
```python
from enum import Enum
from pykson import EnumStringField

class WeatherCondition(Enum):
  SUNNY = 'sunny'
  CLOUDY = 'cloudy'
  RAINY = 'rainy'


class WeatherInfo(JsonObject):
  condition = EnumStringField(enum=WeatherCondition, null=False)

```



## Advanced usage

### Serialized names
It is possible to use change name of fields during serialization/deserialization. For this purpose, use `serialized_name` input in the fields
```python
from pykson import Pykson, JsonObject, IntegerField, StringField, ObjectField
class Score(JsonObject):
    score = IntegerField(serialized_name="s")
    course = StringField(serialized_name="c")


class Student(JsonObject):

    first_name = StringField(serialized_name="fn")
    last_name = StringField(serialized_name="ln")
    age = IntegerField(serialized_name="a")
    score = ObjectField(Score, serialized_name="s")


json_text = '{"fn":"John", "ln":"Smith", "a": 25, "s": {"s": 100, "c":"Algebra"}}'
student = Pykson.from_json(json_text, Student)
```

[pypi_version]: https://img.shields.io/pypi/v/pykson.svg "PYPI version"
[licence_version]: https://img.shields.io/badge/license-MIT%20v2-brightgreen.svg "MIT Licence"
