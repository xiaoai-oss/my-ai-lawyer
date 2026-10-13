import streamlit as st
import requests

st.set_page_config(page_title="我的AI法律顾问", page_icon="⚖️")

st.title("⚖️ 我的AI法律顾问")
st.write("你好！我是你的私人法律助手，请根据我提供的法律文件提问。")

# 从文件读取法律资料
with open("YHNGF.txt", "r", encoding="utf-8") as f:
    file_content = f.read()

# 把聊天记录存在网页的“记忆”里
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 网页底部的输入框
question = st.chat_input("请输入你的法律问题：")

if question:
    # 显示你的问题
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # 调用 AI
    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    prompt = f"请根据以下资料回答问题：\n{file_content}\n\n问题：{question}"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(url, headers=headers, json=data)
    reply = response.json()["choices"][0]["message"]["content"]

    # 显示 AI 的回答
    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})