import streamlit as st
import requests
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="我的AI法律顾问", page_icon="⚖️", layout="wide")

st.title("⚖️ 我的AI法律顾问")
st.caption("上传法律文件，然后问我任何问题。")

# 把长文件切成小段
def split_text(text, chunk_size=800):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

with st.sidebar:
    st.header("📂 上传文件")
    uploaded_file = st.file_uploader("选择 .txt / .pdf / .docx 文件", type=["txt", "pdf", "docx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            file_content = ""
            for page in reader.pages:
                file_content += page.extract_text()
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            file_content = ""
            for para in doc.paragraphs:
                file_content += para.text + "\n"
        else:
            file_content = uploaded_file.read().decode("utf-8")
        st.success("✅ 文件已加载！")
    else:
        with open("YHNGF.txt", "r", encoding="utf-8") as f:
            file_content = f.read()
        st.info("📌 当前使用默认文件")

    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("请输入你的问题：")

if question:
    with st.chat_message("user"):
        st.write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 把文件切成小段
    chunks = split_text(file_content, 800)
    
    # 找出跟问题最相关的几段
    relevant_chunks = []
    for chunk in chunks:
        if any(word in chunk for word in question.split()):
            relevant_chunks.append(chunk)
    
    # 如果没找到相关段落，就用前几段
    if not relevant_chunks:
        relevant_chunks = chunks[:3]
    else:
        relevant_chunks = relevant_chunks[:3]
    
    # 把找到的段落拼起来
    context = "\n\n".join(relevant_chunks)

    prompt = f"请根据以下资料回答问题：\n{context}\n\n问题：{question}"
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(url, headers=headers, json=data)
    reply = response.json()["choices"][0]["message"]["content"]

    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
