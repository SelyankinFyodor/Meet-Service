import urllib.request
import json
from datetime import datetime
from re import *


def post_msg(msg):
    req = urllib.request.Request('http://127.0.0.1:5000/', method="POST")
    req.add_header('Content-Type', 'application/json')

    response = urllib.request.urlopen(req, json.dumps(msg).encode("utf-8"))
    return json.load(response)


def pretty_print(meetings):
    if not meetings:
        print("no meetings")
        return
    for meet in meetings:
        print("\n" + str(meet["id"]) + ") " + meet["name"])
        print(meet["date"])
        print("participants")
        for p in meet["participants"]:
            print("     id: " + str(p["id"]))
            print("         name: " + p["name"])
            print("         email: " + p["email"])


def create_meeting(name, date):
    try:
        valid_date = datetime.strptime(date, "%d/%m/%Y %H:%M")
        msg = {
            "action": "add_meet",
            "data": {
                "name": name,
                "date": valid_date.strftime("%d/%m/%Y %H:%M")
            }
        }
        return "create meeting with id " + post_msg(msg)

    except ValueError:
        return 'Invalid date'


def cancel_meeting(meet_id):
    try:
        valid_id = int(meet_id)
        msg = {
            "action": "rem_meet",
            "data": {
                "meet_id": valid_id
            }
        }

        return post_msg(msg)

    except ValueError:
        return "could not convert id to number"


def add_participant(meet_id, name, email):
    pattern = compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    if not pattern.match(email):
        return "incorrect email address"
    try:
        valid_id = int(meet_id)
        msg = {
            "action": "add_part",
            "data": {
                "meet_id": valid_id,
                "name": name,
                "mail": email
            }
        }

        return post_msg(msg)

    except ValueError:
        return "could not convert id to number"


def remove_participant(meet_id, user_id):
    try:
        valid_id = int(meet_id)
        valid_user_id = int(user_id)
        msg = {
            "action": "rem_part",
            "data": {
                "meet_id": valid_id,
                "user_id": valid_user_id,
            }
        }

        return post_msg(msg)

    except ValueError:
        return 'could not convert id to number'


def all_meetings():
    msg = {
        "action": "show",
        "data": {}
    }
    return post_msg(msg)


def show_help():
    print("0) show help")
    print("1) add meeting")
    print("2) cancel meeting")
    print("3) add participant to meeting")
    print("4) remove participant from meeting")
    print("5) show all meetings")
    print("6) quit")


def main():
    show_help()
    while True:
        command = input()
        if command == "0":
            show_help()

        elif command == "1":
            print("input meeting name")
            name = input()
            print("input meeting date in format d/m/Y H:M")
            date = input()

            result = create_meeting(name, date)

            print(result)

        elif command == "2":
            print("input meeting id")
            meet_id = input()

            result = cancel_meeting(meet_id)

            print(result)

        elif command == "3":
            print("input meeting id")
            meet_id = input()
            print("input user name")
            name = input()
            print("input user email")
            email = input()

            result = add_participant(meet_id, name, email)

            print(result)

        elif command == "4":
            print("input meeting id")
            meet_id = input()
            print("input user id")
            user_id = input()
            result = remove_participant(meet_id, user_id)
            print(result)

        elif command == "5":
            result = all_meetings()
            pretty_print(result)

        elif command == "6":
            break


if __name__ == "__main__":
    main()
