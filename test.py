import streamlit as st
import pandas as pd
import calendar
from datetime import date, timedelta

st.set_page_config(page_title="시험 공부 계획표", layout="wide")
st.title("📚 시험 공부 계획 자동 생성기")

# --- 1. 과목별 시험 일정 입력 ---
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

# --- 2. 하루 공부 가능 시간 입력 ---
st.header("2. 하루 공부 가능 시간 입력")
daily_hours = st.number_input("하루 공부 가능 시간 (시간)", min_value=1, value=4, step=1)

# --- 3. 계획 생성 ---
if st.button("📅 계획 생성"):
    today = date.today()
    plan = []

    for s in subjects:
        days_left = (s["시험일"] - today).days
        s["남은일수"] = max(days_left, 0)
        if s["남은일수"] > 0:
            urgency_score = 1 / s["남은일수"]
            s["가중치"] = urgency_score * 0.5 + (s["중요도"] / 5) * 0.5
        else:
            s["가중치"] = 0

    total_weight = sum(s["가중치"] for s in subjects)
    max_days = max((s["남은일수"] for s in subjects), default=0)

    for day_offset in range(max_days):
        current_date = today + timedelta(days=day_offset)
        for s in subjects:
            if day_offset < s["남은일수"] and total_weight > 0:
                hours = round((s["가중치"] / total_weight) * daily_hours, 1)
                if hours > 0:
                    plan.append({"날짜": current_date, "과목": s["과목"], "시간": hours})

    df = pd.DataFrame(plan)
    st.subheader("📆 생성된 공부 계획표 (표)")
    st.dataframe(df)

    # --- 4. 달력 시각화 ---
    st.subheader("📊 달력형 공부 계획")

    if not df.empty:
        start_month = today.month
        start_year = today.year
        end_date = df["날짜"].max()
        end_month = end_date.month
        end_year = end_date.year

        # 여러 달 표시
        current_year, current_month = start_year, start_month
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            st.markdown(f"### {current_year}년 {current_month}월")
            cal = calendar.Calendar(firstweekday=6)  # 일요일 시작

            month_days = cal.monthdatescalendar(current_year, current_month)

            # 달력 표 만들기
            table = "<table style='border-collapse: collapse; width: 100%;'>"
            table += "<tr>" + "".join([f"<th style='border:1px solid #ccc; padding:4px; text-align:center;'>{d}</th>" for d in ["일","월","화","수","목","금","토"]]) + "</tr>"

            for week in month_days:
                table += "<tr>"
                for day in week:
                    cell_content = f"<div style='font-weight:bold;'>{day.day}</div>"
                    # 계획이 있으면 표시
                    daily = df[df["날짜"] == pd.Timestamp(day)]
                    if not daily.empty:
                        for _, row in daily.iterrows():
                            cell_content += f"<div style='font-size:12px; background:#e0f7fa; margin:2px; padding:2px; border-radius:4px;'>{row['과목']} ({row['시간']}h)</div>"
                    style = "border:1px solid #ccc; vertical-align:top; padding:4px; height:100px;"
                    if day.month != current_month:  # 이전/다음달 날짜 회색 처리
                        style += "background:#f0f0f0; color:#aaa;"
                    table += f"<td style='{style}'>{cell_content}</td>"
                table += "</tr>"

            table += "</table>"
            st.markdown(table, unsafe_allow_html=True)

            # 다음 달로 이동
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1

    # --- 5. CSV 다운로드 ---
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 계획 다운로드 (CSV)", csv, "study_plan.csv", "text/csv")
