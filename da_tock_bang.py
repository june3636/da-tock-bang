import streamlit as st
import time
import random
from datetime import datetime
from db_handler import (
    create_room, join_room, get_room_messages,
    add_message, get_all_rooms, register_user, login_user,
    add_game_score, get_room_game_scores
)

st.set_page_config(page_title="다톡방", layout="wide")

# 세션 상태 초기화
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "current_room" not in st.session_state:
    st.session_state.current_room = ""
if "page" not in st.session_state:
    st.session_state.page = "login"
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = 0
if "game_mode" not in st.session_state:
    st.session_state.game_mode = False
if "game_score" not in st.session_state:
    st.session_state.game_score = 0
if "game_time" not in st.session_state:
    st.session_state.game_time = 0
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "game_start_time" not in st.session_state:
    st.session_state.game_start_time = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False

def go_to_lobby():
    """로비로 돌아가기"""
    st.session_state.page = "lobby"
    st.session_state.current_room = ""
    st.rerun()

def logout():
    """로그아웃"""
    st.session_state.user_id = None
    st.session_state.current_user = ""
    st.session_state.current_room = ""
    st.session_state.page = "login"
    st.rerun()

def render_login():
    """로그인/회원가입 페이지"""
    st.title("🎤 다톡방 (Da Tock Bang)")
    st.subheader("이야기를 나누는 곳")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔓 로그인")
        login_id = st.text_input("아이디", placeholder="아이디를 입력하세요", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="login_pw")

        if st.button("로그인", use_container_width=True, type="primary", key="login_btn"):
            if not login_id or not login_pw:
                st.error("아이디와 비밀번호를 입력해주세요.")
            else:
                success, message = login_user(login_id, login_pw)
                if success:
                    st.session_state.user_id = login_id
                    st.session_state.page = "lobby"
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)

    with col2:
        st.subheader("📝 회원가입")
        signup_id = st.text_input("아이디", placeholder="아이디를 입력하세요", key="signup_id")
        signup_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="signup_pw")
        signup_pw_check = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요", key="signup_pw_check")

        if st.button("회원가입", use_container_width=True, type="primary", key="signup_btn"):
            if not signup_id or not signup_pw or not signup_pw_check:
                st.error("모든 항목을 입력해주세요.")
            elif signup_pw != signup_pw_check:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                success, message = register_user(signup_id, signup_pw)
                if success:
                    st.success(message)
                    st.info("로그인해주세요.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(message)

def render_lobby():
    """로비 페이지"""
    st.title("🎤 다톡방 (Da Tock Bang)")
    st.subheader("이야기를 나누는 곳")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("## 📝 다톡방 만들기")
        st.markdown("새로운 다톡방을 생성하세요")
        if st.button("들어가기", use_container_width=True, key="create_btn", help="새 다톡방을 만듭니다"):
            st.session_state.page = "create_room"
            st.rerun()
        for _ in range(3):
            st.write("")

    with col2:
        st.markdown("## 🚪 다톡방 참가")
        st.markdown("기존 다톡방에 참가하세요")
        if st.button("들어가기", use_container_width=True, key="join_btn", help="기존 다톡방에 참가합니다"):
            st.session_state.page = "join_room"
            st.rerun()
        for _ in range(3):
            st.write("")

def render_create_room():
    """다톡방 생성 페이지"""
    st.title("📝 다톡방 만들기")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("← 뒤로가기"):
            go_to_lobby()

    room_name = st.text_input("다톡방 이름을 입력하세요", placeholder="예: 우리반, 친구들 모임")
    password = st.text_input("비밀번호를 입력하세요", type="password", placeholder="4자 이상")

    if st.button("다톡방 만들기", use_container_width=True, type="primary"):
        if not room_name or not password:
            st.error("모든 항목을 입력해주세요.")
        elif len(password) < 4:
            st.error("비밀번호는 4자 이상이어야 합니다.")
        else:
            success, message = create_room(room_name, password)
            if success:
                st.success(message)
                st.session_state.current_room = room_name
                st.session_state.current_user = st.session_state.user_id
                st.session_state.page = "chatroom"
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)

def render_join_room():
    """다톡방 참가 페이지"""
    st.title("🚪 다톡방 참가")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("← 뒤로가기"):
            go_to_lobby()

    room_name = st.text_input("다톡방 이름을 입력하세요", placeholder="예: 우리반")
    password = st.text_input("비밀번호를 입력하세요", type="password", placeholder="비밀번호")

    if st.button("다톡방 참가", use_container_width=True, type="primary"):
        if not room_name or not password:
            st.error("모든 항목을 입력해주세요.")
        else:
            success, message = join_room(room_name, password)
            if success:
                st.success(message)
                st.session_state.current_room = room_name
                st.session_state.current_user = st.session_state.user_id
                st.session_state.page = "chatroom"
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)

def render_minigame():
    """미니게임 페이지"""
    st.title("🧮 수학 퀴즈 게임")
    st.subheader(f"다톡방: {st.session_state.current_room}")

    # 게임 시작 시간 설정
    if st.session_state.game_start_time is None:
        st.session_state.game_start_time = time.time()
        st.session_state.game_score = 0
        st.session_state.question_count = 0
        st.session_state.game_over = False

    # 경과 시간 계산
    elapsed_time = time.time() - st.session_state.game_start_time
    remaining_time = 5 - elapsed_time

    # 상단 고정 정보 표시
    col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])
    with col1:
        st.markdown(f"**점수: {st.session_state.game_score}점** | 문제: {st.session_state.question_count}개")
    with col2:
        if remaining_time > 0:
            st.markdown(f"### ⏰ {remaining_time:.1f}초")
        else:
            st.markdown(f"### ⏰ 0.0초")
    with col3:
        st.write("")
    with col4:
        if st.button("← 종료", use_container_width=True):
            if st.session_state.game_score > 0:
                add_game_score(st.session_state.current_room, st.session_state.user_id, st.session_state.game_score)
            st.session_state.game_mode = False
            st.session_state.game_score = 0
            st.session_state.question_count = 0
            st.session_state.game_start_time = None
            st.session_state.game_over = False
            st.rerun()

    st.divider()

    # 시간이 끝났을 때 게임 종료
    if remaining_time <= 0:
        st.session_state.game_over = True

    if st.session_state.game_over:
        st.success(f"⏰ 게임 종료! 최종 점수: {st.session_state.game_score}점 ({st.session_state.question_count}문제)")
        st.balloons()

        if st.button("점수 저장하고 나가기", use_container_width=True, type="primary"):
            if st.session_state.game_score > 0:
                add_game_score(st.session_state.current_room, st.session_state.user_id, st.session_state.game_score)
            st.session_state.game_mode = False
            st.session_state.game_score = 0
            st.session_state.question_count = 0
            st.session_state.game_start_time = None
            st.session_state.game_over = False
            st.rerun()
    else:
        # 게임 초기화
        if "current_question" not in st.session_state:
            st.session_state.current_question = None
            st.generate_new_question = True

        # 새 문제 생성
        if st.session_state.current_question is None or st.generate_new_question:
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            operation = random.choice(["+", "-", "*"])

            if operation == "+":
                answer = num1 + num2
            elif operation == "-":
                answer = num1 - num2
            else:
                answer = num1 * num2

            st.session_state.current_question = {
                "num1": num1,
                "num2": num2,
                "operation": operation,
                "answer": answer
            }
            st.generate_new_question = False

        question = st.session_state.current_question

        # 진행 상황 표시
        progress_value = elapsed_time / 5
        st.progress(min(progress_value, 1.0))

        st.info(f"### {question['num1']} {question['operation']} {question['num2']} = ?")

        user_answer = st.number_input("답을 입력하세요", step=1, key="answer_input", value=0)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("제출", use_container_width=True, type="primary"):
                if user_answer == question['answer']:
                    st.session_state.game_score += 10
                    st.session_state.question_count += 1
                    st.success(f"✅ 정답! {question['answer']}입니다!")
                    st.balloons()
                    time.sleep(0.5)
                    st.session_state.answer_input = 0
                    st.session_state.current_question = None
                    st.generate_new_question = True
                    st.rerun()
                else:
                    st.error(f"❌ 틀렸습니다! 정답은 {question['answer']}입니다.")
                    st.session_state.answer_input = 0
                    st.rerun()

        with col2:
            if st.button("다음 문제", use_container_width=True):
                st.session_state.answer_input = 0
                st.session_state.current_question = None
                st.generate_new_question = True
                st.rerun()

    st.divider()

    # 게임 기록 표시
    st.subheader("🏆 게임 기록 순위")
    game_scores = get_room_game_scores(st.session_state.current_room)

    if game_scores:
        # 사용자별 최고 점수 계산
        user_scores = {}
        for score_data in game_scores:
            user = score_data["user_id"]
            points = score_data["score"]
            if user not in user_scores:
                user_scores[user] = points
            else:
                user_scores[user] = max(user_scores[user], points)

        # 점수 순으로 정렬
        sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

        # 순위 표시
        for rank, (user, score) in enumerate(sorted_scores, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            st.write(f"{medal} **{user}** - {score}점")
    else:
        st.info("아직 게임 기록이 없습니다. 게임을 시작해보세요!")

def handle_message_submit():
    """메시지 전송 처리"""
    if "msg_input_submit" in st.session_state:
        message_input = st.session_state.msg_input_submit
        if message_input.strip():
            current_time = time.time()
            time_diff = current_time - st.session_state.last_message_time

            if time_diff < 3:
                st.error(f"3초 뒤에 다시 보낼 수 있습니다. ({3 - int(time_diff)}초)")
            else:
                add_message(st.session_state.current_room, st.session_state.current_user, message_input)
                st.session_state.last_message_time = current_time
                st.session_state.msg_input_submit = ""
                st.session_state.auto_refresh += 1
                st.rerun()

def render_chatroom():
    """채팅방 페이지"""
    st.title(f"🎤 {st.session_state.current_room}")

    col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
    with col1:
        st.caption(f"접속자: {st.session_state.current_user} | 계정: {st.session_state.user_id}")
    with col2:
        if st.button("↻ 새로고침", use_container_width=True):
            st.session_state.auto_refresh += 1
            st.rerun()
    with col3:
        if st.button("← 나가기", use_container_width=True):
            go_to_lobby()

    st.divider()

    # 메시지 표시 영역 (자동 새로고침 컨테이너)
    messages = get_room_messages(st.session_state.current_room)

    msg_container = st.container()
    with msg_container:
        if messages:
            for msg in messages:
                if msg["sender"] == st.session_state.current_user:
                    # 내 메시지는 왼쪽에
                    col1, col2 = st.columns([0.3, 0.7])
                    with col1:
                        st.write(f"**{msg['sender']}**")
                        st.info(msg["content"])
                else:
                    # 상대 메시지는 오른쪽에
                    col1, col2 = st.columns([0.7, 0.3])
                    with col2:
                        st.write(f"**{msg['sender']}**")
                        st.success(msg["content"])
        else:
            st.info("아직 메시지가 없습니다. 첫 메시지를 보내보세요!")

    st.divider()

    # 메시지 입력 영역
    col1, col2 = st.columns([0.9, 0.1])

    with col1:
        st.text_input(
            "메시지를 입력하고 Enter 키를 누르세요",
            placeholder="메시지 입력...",
            key="msg_input_submit",
            on_change=handle_message_submit
        )

    with col2:
        if st.button("✈️", key="send_btn", use_container_width=True):
            current_time = time.time()
            time_diff = current_time - st.session_state.last_message_time
            message_input = st.session_state.msg_input_submit

            if message_input.strip():
                if time_diff < 3:
                    st.error(f"3초 뒤에 다시 보낼 수 있습니다. ({3 - int(time_diff)}초)")
                else:
                    add_message(st.session_state.current_room, st.session_state.current_user, message_input)
                    st.session_state.last_message_time = current_time
                    st.session_state.msg_input_submit = ""
                    st.session_state.auto_refresh += 1
                    st.rerun()
            else:
                st.warning("메시지를 입력해주세요.")

    # 자동 새로고침 (숨겨진 요소)
    st.markdown("""
    <script>
    setTimeout(function() {
        window.location.reload();
    }, 3000);
    </script>
    """, unsafe_allow_html=True)

# 페이지 렌더링
if not st.session_state.user_id:
    render_login()
elif st.session_state.game_mode:
    st.sidebar.title("메뉴")
    if st.sidebar.button("🚪 로그아웃"):
        logout()
    render_minigame()
elif st.session_state.page == "lobby":
    st.sidebar.title("메뉴")
    if st.sidebar.button("🚪 로그아웃"):
        logout()
    render_lobby()
elif st.session_state.page == "create_room":
    st.sidebar.title("메뉴")
    if st.sidebar.button("🚪 로그아웃"):
        logout()
    render_create_room()
elif st.session_state.page == "join_room":
    st.sidebar.title("메뉴")
    if st.sidebar.button("🚪 로그아웃"):
        logout()
    render_join_room()
elif st.session_state.page == "chatroom":
    st.sidebar.title("메뉴")
    if st.sidebar.button("🎮 미니게임 시작", key="sidebar_game"):
        st.session_state.game_mode = True
        st.rerun()
    st.sidebar.divider()
    if st.sidebar.button("🚪 로그아웃"):
        logout()
    render_chatroom()
