import json
import os
from datetime import datetime

DB_FILE = "talkbang_data.json"
USERS_FILE = "users_data.json"

def load_data():
    """데이터베이스에서 모든 다톡방 정보를 불러오기"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_users():
    """사용자 정보 불러오기"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    """데이터베이스에 다톡방 정보 저장"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_users(users):
    """사용자 정보 저장"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def register_user(user_id, password):
    """새로운 사용자 등록"""
    users = load_users()

    if user_id in users:
        return False, "이미 존재하는 아이디입니다."

    users[user_id] = {
        "password": password,
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True, "회원가입이 완료되었습니다."

def login_user(user_id, password):
    """사용자 로그인 확인"""
    users = load_users()

    if user_id not in users:
        return False, "존재하지 않는 아이디입니다."

    if users[user_id]["password"] != password:
        return False, "비밀번호가 틀렸습니다."

    return True, "로그인되었습니다."

def create_room(room_name, password):
    """새로운 다톡방 생성"""
    data = load_data()

    if room_name in data:
        return False, "이미 존재하는 다톡방입니다."

    data[room_name] = {
        "password": password,
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    save_data(data)
    return True, "다톡방이 생성되었습니다."

def join_room(room_name, password):
    """다톡방 참가 확인"""
    data = load_data()

    if room_name not in data:
        return False, "존재하지 않는 다톡방입니다."

    if data[room_name]["password"] != password:
        return False, "비밀번호가 틀렸습니다."

    return True, "다톡방에 입장했습니다."

def get_room_messages(room_name):
    """해당 다톡방의 모든 메시지 불러오기"""
    data = load_data()
    if room_name in data:
        return data[room_name]["messages"]
    return []

def add_message(room_name, sender, message):
    """다톡방에 메시지 추가"""
    data = load_data()

    if room_name not in data:
        return False

    data[room_name]["messages"].append({
        "sender": sender,
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    save_data(data)
    return True

def get_all_rooms():
    """모든 다톡방 이름 가져오기"""
    data = load_data()
    return list(data.keys())

def add_game_score(room_name, user_id, score):
    """게임 점수 추가"""
    data = load_data()

    if room_name not in data:
        return False

    if "game_scores" not in data[room_name]:
        data[room_name]["game_scores"] = []

    data[room_name]["game_scores"].append({
        "user_id": user_id,
        "score": score,
        "timestamp": datetime.now().isoformat()
    })
    save_data(data)
    return True

def get_room_game_scores(room_name):
    """해당 다톡방의 게임 점수 가져오기"""
    data = load_data()
    if room_name in data and "game_scores" in data[room_name]:
        return data[room_name]["game_scores"]
    return []
