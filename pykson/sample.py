from pykson import JsonObject, Pykson, IntegerField, StringField, ObjectListField


class Score(JsonObject):
    score = IntegerField()
    course = StringField()

    def __str__(self):
        return str(self.course) + ": " + str(self.score)


class Student(JsonObject):

    first_name = StringField(serialized_name="fn")
    last_name = StringField()
    age = IntegerField()
    # scores = ListField(int)
    scores = ObjectListField(Score)

    def __str__(self):
        return "first name:" + str(self.first_name) + ", last name: " + str(self.last_name) + ", age: " + str(self.age) + ", score: " + str(self.scores)


print(JsonObject.get_fields(Student))


# json_text = '{"fn":"ali", "last_name":"soltani", "age": 25, "scores": [ 20, 19]}'
json_text = '{"fn":"ali", "last_name":"soltani", "age": 25, "scores": [ {"course": "algebra", "score": 20}, {"course": "statistics", "score": 19} ]}'
item = Pykson.from_json(json_text, Student)

print(item)
print(type(item))

print(Pykson.to_json(item))