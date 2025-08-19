import streamlit as st

# 반드시 가장 먼저 실행
st.set_page_config(page_title="하루 공부 & 복습 계획 짜기", layout="wide")

import pandas as pd
import altair as alt
import random
import math

st.title("📚 하루 공부 & 복습 계획 짜기")

# 과목 목록
subjects = ["생활과윤리", "한국지리", "정치와법", "심화국어",
            "생활과 과학", "국어", "영어", "수학"]

# ---- 사이드바 설정 ----
st.sidebar.header("설정")
total_hours = st.sidebar.number_input("총 공부 시간 (시간)", 1, 24, 8)

st.sidebar.subheader("과목별 비중 (가중치)")
weights = {subj: st.sidebar.slider(f"{subj}", 1, 5, 1) for subj in subjects}
weight_sum = sum(weights.values())

# ---- 오늘 공부 계획 ----
df_today = pd.DataFrame([
    {"과목": s, "공부시간(시간)": round(total_hours * (weights[s]/weight_sum), 2)}
    for s in subjects
])

st.subheader("📋 오늘의 공부 계획")
st.dataframe(df_today, use_container_width=True)

# 오늘 공부 비율 (도넛차트)
pie = (
    alt.Chart(df_today)
    .mark_arc(innerRadius=40)
    .encode(
        theta=alt.Theta("공부시간(시간):Q"),
        color=alt.Color("과목:N"),
        tooltip=["과목", "공부시간(시간)"]
    )
)
st.altair_chart(pie, use_container_width=True)

# ---- 내일 복습 계획 ----
st.subheader("🔄 내일의 복습 계획")

pick_k = max(1, math.floor(len(subjects)/2))  # 과목 절반 선택
subjects_to_review = random.sample(subjects, k=pick_k)

df_review = pd.DataFrame([
    {
        "과목": s,
        "복습시간(시간)": round(
            df_today.loc[df_today["과목"] == s, "공부시간(시간)"].values[0] * 0.5, 2
        )
    }
    for s in subjects_to_review
])

st.dataframe(df_review, use_container_width=True)

# 복습 계획 막대그래프
bar = (
    alt.Chart(df_review)
    .mark_bar()
    .encode(
        x=alt.X("과목:N", sort="-y"),
        y="복습시간(시간):Q",
        tooltip=["과목", "복습시간(시간)"]
    )
)
st.altair_chart(bar, use_container_width=True)
