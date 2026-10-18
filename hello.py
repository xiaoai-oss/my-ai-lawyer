import streamlit as st
import requests
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="我的数学数据分析器", page_icon="📊", layout="wide")
st.title("📊 我的数学数据分析器")
st.caption("微积分、数据拟合、函数作图、数字规律分析。")

with st.sidebar:
    st.header("🧮 微积分与作图")
    expr = st.text_input("输入函数（比如 x**2 + 3*x）：")
    
    if st.button("求导"):
        try:
            x = sp.Symbol("x")
            f = sp.sympify(expr)
            st.success(f"导数：{sp.diff(f, x)}")
        except Exception as e:
            st.error(f"出错了：{e}")
            
    if st.button("作图"):
        try:
            x = sp.Symbol("x")
            f = sp.sympify(expr)
            # 把 sympy 函数转成 numpy 能用的函数
            f_num = sp.lambdify(x, f, "numpy")
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f_num(x_vals)
            
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.axhline(0, color='black', linewidth=0.5)
            ax.axvline(0, color='black', linewidth=0.5)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"出错了：{e}")

    st.header("📈 数据拟合")
    data_input = st.text_area("输入数据点，每行一个（x,y）：")
    
    if st.button("拟合曲线"):
        try:
            lines = [line.strip() for line in data_input.strip().split("\n") if line.strip()]
            x_vals = []
            y_vals = []
            for line in lines:
                parts = line.split(",")
                x_vals.append(float(parts[0]))
                y_vals.append(float(parts[1]))
            
            coeffs = np.polyfit(x_vals, y_vals, 2)
            poly = np.poly1d(coeffs)
            
            # 画原始散点和拟合曲线
            fig, ax = plt.subplots()
            ax.scatter(x_vals, y_vals, color='red', label='原始数据')
            
            x_line = np.linspace(min(x_vals), max(x_vals), 100)
            ax.plot(x_line, poly(x_line), color='blue', label='拟合曲线')
            ax.legend()
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"出错了：{e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("请输入你的数学问题：")

if question:
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    prompt = f"你是一位数学老师。请解答数学问题，或分析数字规律。\n\n用户输入：{question}"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(url, headers=headers, json=data)
    reply = response.json()["choices"][0]["message"]["content"]

    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
