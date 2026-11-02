import streamlit as st
import requests
import json
import random

st.set_page_config(page_title="AI 书法大师", page_icon="🖌️", layout="centered")

# 👇 注入水墨古风 CSS 👇
st.markdown("""
<style>
    .stApp { background-color: #FDF9F1; } /* 宣纸米白底色 */
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    h1 { color: #2C3E50 !important; font-family: 'KaiTi', '楷体', serif; text-align: center; }
    p, label { color: #4A4A4A !important; font-family: 'KaiTi', '楷体', serif; }
    .stChatMessage { background-color: #FFFFFF !important; border-left: 5px solid #8B0000 !important; border-radius: 5px; }
    .stTextInput input { background-color: #FFFFFF !important; border: 1px solid #D3CBB8 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🖌️ AI 书法大师")
st.caption("研墨、铺纸、提笔。跟大师聊聊书法，或者让它给你出个题。")

# ================= 1. 书法大师的知识库与专属工具 =================
# 咱们把五大书体的知识塞进字典里
CALLIGRAPHY_KNOWLEDGE = {
    "篆书": "篆书分为大篆和小篆。特点是字形修长，线条圆润均匀，古朴典雅。代表人物：李斯（小篆鼻祖）。",
    "隶书": "隶书起源于秦代，盛于汉代。特点是字形扁平，讲究'蚕头燕尾'、'一波三折'。代表人物：蔡邕。",
    "楷书": "楷书又称正书，是现在通行的汉字手写正体字。特点是横平竖直，规矩严整。代表人物：颜真卿、柳公权、欧阳询、赵孟頫。",
    "行书": "行书介于楷书和草书之间。特点是既流畅又易辨认。天下第一行书是王羲之的《兰亭序》。",
    "草书": "草书为了书写便捷而产生。特点是结构简省、笔画连绵。代表人物：张旭、怀素（狂草）。"
}

def get_calligraphy_knowledge(style_name):
    """查询五大书体的百科知识"""
    # 简单匹配，如果用户输入“行”，也能匹配到“行书”
    for k, v in CALLIGRAPHY_KNOWLEDGE.items():
        if style_name in k or k in style_name:
            return f"关于【{k}】：{v}"
    return "暂无该书法流派的详细资料。"

def get_calligraphy_styles(word):
    """查询某个字的书写建议"""
    styles = list(CALLIGRAPHY_KNOWLEDGE.keys())
    random_style = random.choice(styles)
    return f"已调取《历代书法字典》：关于“{word}”字，建议参考它在【{random_style}】中的经典写法。请平心静气，悬腕书写。"

def random_practice_char():
    """随机抽取练习字"""
    chars = ["永", "和", "龙", "福", "静", "道", "禅", "悟", "云", "鹤"]
    selected = random.choice(chars)
    return f"抽签结果：今日宜练“{selected}”字。此字结构精妙，请悬腕书写。"

# ================= 2. 将工具打包告诉大模型 =================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_calligraphy_knowledge",
            "description": "查询中国书法五大书体（篆、隶、楷、行、草）的详细介绍、特点和代表人物",
            "parameters": {
                "type": "object",
                "properties": {"style_name": {"type": "string", "description": "书体名称，例如：楷书、行书、草书"}},
                "required": ["style_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calligraphy_styles",
            "description": "查询某个特定汉字的书法写法建议",
            "parameters": {
                "type": "object",
                "properties": {"word": {"type": "string", "description": "要查询的单个汉字"}},
                "required": ["word"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "random_practice_char",
            "description": "当用户不知道练什么字，让你推荐时调用",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ================= 3. 聊天界面 =================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "阿弥陀佛。我是书法大师，今日想请教哪幅字？想了解五大书体，还是让我为你抽个字练练手？"}
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
    
    # 给大师注入灵魂提示词
    system_prompt = "你是一位精通中国传统书法的大师，说话温文尔雅，带点古风。当用户询问篆、隶、楷、行、草等书体知识时，必须调用 get_calligraphy_knowledge 工具。当用户问某个字怎么写时，调用 get_calligraphy_styles 工具。当用户求字时，调用 random_practice_char。"
    messages_with_system = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    
    data = {"model": "deepseek-chat", "messages": messages_with_system, "tools": tools}
    
    with st.spinner("大师正在提笔..."):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30).json()
            response_message = response["choices"][0]["message"]
            tool_calls = response_message.get("tool_calls")
            
            if tool_calls:
                st.session_state.messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    if function_name == "get_calligraphy_knowledge":
                        st.info(f"📖 大师正在翻阅典籍，查阅【{function_args.get('style_name')}】...")
                        function_response = get_calligraphy_knowledge(function_args.get("style_name"))
                    elif function_name == "get_calligraphy_styles":
                        st.info(f"🔍 大师正在查阅【{function_args.get('word')}】字的写法...")
                        function_response = get_calligraphy_styles(function_args.get("word"))
                    elif function_name == "random_practice_char":
                        st.info("🎲 大师正在为你随机抽取练习字...")
                        function_response = random_practice_char()
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
                    st.session_state.messages.append({"role": "assistant", "content": final_reply})
            else:
                reply = response_message["content"]
                with st.chat_message("assistant"):
                    st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
        except Exception as e:
            st.error(f"笔尖卡住了，请稍后再试。错误信息：{e}")