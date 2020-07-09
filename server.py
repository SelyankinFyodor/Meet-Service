import ast
from datetime import datetime
from peewee import *

from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)
db = SqliteDatabase('meeting.db')
cursor = db.cursor()


class BaseModel(Model):
    class Meta:
        database = db


class Meeting(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    date = DateTimeField()

    class Meta:
        table_name = "Meeting"


class Person(BaseModel):
    id = PrimaryKeyField()
    meeting = ForeignKeyField(Meeting, related_name='participants')
    name = CharField()
    email = CharField()

    class Meta:
        table_name = "Person"


Meeting.create_table()
Person.create_table()


def add_meeting(name, date):
    new_meeting = Meeting(name=name, date=date)
    new_meeting.save()
    return new_meeting.id


def remove_meeting(meeting_id):
    try:
        m = Meeting.get(Meeting.id == meeting_id)
        for person in m.participants:
            person.delete_instance()
        m.delete_instance()
        return "SUCCESS"

    except:
        return "not such meeting id in the base"


def add_participant(meeting_id, person_name, person_mail):
    try:
        m = Meeting.get(Meeting.id == meeting_id)
        new_participants = Person(meeting=m, name=person_name, email=person_mail)
        new_participants.save()
        return "SUCCESS"

    except:
        return "not such meeting id in the base"


def remove_participant(meeting_id, person_id):
    try:
        m = Meeting.get(Meeting.id == meeting_id)
        for person in m.participants:
            if person.id == person_id:
                person.delete_instance()
                return "SUCCESS"
        return "not such participant id"
    except:
        return "not such meeting id"


def all_meeting():
    data = []
    for meet in Meeting.select():
        el = {
            "id": meet.id,
            "name": meet.name,
            "date": str(meet.date),
            "participants": [{"id": person.id, "name": person.name, "email": person.email} for person in meet.participants]
        }
        data.append(el)
    return data


class Server(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("action")
        parser.add_argument("data")
        params = parser.parse_args()

        if params["action"] == "add_meet":
            data = ast.literal_eval(params["data"])
            meet_id = add_meeting(data["name"], datetime.strptime(data["date"], "%d/%m/%Y %H:%M"))
            return meet_id, 201

        elif params["action"] == "rem_meet":
            data = ast.literal_eval(params["data"])
            result = remove_meeting(data["meet_id"])
            return result, 200

        elif params["action"] == "add_part":
            data = ast.literal_eval(params["data"])
            result = add_participant(meeting_id=data["meet_id"],
                                     person_name=data["name"],
                                     person_mail=data["mail"])
            return result, 200

        elif params["action"] == "rem_part":
            data = ast.literal_eval(params["data"])
            result = remove_participant(meeting_id=data["meet_id"],
                                        person_id=data["user_id"])
            return result, 200

        elif params["action"] == "show":
            data = all_meeting()
            if data is []:
                return "no meeting", 200
            else:
                return data, 200


api.add_resource(Server, "/")

if __name__ == '__main__':
    app.run()