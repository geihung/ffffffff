import random
import streamlit as st

PITCHES = ["포심", "투심", "슬라이더", "커브", "너클볼"]

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


def init_game():
    st.session_state["inning"] = 1
    st.session_state["max_inning"] = 3
    st.session_state["is_top"] = True
    st.session_state["balls"] = 0
    st.session_state["strikes"] = 0
    st.session_state["outs"] = 0
    st.session_state["bases"] = [False, False, False]
    st.session_state["home_score"] = 0
    st.session_state["away_score"] = 0
    st.session_state["home_batter_idx"] = 0
    st.session_state["away_batter_idx"] = 0
    st.session_state["logs"] = ["⚾ 플레이볼! 1회초 삼성 라이온즈의 공격으로 시작합니다."]
    st.session_state["game_over"] = False


if "inning" not in st.session_state:
    init_game()


def add_log(msg):
    st.session_state["logs"].insert(0, msg)


def reset_count():
    st.session_state["balls"] = 0
    st.session_state["strikes"] = 0


def next_batter():
    if st.session_state["is_top"]:
        st.session_state["away_batter_idx"] = (
            st.session_state["away_batter_idx"] + 1
        ) % 9
    else:
        st.session_state["home_batter_idx"] = (
            st.session_state["home_batter_idx"] + 1
        ) % 9


def advance_runners(hit_type):
    runs = 0
    b1, b2, b3 = st.session_state["bases"]

    if hit_type == "홈런":
        runs = 1 + sum([b1, b2, b3])
        st.session_state["bases"] = [False, False, False]
    elif hit_type == "3루타":
        runs = sum([b1, b2, b3])
        st.session_state["bases"] = [False, False, True]
    elif hit_type == "2루타":
        runs = sum([b2, b3])
        st.session_state["bases"] = [False, True, b1]
    elif hit_type == "1루타":
        runs = 1 if b3 else 0
        st.session_state["bases"] = [True, b1, b2]
    elif hit_type == "볼넷":
        if b1 and b2 and b3:
            runs = 1
            st.session_state["bases"] = [True, True, True]
        elif b1 and b2:
            st.session_state["bases"] = [True, True, True]
        elif b1:
            st.session_state["bases"] = [True, True, b3]
        else:
            st.session_state["bases"] = [True, b2, b3]

    if runs > 0:
        if st.session_state["is_top"]:
            st.session_state["away_score"] += runs
            add_log(f"🚨 삼성 {runs}점 득점!")
        else:
            st.session_state["home_score"] += runs
            add_log(f"🎉 KIA {runs}점 득점!")


def add_out(reason):
    st.session_state["outs"] += 1
    reset_count()
    next_batter()
    add_log(f"🔴 아웃! ({reason}) - {st.session_state['outs']}아웃")

    if st.session_state["outs"] >= 3:
        st.session_state["outs"] = 0
        st.session_state["bases"] = [False, False, False]

        if (
            not st.session_state["is_top"]
            and st.session_state["inning"] >= st.session_state["max_inning"]
        ):
            st.session_state["game_over"] = True
            add_log("🏁 경기 종료!")
            return

        if (
            st.session_state["is_top"]
            and st.session_state["inning"] >= st.session_state["max_inning"]
            and st.session_state["home_score"] > st.session_state["away_score"]
        ):
            st.session_state["game_over"] = True
            add_log("🏁 3회말 공격 없이 KIA의 승리로 경기 종료!")
            return

        if st.session_state["is_top"]:
            st.session_state["is_top"] = False
            add_log(
                f"🔄 공수 교대! {st.session_state['inning']}회말 KIA 타이거즈 공격입니다."
            )
        else:
            st.session_state["is_top"] = True
            st.session_state["inning"] += 1
            add_log(
                f"🔄 공수 교대! {st.session_state['inning']}회초 삼성 라이온즈 공격입니다."
            )


def handle_pitch():
    pitch = st.session_state["pitch_choice"]
    batter_name = AWAY_TEAM["batters"][st.session_state["away_batter_idx"]]
    pitcher_name = HOME_TEAM["pitcher"]

    pitch_stats = {
        "포심": [0.25, 0.30, 0.20, 0.10, 0.15],
        "투심": [0.15, 0.30, 0.20, 0.15, 0.20],
        "슬라이더": [0.35, 0.15, 0.25, 0.15, 0.10],
        "커브": [0.25, 0.25, 0.30, 0.10, 0.10],
        "너클볼": [0.40, 0.10, 0.35, 0.05, 0.10],
    }
    outcomes = ["헛스윙", "루킹 스트라이크", "볼", "파울", "타격"]
    result = random.choices(outcomes, weights=pitch_stats[pitch])[0]

    add_log(f"⚾ {pitcher_name}의 {pitch} 투구! (타자: {batter_name})")

    if result == "헛스윙":
        st.session_state["strikes"] += 1
        add_log(f"💨 {batter_name} 헛스윙! 스트라이크!")
        if st.session_state["strikes"] >= 3:
            add_out(f"{batter_name} 헛스윙 삼진")
    elif result == "루킹 스트라이크":
        st.session_state["strikes"] += 1
        add_log(f"🎯 {batter_name} 얼어붙습니다! 루킹 스트라이크!")
        if st.session_state["strikes"] >= 3:
            add_out(f"{batter_name} 루킹 삼진")
    elif result == "볼":
        st.session_state["balls"] += 1
        add_log("⚾ 스트라이크 존을 벗어납니다. 볼!")
        if st.session_state["balls"] >= 4:
            add_log(f"🚶 {batter_name} 볼넷 출루!")
            reset_count()
            next_batter()
            advance_runners("볼넷")
    elif result == "파울":
        if st.session_state["strikes"] < 2:
            st.session_state["strikes"] += 1
        add_log(f"🏏 {batter_name} 커트, 파울!")
    elif result == "타격":
        inplay = random.choices(
            ["아웃", "1루타", "2루타", "홈런"], weights=[0.65, 0.20, 0.10, 0.05]
        )[0]
        if inplay == "아웃":
            add_out(f"{batter_name} 수비수 정면 타구 아웃")
        else:
            add_log(f"💥 {batter_name} 안타! ({inplay})")
            reset_count()
            next_batter()
            advance_runners(inplay)


def handle_bat():
    swing = st.session_state["swing_choice"]
    guess_pitch = st.session_state["guess_choice"]
    batter_name = HOME_TEAM["batters"][st.session_state["home_batter_idx"]]
    pitcher_name = AWAY_TEAM["pitcher"]

    cpu_pitch = random.choice(PITCHES)
    add_log(
        f"[{pitcher_name} 투구: {cpu_pitch}] vs [{batter_name}: {swing} / {guess_pitch} 노림]"
    )

    if guess_pitch == cpu_pitch:
        if swing == "파워스윙":
            result = random.choices(
                ["홈런", "2루타", "3루타"], weights=[0.4, 0.4, 0.2]
            )[0]
        elif swing == "컨택":
            result = random.choices(["1루타", "2루타"], weights=[0.7, 0.3])[0]
        else:
            result = random.choices(
                ["1루타", "2루타", "3루타", "홈런"], weights=[0.5, 0.25, 0.1, 0.15]
            )[0]

        add_log(f"💥 {batter_name}, 노림수 적중! {result}!")
        reset_count()
        next_batter()
        advance_runners(result)

        if (
            not st.session_state["is_top"]
            and st.session_state["inning"] >= st.session_state["max_inning"]
            and st.session_state["home_score"] > st.session_state["away_score"]
        ):
            st.session_state["game_over"] = True
            add_log(f"🎆 {batter_name}의 끝내기! KIA 승리!")
    else:
        outcome = random.choices(
            ["헛스윙", "파울", "볼", "범타"], weights=[0.35, 0.25, 0.25, 0.15]
        )[0]
        if outcome == "헛스윙":
            st.session_state["strikes"] += 1
            add_log(f"💨 {batter_name} 헛스윙! 스트라이크!")
            if st.session_state["strikes"] >= 3:
                add_out(f"{batter_name} 삼진 아웃")
        elif outcome == "파울":
            if st.session_state["strikes"] < 2:
                st.session_state["strikes"] += 1
            add_log(f"🏏 {batter_name} 파울!")
        elif outcome == "볼":
            st.session_state["balls"] += 1
            add_log("👀 볼!")
            if st.session_state["balls"] >= 4:
                add_log(f"🚶 {batter_name} 볼넷 출루!")
                reset_count()
                next_batter()
                advance_runners("볼넷")
        elif outcome == "범타":
            add_out(f"{batter_name} 내야 땅볼 / 외야 뜬공")


# ================= UI 화면 구성 =================
st.title("⚾ KBO 프로야구 미니 시뮬레이터")

half_text = "초 ▲" if st.session_state["is_top"] else "말 ▼"
st.subheader(
    f"🏟️ {st.session_state['inning']}회{half_text} (총 {st.session_state['max_inning']}이닝 경기)"
)

col_score, col_bso, col_base = st.columns([1.2, 1.3, 1])

with col_score:
    st.markdown("**[스코어보드]**")
    st.write(f"🦁 삼성 (초): {st.session_state['away_score']} 점")
    st.write(f"🐯 KIA (말): {st.session_state['home_score']} 점")

with col_bso:
    st.markdown("**[B - S - O 카운트]**")
    b_lights = "🟢 " * st.session_state["balls"] + "⚫ " * (3 - st.session_state["balls"])
    s_lights = "🟡 " * st.session_state["strikes"] + "⚫ " * (2 - st.session_state["strikes"])
    o_lights = "🔴 " * st.session_state["outs"] + "⚫ " * (2 - st.session_state["outs"])

    st.write(f"B : {b_lights}")
    st.write(f"S : {s_lights}")
    st.write(f"O : {o_lights}")

with col_base:
    st.markdown("**[주자 상황]**")
    b1, b2, b3 = ["🟠" if b else "◇" for b in st.session_state["bases"]]
    st.write(f"  {b2}")
    st.write(f"{b3}   {b1}")

st.markdown("---")

if st.session_state["game_over"]:
    if st.session_state["home_score"] > st.session_state["away_score"]:
        st.success(
            f"🏆 KIA 타이거즈 승리! ({st.session_state['home_score']} : {st.session_state['away_score']})"
        )
    elif st.session_state["home_score"] < st.session_state["away_score"]:
        st.error(
            f"😢 삼성 라이온즈 승리... ({st.session_state['away_score']} : {st.session_state['home_score']})"
        )
    else:
        st.info(
            f"🤝 무승부로 경기 종료! ({st.session_state['home_score']} : {st.session_state['away_score']})"
        )

    st.button("🔄 새 경기 시작", on_click=init_game)

else:
    if st.session_state["is_top"]:
        cur_batter = AWAY_TEAM["batters"][st.session_state["away_batter_idx"]]
        cur_pitcher = HOME_TEAM["pitcher"]
        batter_num = st.session_state["away_batter_idx"] + 1

        st.info(
            f"🛡️ 수비 (투구) | 투수: 🐯 {cur_pitcher} vs 타자: 🦁 {batter_num}번 {cur_batter}"
        )
        st.selectbox("던질 구종 선택", PITCHES, key="pitch_choice")
        st.button("⚾ 공 던지기!", on_click=handle_pitch)

    else:
        cur_batter = HOME_TEAM["batters"][st.session_state["home_batter_idx"]]
        cur_pitcher = AWAY_TEAM["pitcher"]
        batter_num = st.session_state["home_batter_idx"] + 1

        st.warning(
            f"⚔️ 공격 (타격) | 투수: 🦁 {cur_pitcher} vs 타자: 🐯 {batter_num}번 {cur_batter}"
        )
        c1, c2 = st.columns(2)
        with c1:
            st.radio("스윙 종류 선택", ["파워스윙", "컨택", "보통스윙"], key="swing_choice")
        with c2:
            st.selectbox("노릴 구종 선택", PITCHES, key="guess_choice")

        st.button("🏏 스윙하기!", on_click=handle_bat)

st.subheader("📢 문자 중계")
for log in st.session_state["logs"][:8]:
    st.write(log)
