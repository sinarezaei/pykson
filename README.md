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
There are different types of predefined fields: `IntegerField`, `FloatField`, `BooleanField`, `StringField`, `ListField`, `ObjectField`, `ObjectListField`, `DateField`, `TimeField`, `DateTimeField`, `TimestampSecondsField` and `TimestampMillisecondsField`.

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

### Work with dates and datetimes
Pykson currenty has five fields for handling `date`s and `datetime`s.
Three of them, `DateField`, `TimeField` and `DateTimeField`, use date/time formats to serialize/deserialize values. The other ones, `TimestampSecondsField` and `TimestampMillisecondsField` use integer values to serialize/deserialize datetimes.


### Accept unknown key/value pairs when deserializing
`from_json` method currently has an input parameter named `accept_unknown` with default value of `false`. If you want to deserialize an string to a `JsonObject` and ignore unknown keys which are not defined in your model class as fields, you can set this parameter to `true`. If this parameter is false, an error is raised when facing an unknown key in the json.

```
json_text = '{"fn":"John", "ln":"Smith", "a": 25, "up":"some unknown parameter", "s": {"s": 100, "c":"Algebra"}}'
student = Pykson.from_json(json_text, Student, accept_unknown=True)
```

[pypi_version]: https://img.shields.io/pypi/v/pykson.svg "PYPI version"
[licence_version]: https://img.shields.io/badge/license-MIT%20v2-brightgreen.svg "MIT Licence"
