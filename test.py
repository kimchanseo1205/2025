import streamlit as st
import pandas as pd
import calendar
from datetime import date, timedelta

st.set_page_config(page_title="시험 공부 계획표", layout="wide")
st.title("📚 시험 공부 계획 자동 생성기")

# --- 1. 과목 입력 ---
st.header("1. 과목별 시험 정보 입력")
subjects = []
num_subjects = st.number_input("시험 과목 수", min_value=1, value=3, step=1)

for i in range(num_subjects):
    with st.expander(f"과목 {i+1} 입력"):
        subject = st.text_input(f"{i+1}번 과목명", key=f"sub_{i}")
        publisher = st.text_input(f"{subject or '과목'} 교과서 출판사", key=f"pub_{i}")
        unit = st.text_input(f"{subject or '과목'} 단원명", key=f"unit_{i}")
        exam_date = st.date_input(f"{subject or '과목'} 시험 날짜", min_value=date.today(), key=f"date_{i}")
        importance = st.slider(f"{subject or '과목'} 중요도 (1=낮음, 5=높음)", 1, 5, 3, key=f"imp_{i}")
        
        st.markdown("시험범위 (예: p.1~50, 문제 1~30)")
        start = st.text_input(f"{subject} 시작 범위", key=f"start_{i}")
        end = st.text_input(f"{subject} 끝 범위", key=f"end_{i}")

        if subject:
            subjects.append({
                "과목": subject,
                "출판사": publisher,
                "단원": unit,
                "시험일": exam_date,
                "중요도": importance,
                "범위시작": start,
                "범위끝": end
            })

# --- 2. 하루 공부 가능 시간 ---
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
            # 하루 분량을 "시작~끝" 숫자가 아니라 단순 반복으로 처리
            for d in range(s["남은일수"]):
                current_date = today + timedelta(days=d)

                # 본공부 일정
                plan.append({
                    "날짜": current_date,
                    "과목": s["과목"],
                    "출판사": s["출판사"],
                    "단원": s["단원"],
                    "범위": f"{s['범위시작']} ~ {s['범위끝']}",
                    "종류": "공부",
                    "예상시간(h)": round(daily_hours / num_subjects, 1)
                })

                # 복습 일정 자동 생성 (+1, +3, +7일)
                for offset in [1, 3, 7]:
                    review_date = current_date + timedelta(days=offset)
                    if review_date <= s["시험일"]:  
                        plan.append({
                            "날짜": review_date,
                            "과목": s["과목"],
                            "출판사": s["출판사"],
                            "단원": s["단원"],
                            "범위": f"{s['범위시작']} ~ {s['범위끝']}",
                            "종류": f"복습(D+{offset})",
                            "예상시간(h)": round(daily_hours / num_subjects / 2, 1)
                        })

    df = pd.DataFrame(plan).sort_values(by=["날짜", "과목"])

    # --- 4. 오늘의 계획 체크리스트 ---
    st.subheader("✅ 오늘 공부 체크리스트")
    today_plan = df[df["날짜"] == pd.Timestamp(today)]
    done_count = 0

    if not today_plan.empty:
        for i, row in today_plan.iterrows():
            checked = st.checkbox(
                f"[{row['과목']} - {row['출판사']}] {row['단원']} / {row['범위']} ({row['종류']}, {row['예상시간(h)']}h)",
                key=f"check_{i}"
            )
            if checked:
                done_count += 1

        progress = done_count / len(today_plan)
        st.progress(progress)
        st.write(f"오늘 계획 달성률: **{int(progress*100)}%**")
    else:
        st.info("오늘은 특별히 배정된 공부 계획이 없습니다!")

    # --- 5. 전체 계획표 ---
    st.subheader("📆 전체 공부 계획표")
    st.dataframe(df)

    # --- 6. 달력 출력 ---
    st.subheader("📊 달력형 계획표")
    if not df.empty:
        start_month, start_year = today.month, today.year
        end_date = df["날짜"].max()
        end_month, end_year = end_date.month, end_date.year

        current_year, current_month = start_year, start_month
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            st.markdown(f"### {current_year}년 {current_month}월")
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdatescalendar(current_year, current_month)

            table = "<table style='border-collapse: collapse; width: 100%;'>"
            table += "<tr>" + "".join([f"<th style='border:1px solid #ccc; padding:4px; text-align:center;'>{d}</th>" for d in ["일","월","화","수","목","금","토"]]) + "</tr>"

            for week in month_days:
                table += "<tr>"
                for day in week:
                    cell_content = f"<div style='font-weight:bold;'>{day.day}</div>"
                    daily = df[df["날짜"] == pd.Timestamp(day)]
                    if not daily.empty:
                        for _, row in daily.iterrows():
                            color = "#e3f2fd" if row["종류"] == "공부" else "#ffe0b2"
                            cell_content += f"<div style='font-size:12px; background:{color}; margin:2px; padding:2px; border-radius:4px;'>{row['과목']} ({row['출판사']})<br>{row['단원']}<br>{row['종류']} [{row['범위']}]</div>"
                    style = "border:1px solid #ccc; vertical-align:top; padding:4px; height:120px;"
                    if day.month != current_month:
                        style += "background:#f0f0f0; color:#aaa;"
                    table += f"<td style='{style}'>{cell_content}</td>"
                table += "</tr>"

            table += "</table>"
            st.markdown(table, unsafe_allow_html=True)

            # 다음 달 이동
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1

    # --- 7. CSV 다운로드 ---
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 계획 다운로드 (CSV)", csv, "study_plan.csv", "text/csv")
