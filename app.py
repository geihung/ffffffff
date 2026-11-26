import random
import streamlit as st

st.set_page_config(page_title="KBO 프로야구 시뮬레이터", page_icon="⚾")

PITCHES = ["포심", "투심", "슬라이더", "커브", "너클볼"]

# KBO 선수 데이터 세팅
HOME_TEAM = {
    "name": "KIA 타이거즈 (나)",
    "pitcher": "양현종",
    "batters": [
        "박찬호",
        "소크라테스",
        "김도영",
        "최형우",
        "나성범",
        "김선빈",
        "이우성",
        "김태군",
        "최원준",
    ],
}

AWAY_TEAM = {
    "name": "삼성 라이온즈 (상대)",
    "pitcher": "원태인",
    "batters": [
        "김지찬",
        "이재현",
        "구자욱",
        "디아즈",
        "강민호",
        "박병호",
        "김영웅",
        "류지혁",
        "김헌곤",
    ],
}


# 1. 경기 초기화
def init_game():
    st.session_state.inning = 1
    st.session_state.max_inning = 3  # 3이닝 경기
    st.session_state.is_top = True  # True: 초(상대 공격/내 투구), False: 말(내 공격/내 타격)
    st.session_state.balls = 0
    st.session_state.strikes = 0
    st.session_state.outs = 0
    st.session_state.bases = [False, False, False]  # 1루, 2루, 3루
    st.session_state.home_score = 0
    st.session_state.away_score = 0
    st.session_state.home_batter_idx = 0
    st.session_state.away_batter_idx = 0
    st.session_state.logs = ["⚾ 플레이볼! 1회초 삼성 라이온즈의 공격으로 시작합니다."]
    st.session_state.game_over = False


if "inning" not in st.session_state:
    init_game()


def add_log(msg):
    st.session_state.logs.insert(0, msg)


def reset_count():
    st.session_state.balls = 0
    st.session_state.strikes = 0


def next_batter():
    if st.session_state.is_top:
        st.session_state.away_batter_idx = (
            st.session_state.away_batter_idx + 1
        ) % 9
    else:
        st.session_state.home_batter_idx = (
            st.session_state.home_batter_idx + 1
        ) % 9


# 2. 주자 진루 및 득점 처리
def advance_runners(hit_type):
    runs = 0
    b1, b2, b3 = st.session_state.bases

    if hit_type == "홈런":
        runs = 1 + sum([b1, b2, b3])
        st.session_state.bases = [False, False, False]
    elif hit_type == "3루타":
        runs = sum([b1, b2, b3])
        st.session_state.bases = [False, False, True]
    elif hit_type == "2루타":
        runs = sum([b2, b3])
        st.session_state.bases = [False, True, b1]
    elif hit_type == "1루타":
        runs = 1 if b3 else 0
        st.session_state.bases = [True, b1, b2]
    elif hit_type == "볼넷":
        if b1 and b2 and b3:
            runs = 1
            st.session_state.bases = [True, True, True]
        elif b1 and b2:
            st.session_state.bases = [True, True, True]
        elif b1:
            st.session_state.bases = [True, True, b3]
        else:
            st.session_state.bases = [True, b2, b3]

    if runs > 0:
        if st.session_state.is_top:
            st.session_state.away_score += runs
            add_log(f"🚨 삼성 {
