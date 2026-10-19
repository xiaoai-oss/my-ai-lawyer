import streamlit as st
import requests
import random
import time

# 1. 优化了网页标签图标（太极☯️）和页面布局
st.set_page_config(page_title="AI 周易解卦助手", page_icon="☯️", layout="centered")

# 2. 标题图标改为太极，更贴合易经
st.title("☯️ AI 周易摇签助手")
st.caption("心诚则灵，摇一摇签筒，让 AI 为你解读签文。")

# 64卦名称
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

# 初始化状态
if "gua_result" not in st.session_state:
    st.session_state.gua_result = None
if "ai_reading" not in st.session_state:
    st.session_state.ai_reading = None
if "last_shake_time" not in st.session_state:
    st.session_state.last_shake_time = 0 

# 侧边栏
with st.sidebar:
    # 3. 侧边栏图标改为古书卷轴 📜，更有仪式感
    st.header("📜 求签问卜")
    question = st.text_input("默念你的问题（8~15个字）：", placeholder="比如：我最近的财运如何发展？")
    
    # 4. 按钮图标改为竹签 🎋 或者香 🪔
    if st.button("🎋 摇一摇签筒"):
        # 去除前后空格计算字数
        q_len = len(question.strip())
        
        # 判断字数是否在 8-15 之间
        if q_len < 8 or q_len > 15:
            st.warning(f"当前字数 {q_len}。心诚则灵，问题请控制在 8 到 15 个字之间哦～")
        else:
            # 检查冷却时间（59秒）
            current_time = time.time()
            time_passed = current_time - st.session_state.last_shake_time
            
            if time_passed < 59:
                remaining = int(59 - time_passed)
                st.error(f"签筒需要静心休息，请等待 {remaining} 秒后再摇。")
            else:
                # 满足条件，开始摇签
                with st.spinner("签筒摇晃中... 哗啦哗啦..."):
                    time.sleep(1.5) 
                    
                ben_gua = random.choice(gua_names)
                bian_gua = random.choice(gua_names)
                dong_yao = random.randint(1, 6)
                qian_number = random.randint(1, 100)
                
                st.session_state.gua_result = {
                    "question": question,
                    "ben_gua": ben_gua,
                    "bian_gua": bian_gua,
                    "dong_yao": dong_yao,
                    "qian_number": qian_number
                }
                st.session_state.ai_reading = None
                st.session_state.last_shake_time = current_time

# 主界面
if st.session_state.gua_result:
    res = st.session_state.gua_result
    
    st.markdown(f"### 你问的问题是：{res['question']}")
    
    # 签文卡片展示
    st.markdown(f"""
    <div style="background-color: #FFF8DC; border: 2px solid #D2B48C; border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h1 style="color: #8B0000; font-family: 'KaiTi', '楷体', serif; margin: 0;">第 {res['qian_number']} 签</h1>
        <h2 style="color: #8B4513; font-family: 'KaiTi', '楷体', serif; margin: 10px 0;">{res['ben_gua']}</h2>
        <p style="color: #555; margin: 0;">本卦：{res['ben_gua']} ｜ 变卦：{res['bian_gua']} ｜ 动爻：第 {res['dong_yao']} 爻</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI 解签
    if st.session_state.ai_reading is None:
        with st.spinner("AI 道长正在为你解签..."):
            api_key = st.secrets["API_KEY"]
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            prompt = f"""
            你是一位精通周易、说话温和睿智的解签大师。请为用户解读以下签文。
            用户的问题：{res['question']}
            抽到的签文（本卦）：{res['ben_gua']}
            变卦：{res['bian_gua']}
            动爻：第 {res['dong_yao']} 爻
            
            请给出解读，要求：
            1. 语气要温暖、积极，提供情绪价值。
            2. 结合签文的本意，给出现实生活中（如工作、感情、生活）的具体建议。
            3. 不要说绝对的“吉”或“凶”，而是强调人自身的努力和心态。
            4. 字数控制在 300 字左右。
            """
            
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]
            
            st.session_state.ai_reading = reply
            
    st.success(st.session_state.ai_reading)
    st.caption("⚠️ 免责声明：本产品仅供娱乐和文化交流，请理性看待。")

else:
    st.info("☯️ 请在左侧默念问题（8~15个字），然后点击“摇一摇签筒”。")
