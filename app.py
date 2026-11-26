import random
import streamlit as st

st.set_page_config(page_title="Streamlit 미니 야구", page_icon="⚾")

PITCHES = ["포심", "투심", "슬라이더", "커브", "너클볼"]


# 1. 게임 상태 초기화
def init_game():
    st.session_state.role = None
    st.session_state.inning = 1
    st.session_state.max_inning = 3
    st.session_state.balls = 0
    st.session_state.strikes = 0
    st.session_state.outs = 0
    st.session_state.bases = [False, False, False]  # 1루, 2루, 3루 주자 여부
    st.session_state.user_score = 0
    st.session_state.cpu_score = 0
    st.session_state.logs = ["⚾ 경기 시작! 역할을 선택하세요."]
    st.session_state.game_over = False


if "role" not in st.session_state:
    init_game()


def add_log(msg):
    st.session_state.logs.insert(0, msg)


def reset_count():
    st.session_state.balls = 0
    st.session_state.strikes = 0


# 2. 주자 진루 및 득점 처리 함수
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
    elif hit_type == "1루타" or hit_type == "볼넷":
        runs = 1 if b3 else 0
        # 밀어내기(볼넷)일 경우와 안타일 경우 단순화 진루
        if hit_type == "볼넷":
            if b1 and b2 and b3:
                runs = 1
                st.session_state.bases = [True, True, True]
            elif b1 and b2:
                st.session_state.bases = [True, True, True]
            elif b1:
                st.session_state.bases = [True, True, b3]
            else:
                st.session_state.bases = [True, b2, b3]
        else:
            st.session_state.bases = [True, b1, b2]

    if runs > 0:
        if st.session_state.role == "타자":
            st.session_state.user_score += runs
        else:
            st.session_state.cpu_score += runs
        add_log(f"🎉 {runs}점 득점!")


# 3. 아웃 및 이닝 종료 처리
def add_out(reason):
    st.session_state.outs += 1
    reset_count()
    add_log(f"🔴 아웃! ({reason}) - {st.session_state.outs}아웃")

    if st.session_state.outs >= 3:
        st.session_state.outs = 0
        st.session_state.bases = [False, False, False]
        st.session_state.inning += 1

        # 상대 팀 공격 시뮬레이션 (랜덤 0~2점)
        opp_runs = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        if st.session_state.role == "타자":
            st.session_state.cpu_score += opp_runs
        else:
            st.session_state.user_score += opp_runs

        add_log(
            f"🔄 공수 교대! 상대 팀이 이닝 동안 {opp_runs}점을 획득했습니다."
        )

        if st.session_state.inning > st.session_state.max_inning:
            st.session_state.game_over = True
            add_log("🏁 경기 종료!")


# 4. 타자 플레이 로직
def play_batter(swing, guess_pitch):
    cpu_pitch = random.choice(PITCHES)
    add_log(
        f"투수 투구: [{cpu_pitch}] / 타자 선택: [{swing} - {guess_pitch} 노림]"
    )

    # 구종을 정확히 노렸을 때 -> 안타!
    if guess_pitch == cpu_pitch:
        if swing == "파워스윙":
            result = random.choices(
                ["홈런", "2루타", "3루타"], weights=[0.4, 0.4, 0.2]
            )[0]
        elif swing == "컨택":
            result = random.choices(["1루타", "2루타"], weights=[0.7, 0.3])[0]
        else:  # 보통스윙
            result = random.choices(
                ["1루타", "2루타", "3루타", "홈런"], weights=[0.5, 0.25, 0.1, 0.15]
            )[0]

        add_log(f"💥 정타! 구종 예측 성공! 결과: **{result}**")
        reset_count()
        advance_runners(result)

    # 구종 예측 실패 시 -> 실제 야구처럼 볼/스트라이크/파울/범타 확률 분기
    else:
        outcome = random.choices(
            ["헛스윙", "파울", "볼", "범타"], weights=[0.35, 0.25, 0.25, 0.15]
        )[0]
        if outcome == "헛스윙":
            st.session_state.strikes += 1
            add_log("💨 헛스윙 스트라이크!")
            if st.session_state.strikes >= 3:
                add_out("삼진 아웃")
        elif outcome == "파울":
            if st.session_state.strikes < 2:
                st.session_state.strikes += 1
            add_log("🏏 파울!")
        elif outcome == "볼":
            st.session_state.balls += 1
            add_log("👀 볼!")
            if st.session_state.balls >= 4:
                add_log("🚶 볼넷 출루!")
                reset_count()
                advance_runners("볼넷")
        elif outcome == "범타":
            add_out("내야 땅볼 / 외야 뜬공")


# 5. 투수 플레이 로직
def play_pitcher(pitch):
    # 구종별 특성 (스트라이크/헛스윙 확률 가중치)
    pitch_stats = {
        "포심": [0.25, 0.30, 0.20, 0.10, 0.15],  # 헛스윙, 루킹S, 볼, 파울, 인플레이(안타/아웃)
        "투심": [0.15, 0.30, 0.20, 0.15, 0.20],
        "슬라이더": [0.35, 0.15, 0.25, 0.15, 0.10],
        "커브": [0.25, 0.25, 0.30, 0.10, 0.10],
        "너클볼": [0.40, 0.10, 0.35, 0.05, 0.10],
    }
    outcomes = ["헛스윙", "루킹 스트라이크", "볼", "파울", "타격"]
    result = random.choices(outcomes, weights=pitch_stats[pitch])[0]

    add_log(f"투수 투구: [{pitch}]")

    if result == "헛스윙":
        st.session_state.strikes += 1
        add_log("💨 타자 헛스윙! 스트라이크!")
        if st.session_state.strikes >= 3:
            add_out("헛스윙 삼진!")
    elif result == "루킹 스트라이크":
        st.session_state.strikes += 1
        add_log("🎯 보더라인 걸치는 루킹 스트라이크!")
        if st.session_state.strikes >= 3:
            add_out("루킹 삼진!")
    elif result == "볼":
        st.session_state.balls += 1
        add_log("⚾ 스트라이크 존을 벗어납니다. 볼!")
        if st.session_state.balls >= 4:
            add_log("🚶 볼넷 허용!")
            reset_count()
            advance_runners("볼넷")
    elif result == "파울":
        if st.session_state.strikes < 2:
            st.session_state.strikes += 1
        add_log("🏏 타자 커트, 파울!")
    elif result == "타격":
        inplay = random.choices(
            ["아웃", "1루타", "2루타", "홈런"], weights=[0.65, 0.20, 0.10, 0.05]
        )[0]
        if inplay == "아웃":
            add_out("수비수 정면 타구 아웃")
        else:
            add_log(f"💥 피안타 허용! ({inplay})")
            reset_count()
            advance_runners(inplay)


# ================= UI 렌더링 =================
st.title("⚾ Streamlit 야구 시뮬레이터")

# 역할 선택 화면
if st.session_state.role is None:
    st.subheader("플레이할 포지션을 선택하세요 (총 3이닝 경기)")
    col1, col2 = st.columns(2)
    if col1.button("🏏 타자로 플레이", use_container_width=True):
        st.session_state.role = "타자"
        add_log("🏏 타자 모드로 경기를 시작합니다!")
        st.rerun()
    if col2.button("⚾ 투수로 플레이", use_container_width=True):
        st.session_state.role = "투수"
        add_log("⚾ 투수 모드로 경기를 시작합니다!")
        st.rerun()

# 경기 진행 화면
else:
    # 전광판 영역
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "이닝", f"{min(st.session_state.inning, st.session_state.max_inning)}회"
    )
    c2.metric("점수 (나 : 상대)", f"{st.session_state.user_score} : {st.session_state.cpu_score}")
    c3.metric(
        "볼카운트 (B-S-O)",
        f"{st.session_state.balls}B - {st.session_state.strikes}S - {st.session_state.outs}O",
    )

    # 주자 상황 표시
    b_icons = ["🟠" if b else "⚪" for b in st.session_state.bases]
    c4.markdown(f"**주자 상황**\n\n1루:{b_icons[0]} 2루:{b_icons[1]} 3루:{b_icons[2]}")
    st.markdown("---")

    # 경기 종료 시 결과 출력
    if st.session_state.game_over:
        if st.session_state.user_score > st.session_state.cpu_score:
            st.success(
                f"🏆 승리했습니다! ({st.session_state.user_score} : {st.session_state.cpu_score})"
            )
        elif st.session_state.user_score < st.session_state.cpu_score:
            st.error(
                f"😢 패배했습니다... ({st.session_state.user_score} : {st.session_state.cpu_score})"
            )
        else:
            st.info(
                f"🤝 무승부입니다! ({st.session_state.user_score} : {st.session_state.cpu_score})"
            )

        if st.button("🔄 새 경기 시작"):
            init_game()
            st.rerun()

    # 컨트롤 패널 (타자 vs 투수)
    else:
        if st.session_state.role == "타자":
            st.subheader("🏏 타석 선택")
            col1, col2 = st.columns(2)
            swing = col1.radio("스윙 종류 선택", ["파워스윙", "컨택", "보통스윙"])
            guess = col2.selectbox("노릴 구종 선택", PITCHES)

            if st.button("스윙하기!", type="primary", use_container_width=True):
                play_batter(swing, guess)
                st.rerun()

        elif st.session_state.role == "투수":
            st.subheader("⚾ 투구 선택")
            pitch = st.radio("던질 구종 선택", PITCHES, horizontal=True)

            if st.button("공 던지기!", type="primary", use_container_width=True):
                play_pitcher(pitch)
                st.rerun()

    # 중계 로그
    st.subheader("📢 경기 중계 로그")
    for log in st.session_state.logs[:8]:
        st.write(log)
