import unittest
from datetime import datetime
from peewee import *


new_db = SqliteDatabase(':memory:')
cursor = new_db.cursor()


class BaseModel(Model):
    class Meta:
        database = new_db


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


class TestFuncs(unittest.TestCase):
    def test_all_meeting(self):
        self.assertEqual(all_meeting(), [])

    def test_add_remove_meeting_1(self):
        self.assertEqual(1, add_meeting("a", "22/10/2020 10:30"))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30", "participants": []}])
        self.assertEqual("SUCCESS", remove_meeting(1))
        self.assertEqual(all_meeting(), [])

    def test_add_remove_meeting_2(self):
        self.assertEqual(1, add_meeting("a", "22/10/2020 10:30"))
        self.assertEqual(2, add_meeting("b", "22/10/2020 10:30"))
        self.assertEqual(all_meeting(), [
            {"id": 1, "name": "a", "date": "22/10/2020 10:30", "participants": []},
            {"id": 2, "name": "b", "date": "22/10/2020 10:30", "participants": []}])
        self.assertEqual("SUCCESS", remove_meeting(1))
        self.assertEqual("SUCCESS", remove_meeting(2))
        self.assertEqual(all_meeting(), [])

    def test_remove_nonexistent_meeting_1(self):
        self.assertEqual("not such meeting id in the base", remove_meeting(1))

    def test_remove_nonexistent_meeting_2(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("not such meeting id in the base", remove_meeting(2))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30", "participants": []}])
        self.assertEqual("SUCCESS", remove_meeting(1))
        self.assertEqual(all_meeting(), [])

    def test_add_participants_to_meet_1(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("not such meeting id in the base", add_participant(2, "Ivan", "email@email.com"))
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

    def test_add_participants_to_meet_2(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("SUCCESS", add_participant(1, "Ivan", "email@email.com"))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30",
                                          "participants": [
                                              {"id": 1, "name": "Ivan", "email": "email@email.com"}
                                          ]}])
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

    def test_add_participants_to_meet_3(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("SUCCESS", add_participant(1, "Ivan", "email@email.com"))
        self.assertEqual("SUCCESS", add_participant(1, "Eve", "mail@email.com"))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30",
                                          "participants": [
                                              {"id": 1, "name": "Ivan", "email": "email@email.com"},
                                              {"id": 2, "name": "Eve", "email": "mail@email.com"}
                                          ]}])
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

    def test_remove_participants_from_meet_1(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("SUCCESS", add_participant(1, "Ivan", "email@email.com"))
        self.assertEqual("SUCCESS", remove_participant(1, 1))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30",
                                          "participants": []}])
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

    def test_remove_participants_from_meet_2(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("SUCCESS", add_participant(1, "Ivan", "email@email.com"))
        self.assertEqual("not such meeting id", remove_participant(2, 1))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30",
                                          "participants": [
                                              {"id": 1, "name": "Ivan", "email": "email@email.com"},
                                          ]}])
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

    def test_remove_participants_from_meet_3(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("SUCCESS", add_participant(1, "Ivan", "email@email.com"))
        self.assertEqual("not such participant id", remove_participant(1, 2))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30",
                                          "participants": [
                                              {"id": 1, "name": "Ivan", "email": "email@email.com"},
                                          ]}])
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

    def test_remove_participants_from_meet_4(self):
        add_meeting("a", "22/10/2020 10:30")
        self.assertEqual("SUCCESS", add_participant(1, "Ivan", "email@email.com"))
        self.assertEqual("SUCCESS", add_participant(1, "Eve", "mail@email.com"))
        self.assertEqual("SUCCESS", remove_participant(1, 1))
        self.assertEqual(all_meeting(), [{"id": 1, "name": "a", "date": "22/10/2020 10:30",
                                          "participants": [
                                              {"id": 2, "name": "Eve", "email": "mail@email.com"},
                                          ]}])
        remove_meeting(1)
        self.assertEqual(all_meeting(), [])

if __name__ == '__main__':
    unittest.main()
    new_db.close()