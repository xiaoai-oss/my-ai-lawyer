    import streamlit as st
import requests
import json
import random
import asyncio
import edge_tts
import re

st.set_page_config(page_title="AI 书法大师", page_icon="🖌️", layout="centered")

# 👇 注入水墨古风 CSS 👇
st.markdown("""
<style>
    .stApp { background-color: #FDF9F1; } 
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    h1 { color: #2C3E50 !important; font-family: 'KaiTi', '楷体', serif; text-align: center; }
    p, label { color: #4A4A4A !important; font-family: 'KaiTi', '楷体', serif; }
    .stChatMessage { background-color: #FFFFFF !important; border-left: 5px solid #8B0000 !important; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🖌️ AI 书法大师")
st.caption("研墨、铺纸、提笔。跟大师聊聊书法，或者让它给你出个题。")

# 👇 语音生成函数（带 Markdown 符号清洗功能） 👇
def generate_voice(text, filename="shufa_voice.mp3"):
    clean_text = re.sub(r'[*#`~_>]', '', text)
    voice = "zh-CN-YunjianNeural"
    rate = "-15%" 
    async def _generate():
        communicate = edge_tts.Communicate(clean_text, voice, rate=rate)
        await communicate.save(filename)
    asyncio.run(_generate())
    return filename

# ================= 1. 知识库与工具 =================
CALLIGRAPHY_KNOWLEDGE = {
    "篆书": "篆书分为大篆和小篆。特点是字形修长，线条圆润均匀。代表人物：李斯。",
    "隶书": "隶书字形扁平，讲究'蚕头燕尾'。代表人物：蔡邕。",
    "楷书": "楷书横平竖直，规矩严整。代表人物：颜真卿、柳公权。",
    "行书": "行书介于楷草之间，流畅易认。王羲之的《兰亭序》是天下第一行书。",
    "草书": "草书结构简省、笔画连绵。代表人物：张旭、怀素。"
}

def get_calligraphy_knowledge(style_name):
    for k, v in CALLIGRAPHY_KNOWLEDGE.items():
        if style_name in k or k in style_name:
            return f"关于【{k}】：{v}"
    return "暂无该书法流派的详细资料。"

def get_calligraphy_styles(word):
    return f"关于“{word}”字，建议参考历代名家的经典碑帖。请平心静气，悬腕书写。"

def random_practice_char():
    chars = ["永", "和", "龙", "福", "静", "道", "禅", "悟", "云", "鹤"]
    return random.choice(chars)

# ================= 2. 工具打包 =================
tools = [
    {"type": "function", "function": {"name": "get_calligraphy_knowledge", "description": "查询书体知识", "parameters": {"type": "object", "properties": {"style_name": {"type": "string"}}, "required": ["style_name"]}}},
    {"type": "function", "function": {"name": "get_calligraphy_styles", "description": "查询汉字写法", "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}}},
    {"type": "function", "function": {"name": "random_practice_char", "description": "随机抽字", "parameters": {"type": "object", "properties": {}}}}
]

# ================= 3. 展示书法真迹（已改为横排） =================
def show_calligraphy_art(text, style="楷书"):
    font_map = {
        "楷书": "'KaiTi', '楷体', serif",
        "行书": "'STXingkai', '华文行楷', cursive",
        "草书": "'STXingkai', '华文行楷', cursive",
        "隶书": "'LiSu', '隶书', serif",
        "篆书": "'KaiTi', '楷体', serif"
    }
    font_family = font_map.get(style, "'KaiTi', '楷体', serif")
    
    # 字号调整，横排可以稍微大一点，并加上字间距 (letter-spacing)
    font_size = "90px" if len(text) <= 2 else "70px" if len(text) <= 4 else "50px"
    
    # 💡 核心修改：去掉了 vertical-rl，改为横排，并加上了 letter-spacing 增加字间距
    html = f'<div style="background-color: #F9F6EE; border: 2px solid #D3CBB8; border-radius: 8px; padding: 40px 20px; text-align: center; margin: 20px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.1); position: relative; min-height: 300px; display: flex; align-items: center; justify-content: center;"><div style="font-family: {font_family}; font-size: {font_size}; color: #1A1A1A; line-height: 1.2; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); letter-spacing: 15px; margin-right: -15px;">{text}</div><div style="position: absolute; bottom: 30px; right: 30px; width: 60px; height: 60px; border: 3px solid #B22222; color: #B22222; font-family: \'KaiTi\', \'楷体\', serif; font-size: 16px; font-weight: bold; display: flex; flex-wrap: wrap; align-content: center; justify-content: center; transform: rotate(-5deg); border-radius: 4px; line-height: 1;"><div style="width: 50%; text-align: center;">劉</div><div style="width: 50%; text-align: center;">志</div><div style="width: 50%; text-align: center;">強</div><div style="width: 50%; text-align: center;">印</div></div></div>'
    
    st.markdown(html, unsafe_allow_html=True)

# ================= 4. 五体书展 =================
with st.expander("📜 点击展开：五体书展（选择书体看效果）", expanded=False):
    demo_style = st.selectbox("选择书体", ["篆书", "隶书", "楷书", "行书", "草书"])
    demo_text = st.text_input("输入想写的字（建议4个字以内）", value="天道酬勤")
    if st.button("✨ 立刻展示作品"):
        st.session_state.show_demo = (demo_text, demo_style)

if "show_demo" in st.session_state:
    st.subheader(f"✨ {st.session_state.show_demo[1]} 作品展示")
    show_calligraphy_art(st.session_state.show_demo[0], st.session_state.show_demo[1])
    st.write("---")

# ================= 5. 聊天界面与 Agent 逻辑 =================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "阿弥陀佛。我是书法大师。今日想请教哪幅字？想了解五大书体，还是让我为你抽个字练练手？"}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "tool" and msg["role"] != "system" and (msg["role"] != "assistant" or not msg.get("tool_calls")):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

if prompt := st.chat_input("与大师对话..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = "你是一位精通中国传统书法的大师。当用户询问书体知识时，调用 get_calligraphy_knowledge。当用户问某个字怎么写时，调用 get_calligraphy_styles。当用户求字时，调用 random_practice_char。"
    messages_with_system = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    
    data = {"model": "deepseek-chat", "messages": messages_with_system, "tools": tools}
    
    with st.spinner("大师正在提笔..."):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30).json()
            response_message = response["choices"][0]["message"]
            tool_calls = response_message.get("tool_calls")
            
            if tool_calls:
                st.session_state.messages.append(response_message)
                char_to_display = None 
                style_to_display = "楷书"
                
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    if function_name == "get_calligraphy_knowledge":
                        st.info(f"📖 大师正在翻阅典籍，查阅【{function_args.get('style_name')}】...")
                        function_response = get_calligraphy_knowledge(function_args.get("style_name"))
                        style_to_display = function_args.get("style_name")
                    elif function_name == "get_calligraphy_styles":
                        st.info(f"🔍 大师正在查阅【{function_args.get('word')}】字的写法...")
                        function_response = get_calligraphy_styles(function_args.get("word"))
                        char_to_display = function_args.get("word")
                    elif function_name == "random_practice_char":
                        st.info("🎲 大师正在为你随机抽取练习字...")
                        char_result = random_practice_char()
                        function_response = f"抽签结果：今日宜练“{char_result}”字。"
                        char_to_display = char_result
                    else:
                        function_response = "未知工具"
                    
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": str(function_response)
                    })
                
                with st.spinner("大师正在挥毫泼墨..."):
                    data2 = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}] + st.session_state.messages}
                    final_response = requests.post(url, headers=headers, json=data2, timeout=30).json()
                    final_reply = final_response["choices"][0]["message"]["content"]
                    
                    with st.chat_message("assistant"):
                        st.write(final_reply)
                        if char_to_display:
                            show_calligraphy_art(char_to_display, style_to_display)
                        
                        with st.spinner("大师正在清清嗓子..."):
                            audio_file = generate_voice(final_reply)
                            st.audio(audio_file, format="audio/mp3", autoplay=True)
                            
                    st.session_state.messages.append({"role": "assistant", "content": final_reply})
            else:
                reply = response_message["content"]
                with st.chat_message("assistant"):
                    st.write(reply)
                    with st.spinner("大师正在清清嗓子..."):
                        audio_file = generate_voice(reply)
                        st.audio(audio_file, format="audio/mp3", autoplay=True)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
        except Exception as e:
            st.error(f"笔尖卡住了，请稍后再试。错误信息：{e}")
