# ==============================
# 스타일 꾸미기 (CSS + 배경 이미지)
# ==============================
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
  background-image: url("https://images.unsplash.com/photo-1523050854058-8df90110c9f1");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

[data-testid="stHeader"] {
  background: rgba(0,0,0,0);
}

.block-container {
  background: rgba(255, 255, 255, 0.8);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ==============================
# Streamlit 앱 기본 설정
# ==============================
st.set_page_config(page_title="시험 공부 계획표", layout="wide")

st.title("📚 시험 공부 계획 앱")
st.write("시험 범위를 입력하면 자동으로 공부량을 분배하고, 복습까지 포함한 일정을 만들어 드립니다.")

# ==============================
# 유틸 함수
# ==============================
def parse_range(start, end):
    """범위 문자열에서 숫자 추출"""
    try:
        start_num = int(''.join(filter(str.isdigit, start)))
        end_num = int(''.join(filter(str.isdigit, end)))
        prefix = ''.join(filter(str.isalpha, start))  # p, 문제, 단원 등
        return start_num, end_num, prefix
    except:
        return None, None, ""

# ==============================
# 입력 영역
# ==============================
st.sidebar.header("시험 과목 & 교재 입력")

num_subjects = st.sidebar.number_input("과목 수", min_value=1, max_value=10, value=2, step=1)
daily_hours = st.sidebar.number_input("하루 공부 가능 시간 (시간)", min_value=1, max_value=12, value=6)

subjects = []

for i in range(num_subjects):
    with st.sidebar.expander(f"과목 {i+1} 입력"):
        subject = st.text_input(f"{i+1}번 과목명", key=f"sub_{i}")
        material_type = st.radio("자료 종류", ["교과서", "부교재"], key=f"mat_{i}")
        publisher = st.text_input("출판사/교재명", key=f"pub_{i}")
        unit = st.text_input("단원명", key=f"unit_{i}")
        exam_date = st.date_input("시험 날짜", min_value=date.today(), key=f"date_{i}")
        start = st.text_input("범위 시작 (예: p.1, 1번)", key=f"start_{i}")
        end = st.text_input("범위 끝 (예: p.150, 200번)", key=f"end_{i}")

        if subject and start and end:
            subjects.append({
                "과목": subject,
                "자료종류": material_type,
                "출판사": publisher,
                "단원": unit,
                "시험일": exam_date,
                "범위시작": start,
                "범위끝": end
            })

# ==============================
# 계획 생성
# ==============================
if st.sidebar.button("📅 공부 계획 세우기") and subjects:
    today = date.today()
    plan = []

    for s in subjects:
        days_left = (s["시험일"] - today).days
        if days_left <= 0:
            continue

        start_num, end_num, prefix = parse_range(s["범위시작"], s["범위끝"])
        if start_num and end_num:
            total_amount = end_num - start_num + 1
            daily_amount = total_amount // days_left
            if daily_amount == 0: daily_amount = 1

            for d in range(days_left):
                current_date = today + timedelta(days=d)
                part_start = start_num + d * daily_amount
                part_end = part_start + daily_amount - 1
                if d == days_left - 1:  # 마지막 날
                    part_end = end_num

                # 공부 일정
                plan.append({
                    "날짜": current_date,
                    "과목": s["과목"],
                    "자료종류": s["자료종류"],
                    "출판사": s["출판사"],
                    "단원": s["단원"],
                    "범위": f"{prefix}{part_start} ~ {prefix}{part_end}",
                    "종류": "공부",
                    "예상시간(h)": round(daily_hours / num_subjects, 1)
                })

                # 복습 일정
                for offset in [1, 3, 7]:
                    review_date = current_date + timedelta(days=offset)
                    if review_date <= s["시험일"]:
                        plan.append({
                            "날짜": review_date,
                            "과목": s["과목"],
                            "자료종류": s["자료종류"],
                            "출판사": s["출판사"],
                            "단원": s["단원"],
                            "범위": f"{prefix}{part_start} ~ {prefix}{part_end}",
                            "종류": f"복습(D+{offset})",
                            "예상시간(h)": round(daily_hours / num_subjects / 2, 1)
                        })

    # ==============================
    # 결과 정리
    # ==============================
    df = pd.DataFrame(plan).sort_values(["날짜", "과목"]).reset_index(drop=True)

    # 오늘 공부
    st.subheader("📌 오늘 할 공부")
    today_plan = df[df["날짜"] == today]
    if today_plan.empty:
        st.info("오늘은 계획된 공부가 없습니다 😴")
    else:
        done_count = 0
        for i, row in today_plan.iterrows():
            done = st.checkbox(
                f"[{row['과목']} - {row['자료종류']}({row['출판사']}) {row['단원']} - {row['범위']} ({row['종류']})",
                key=f"done_{i}"
            )
            if done:
                st.success("완료 ✅")
                done_count += 1
        st.progress(done_count / len(today_plan))

    # 달력 출력
    st.subheader("📅 달력 계획")
    unique_dates = df["날짜"].unique()
    for d in unique_dates:
        day_tasks = df[df["날짜"] == d]
        st.markdown(f"### {d}")
        for _, t in day_tasks.iterrows():
            if t["자료종류"] == "교과서":
                color = "🔵"
            else:
                color = "🟡"
            if "복습" in t["종류"]:
                color = "🔴"
            st.write(f"{color} {t['과목']} - {t['자료종류']}({t['출판사']}) {t['단원']} - {t['범위']} ({t['종류']})")

    # 전체 계획표
    st.subheader("📖 전체 계획표")
    st.dataframe(df, use_container_width=True)

else:
    st.info("왼쪽에서 과목과 시험 범위를 입력하고 [📅 공부 계획 세우기] 버튼을 눌러주세요.")
