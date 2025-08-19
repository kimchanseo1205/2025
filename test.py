import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.set_page_config(page_title="하루 공부 계획 앱", layout="wide")

st.title("📚 하루 공부 & 복습 계획 짜기")

# 과목 목록
subjects = ["생활과윤리", "한국지리", "정치와법", "심화국어", 
            "생활과 과학", "국어", "영어", "수학"]

st.sidebar.header("설정")
total_hours = st.sidebar.number_input("총 공부 시간 (시간)", 1, 24, 8)

# 과목별 비중 설정
st.sidebar.subheader("과목별 비중 (가중치)")
weights = {}
for subj in subjects:
    weights[subj] = st.sidebar.slider(f"{subj}", 1, 5, 1)

# 가중치 합
weight_sum = sum(weights.values())

# 오늘 공부 계획
study_plan = []
for subj in subjects:
    hours = round(total_hours * (weights[subj] / weight_sum), 2)
    study_plan.append({"과목": subj, "공부시간(시간)": hours})

df_today = pd.DataFrame(study_plan)

# 오늘 공부 계획 출력
st.subheader("📋 오늘의 공부 계획")
st.dataframe(df_today, use_container_width=True)

# 그래프 시각화
fig = px.pie(df_today, values="공부시간(시간)", names="과목", title="오늘 공부 비율")
st.plotly_chart(fig, use_container_width=True)

# 내일 복습 계획 생성
st.subheader("🔄 내일의 복습 계획")

# 오늘 공부한 과목 중 랜덤 50% 선택
subjects_to_review = random.sample(subjects, k=len(subjects)//2)

review_plan = []
for subj in subjects_to_review:
    today_hours = df_today.loc[df_today["과목"] == subj, "공부시간(시간)"].values[0]
    review_plan.append({"과목": subj, "복습시간(시간)": round(today_hours * 0.5, 2)})

df_review = pd.DataFrame(review_plan)

st.dataframe(df_review, use_container_width=True)

# 복습 그래프
fig2 = px.bar(df_review, x="과목", y="복습시간(시간)", title="내일 복습 분량")
st.plotly_chart(fig2, use_container_width=True)

