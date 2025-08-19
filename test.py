import streamlit as st
import pandas as pd
from datetime import date, timedelta
import altair as alt

# ✅ 페이지 설정
st.set_page_config(page_title="시험 공부 계획표", layout="wide")

st.title("📚 시험 공부 계획 자동 생성기")

# --- 1. 시험 일정 입력 ---
st.header("1. 과목별 시험 일정 입력")
subjects = []
num_subjects = st.number_input("시험 과목 수", min_value=1, value=3, step=1)

for i in range(num_subjects):
    with st.expander(f"과목 {i+1} 입력"):
        subject = st.text_input(f"{i+1}번 과목명", key=f"sub_{i}")
        exam_date = st.date_input(f"{subject or '과목'} 시험 날짜", min_value=date.today(), key=f"date_{i}")
        importance = st.slider(f"{subject or '과목'} 중요도 (1=낮음, 5=높음)", 1, 5, 3, key=f"imp_{i}")
        if subject:
            subjects.append({
                "과목": subject,
                "시험일": exam_date,
                "중요도": importance
            })

# --- 2. 하루 공부 가능 시간 ---
st.header("2. 하루 공부 가능 시간 입력")
daily_hours = st.number_input("하루 공부 가능 시간 (시간)", min_value=1, value=4, step=1)

# --- 3. 계획 생성 ---
if st.button("📅 계획 생성"):
    today = date.today()
    plan = []

    # 시험일까지 남은 일수 계산
    for s in subjects:
        days_left = (s["시험일"] - today).days
        s["남은일수"] = max(days_left, 0)

    # 과목별 가중치 계산 (시험일 가까움 + 중요도)
    for s in subjects:
        if s["남은일수"] > 0:
            urgency_score = 1 / s["남은일수"]  # 가까울수록 점수 ↑
            s["가중치"] = urgency_score * 0.5 + (s["중요도"] / 5) * 0.5
        else:
            s["가중치"] = 0

    total_weight = sum(s["가중치"] for s in subjects)

    # 날짜별 계획 생성
    max_days = max(s["남은일수"] for s in subjects) if subjects else 0
    for day_offset in range(max_days):
        current_date = today + timedelta(days=day_offset)
        for s in subjects:
            if day_offset < s["남은일수"]:
                if total_weight > 0:
                    hours = round((s["가중치"] / total_weight) * daily_hours, 2)
                else:
                    hours = 0
                if hours > 0:
                    plan.append({
                        "날짜": current_date,
                        "과목": s["과목"],
                        "공부시간(시간)": hours
                    })

    # DataFrame 변환
    df = pd.DataFrame(plan)
    st.subheader("📆 생성된 공부 계획")
    st.dataframe(df)

    # --- 4. 시각화 (Altair로 색깔별 과목 표시) ---
    st.subheader("📊 과목별 공부 계획 시각화")
    if not df.empty:
        chart = alt.Chart(df).mark_bar().encode(
            x="날짜:T",
            y="공부시간(시간):Q",
            color="과목:N",
            tooltip=["날짜", "과목", "공부시간(시간)"]
        ).properties(width=700, height=400)

        st.altair_chart(chart, use_container_width=True)

    # --- 5. CSV 다운로드 ---
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 계획 다운로드 (CSV)", csv, "study_plan.csv", "text/csv")
