import streamlit as st
import pandas as pd
import calendar
from datetime import date, timedelta

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="📘 시험 공부 계획 앱", layout="wide")

st.title("📘 시험 공부 계획 자동 생성기")
st.write("시험 범위를 입력하면 자동으로 하루 공부량과 복습 계획을 나눠줍니다!")

# -------------------------
# 입력 섹션
# -------------------------
st.sidebar.header("과목 입력")

num_subjects = st.sidebar.number_input("과목 개수", 1, 10, 3)
subjects = []

for i in range(num_subjects):
    with st.sidebar.expander(f"과목 {i+1} 입력"):
        subject = st.text_input(f"{i+1}번 과목명", key=f"sub_{i}")
        publisher = st.text_input("교과서 출판사", key=f"pub_{i}")
        unit = st.text_input("단원명", key=f"unit_{i}")
        exam_date = st.date_input("시험 날짜", min_value=date.today(), key=f"date_{i}")
        start = st.text_input("범위 시작 (예: p.1, 1번)", key=f"start_{i}")
        end = st.text_input("범위 끝 (예: p.150, 200번)", key=f"end_{i}")

        if subject:
            subjects.append({
                "과목": subject,
                "출판사": publisher,
                "단원": unit,
                "시험일": exam_date,
                "범위시작": start,
                "범위끝": end
            })

daily_hours = st.sidebar.slider("하루 총 공부시간(시간)", 1, 12, 6)

# -------------------------
# 범위 파싱 함수
# -------------------------
def parse_range(start, end):
    """범위 문자열에서 숫자 추출"""
    try:
        start_num = int(''.join(filter(str.isdigit, start)))
        end_num = int(''.join(filter(str.isdigit, end)))
        return start_num, end_num, start[0]
    except:
        return None, None, ""

# -------------------------
# 계획 생성
# -------------------------
plan = []
today = date.today()

if st.sidebar.button("📅 공부 계획 세우기"):
    for s in subjects:
        days_left = (s["시험일"] - today).days
        if days_left <= 0:
            continue

        start_num, end_num, prefix = parse_range(s["범위시작"], s["범위끝"])
        if not start_num or not end_num:
            continue

        total_amount = end_num - start_num + 1
        daily_amount = total_amount // days_left

        for d in range(days_left):
            current_date = today + timedelta(days=d)
            part_start = start_num + d * daily_amount
            part_end = part_start + daily_amount - 1
            if d == days_left - 1:  # 마지막 날은 남은 범위 몰아주기
                part_end = end_num

            task = {
                "날짜": current_date,
                "과목": s["과목"],
                "출판사": s["출판사"],
                "단원": s["단원"],
                "범위": f"{prefix}{part_start} ~ {prefix}{part_end}",
                "종류": "공부",
                "예상시간(h)": round(daily_hours / num_subjects, 1)
            }
            plan.append(task)

            # 복습 일정 추가 (D+1, D+3, D+7)
            for offset in [1, 3, 7]:
                review_date = current_date + timedelta(days=offset)
                if review_date <= s["시험일"]:
                    plan.append({
                        "날짜": review_date,
                        "과목": s["과목"],
                        "출판사": s["출판사"],
                        "단원": s["단원"],
                        "범위": f"{prefix}{part_start} ~ {prefix}{part_end}",
                        "종류": f"복습(D+{offset})",
                        "예상시간(h)": round(daily_hours / num_subjects / 2, 1)
                    })

    # -------------------------
    # DataFrame으로 변환
    # -------------------------
    df = pd.DataFrame(plan)
    df = df.sort_values(by=["날짜", "과목"])

    # -------------------------
    # 오늘 할 공부
    # -------------------------
    st.subheader("📌 오늘 할 공부")
    today_plan = df[df["날짜"] == today]

    if today_plan.empty:
        st.info("오늘은 계획된 공부가 없습니다! 😴")
    else:
        done_count = 0
        for i, row in today_plan.iterrows():
            done = st.checkbox(
                f"[{row['과목']}({row['출판사']}) {row['단원']} - {row['범위']} ({row['종류']})",
                key=f"done_{i}"
            )
            if done:
                st.success("완료 ✅")
                done_count += 1

        st.write(f"진행률: {done_count} / {len(today_plan)} 완료")

    # -------------------------
    # 전체 계획 테이블
    # -------------------------
    st.subheader("📖 전체 계획표")
    st.dataframe(df, use_container_width=True)

    # -------------------------
    # 달력 시각화
    # -------------------------
    st.subheader("📅 달력 시각화")

    def make_calendar(year, month, df):
        cal = calendar.Calendar()
        month_days = cal.itermonthdates(year, month)
        events = df[df["날짜"].between(date(year, month, 1), date(year, month, 28))]

        html = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
        html += "<tr>" + "".join([f"<th>{d}</th>" for d in ["월", "화", "수", "목", "금", "토", "일"]]) + "</tr><tr>"

        week_day = 0
        for day in month_days:
            if day.month != month:
                html += "<td style='padding:10px; background:#f0f0f0;'></td>"
            else:
                tasks = events[events["날짜"] == day]
                content = f"<b>{day.day}</b><br>"
                for _, t in tasks.iterrows():
                    color = "#a3c9f7" if t["종류"] == "공부" else "#f7b3c9"
                    content += f"<div style='background:{color}; border-radius:5px; margin:2px; padding:2px; font-size:10px'>{t['과목']}</div>"
                html += f"<td style='padding:10px; vertical-align:top;'>{content}</td>"

            week_day += 1
            if week_day == 7:
                html += "</tr><tr>"
                week_day = 0
        html += "</tr></table>"
        return html

    month_html = make_calendar(today.year, today.month, df)
    st.markdown(month_html, unsafe_allow_html=True)
