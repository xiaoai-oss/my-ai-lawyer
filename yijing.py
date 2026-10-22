import streamlit as st
import requests
import random
import time
import asyncio
import edge_tts
import os  # 新增：用来判断图片是否存在

st.set_page_config(page_title="AI 周易解卦助手", page_icon="☯️", layout="centered")

# CSS 样式（保持不变）
st.markdown("""
<style>
    .stApp { background-color: #FDF5E6; }
    [data-testid="stSidebar"] { background-color: #F4ECE1; }
    .stButton>button {
        background-color: #8B0000; color: #FDF5E6; border-radius: 4px;
        border: 2px solid #D4AF37; font-family: 'KaiTi', '楷体', serif;
        font-size: 18px; font-weight: bold; letter-spacing: 2px;
        width: 100%; padding: 10px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #A52A2A; color: #FFD700; }
    h1, h2, h3, p { color: #2C3E50; }
</style>
""", unsafe_allow_html=True)

st.title("☯️ AI 周易摇签助手")
st.caption("心诚则灵，摇一摇签筒，让 AI 为你解读签文。")

gua_names = [
    "乾为天", "坤为地", "水雷屯", "山水蒙", "水天需", "天水讼", "地水师", "水地比",
    "风天小畜", "天泽履", "地天泰", "天地否", "天火同人", "火天大有", "地山谦", "雷地豫",
    "泽雷随", "山风蛊", "地泽临", "风地观", "火雷噬嗑", "山火贲", "山地剥", "地雷复",
    "天雷无妄", "山天大畜", "山雷颐", "泽风大过", "坎为水", "离为火", "泽山咸", "雷风恒",
    "天山遁", "雷天大壮", "火地晋", "地火明夷", "风火家人", "火泽睽", "水山蹇", "雷水解",
    "山泽损", "风雷益", "泽天夬", "天风姤", "泽地萃", "地风升", "泽水困", "水风井",
    "泽火革", "火风鼎", "震为雷", "艮为山", "风山渐", "雷泽归妹", "雷火丰", "火山旅",
    "巽为风", "兑为泽", "风水涣", "水泽节", "风泽中孚", "雷山小过", "水火既济", "火水未济"
]

def generate_voice(text, filename="output.mp3"):
    voice = "zh-CN-XiaoxiaoNeural"
    rate = "-10%" 
    async def _generate():
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(filename)
    asyncio.run(_generate())
    return filename

if "gua_result" not in st.session_state:
    st.session_state.gua_result = None
if "ai_reading" not in st.session_state:
    st.session_state.ai_reading = None
if "last_shake_time" not in st.session_state:
    st.session_state.last_shake_time = 0 

with st.sidebar:
    st.header("📜 求签问卜")
    question = st.text_input("默念你的问题（8~15个字）：", placeholder="比如：我最近的财运如何发展？")
    
    if st.button("摇签问卜"):
        q_len = len(question.strip())
        if q_len < 8 or q_len > 15:
            st.warning(f"当前字数 {q_len}。心诚则灵，请控制在 8 到 15 个字。")
        else:
            current_time = time.time()
            if current_time - st.session_state.last_shake_time < 59:
                remaining = int(59 - (current_time - st.session_state.last_shake_time))
                st.error(f"签筒需要静心休息，请等待 {remaining} 秒后再摇。")
            else:
                with st.spinner("签筒摇晃中... 哗啦哗啦..."):
                    time.sleep(1.5) 
                st.session_state.gua_result = {
                    "question": question,
                    "ben_gua": random.choice(gua_names),
                    "bian_gua": random.choice(gua_names),
                    "dong_yao": random.randint(1, 6),
                    "qian_number": random.randint(1, 100)
                }
                st.session_state.ai_reading = None
                st.session_state.last_shake_time = current_time

    # 新增：重置按钮（一键清空，重新开始）
    if st.session_state.gua_result:
        if st.button("🔄 重新摇签"):
            st.session_state.gua_result = None
            st.session_state.ai_reading = None
            st.rerun() # 强制刷新页面状态

if st.session_state.gua_result:
    res = st.session_state.gua_result
    
    st.markdown(f"### 你问的问题是：{res['question']}")
    
    st.markdown(f"""
    <div style="background-color: #FFF8DC; border: 2px solid #D4AF37; border-radius: 12px; padding: 30px 20px; text-align: center; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);">
        <h1 style="color: #8B0000; font-family: 'KaiTi', '楷体', serif; margin: 0; font-size: 42px;">第 {res['qian_number']} 签</h1>
        <div style="width: 50px; height: 2px; background-color: #D4AF37; margin: 15px auto;"></div>
        <h2 style="color: #8B4513; font-family: 'KaiTi', '楷体', serif; margin: 10px 0; font-size: 32px;">{res['ben_gua']}</h2>
        <p style="color: #666; margin-top: 15px; font-size: 14px;">本卦：{res['ben_gua']} ｜ 变卦：{res['bian_gua']} ｜ 动爻：第 {res['dong_yao']} 爻</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.ai_reading is None:
        with st.spinner("AI 道长正在为你解签..."):
            api_key = st.secrets["API_KEY"]
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            prompt = f"你是一位精通周易、说话温和睿智的解签大师。用户的问题：{res['question']}。签文：{res['ben_gua']}，变卦：{res['bian_gua']}，动爻：第 {res['dong_yao']} 爻。请给出300字左右的温暖解读和具体建议，不要说绝对的吉凶。"
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=data)
            st.session_state.ai_reading = response.json()["choices"][0]["message"]["content"]
            
    st.success(st.session_state.ai_reading)
    
    # 新增：语音播放与下载
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔊 听 AI 道长语音"):
            with st.spinner("录制中..."):
                audio_file = generate_voice(st.session_state.ai_reading)
                st.audio(audio_file, format="audio/mp3", autoplay=True)
    with col_b:
        # 下载按钮：把解签结果存成 txt
        st.download_button(
            label="📥 保存解签结果",
            data=f"【你问的问题】\n{res['question']}\n\n【抽到的签】\n第 {res['qian_number']} 签：{res['ben_gua']}\n\n【AI 道长解签】\n{st.session_state.ai_reading}",
            file_name="解签结果.txt",
            mime="text/plain"
        )

    st.write("---") 
    
    # 新增：判断图片是否存在，防止崩溃
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if os.path.exists("pay.png"):
            st.image("pay.png", caption="若解签对你有启发，可扫码随喜结缘 ☕", width=180)
        else:
            st.caption("☕ (随喜二维码准备中...)")

    st.caption("⚠️ 免责声明：本产品仅供娱乐和文化交流，请理性看待。")

else:
    st.info("☯️ 请在左侧默念问题（8~15个字），然后点击“摇签问卜”。")
