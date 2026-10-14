import streamlit as st
import requests

st.set_page_config(page_title="我的AI法律顾问", page_icon="⚖️")
st.title("⚖️ 我的AI法律顾问")

# 侧边栏：上传文件
with st.sidebar:
    st.header("上传法律文件")
    uploaded_file = st.file_uploader("选择 .txt 文件", type="txt")
    
    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        st.success("文件已加载！")
    else:
        with open("YHNGF.txt", "r", encoding="utf-8") as f:
            file_content = f.read()
        st.info("当前使用默认文件")

# 聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("请输入你的法律问题：")

if question:
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    prompt = f"请根据以下资料回答问题：\n{file_content}\n\n问题：{question}"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(url, headers=headers, json=data)
    reply = response.json()["choices"][0]["message"]["content"]

    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
