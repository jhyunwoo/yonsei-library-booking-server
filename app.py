from typing import TypedDict, List
from flask import Flask, request, jsonify

from bookRoom import book_room

app = Flask(__name__)


class Participant(TypedDict):
    id: str
    phone: str

@app.route('/')
def hello_world():  # put application's code here
    return 'Server is running'


@app.route('/api/booking', methods=['POST'])
def booking():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    # 받은 데이터 처리 (예: name 값을 추출)
    student_id = data.get('student_id')
    password = data.get('password')

    start_time = data.get('start_time')
    duration = data.get('duration')

    library = data.get('library')
    room = data.get('room')
    room_number = data.get('roomNumber')

    participants:List[Participant] = data.get('participants')

    print(participants[0]['id'])

    print(student_id, password, start_time, duration, library, room, room_number, participants)
    result = book_room(student_id, password, start_time, duration, library, room, room_number, participants)
    return result

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=3000, debug=True)
