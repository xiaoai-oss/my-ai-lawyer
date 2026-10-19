import streamlit as st
import requests
import random
import time

st.set_page_config(page_title="AI 周易摇签助手", page_icon="🎋", layout="wide")

# 自定义 CSS 样式，画签筒和签子
st.markdown("""
<style>
    .qian-tong {
        width: 120px;
        height: 160px;
        background-color: #8B4513;
        border-radius: 10px 10px 50px 50px;
        margin: 0 auto;
        position: relative;
        box-shadow: inset -10px 0 20px rgba(0,0,0,0.5), 5px 5px 15px rgba(0,0,0,0.3);
    }
    .qian-zi {
        width: 30px;
        height: 200px;
        background-color: #F5DEB3;
        border: 2px solid #D2B48C;
        border-radius: 5px;
        position: absolute;
        left: 45px;
        bottom: 120px;
        text-align: center;
        writing-mode: vertical-rl;
        text-orientation: upright;
        font-weight: bold;
        font-size: 18px;
        color: #8B0000;
        padding: 10px 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        animation: pop-out 0.8s ease-out forwards;
    }
    @keyframes pop-out {
        0% { transform: translateY(0); opacity: 0; }
        100% { transform: translateY(-60px); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

st.title("🎋 AI 周易摇签助手")
st.caption("心诚则灵，点击摇签筒，让 AI 为你解读签文。")

# 64卦的名称列表
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

if "gua_result" not in st.session_state:
    st.session_state.gua_result = None
if "ai_reading" not in st.session_state:
    st.session_state.ai_reading = None

with st.sidebar:
    st.header("🔮 摇签")
    question = st.text_input("默念你的问题（比如：我最近的事业运势如何？）：")
    
    # 按钮改成了摇签
    if st.button("🎋 摇一摇签筒"):
        if not question:
            st.warning("请先在左侧输入你想问的问题哦！")
        else:
            ben_gua = random.choice(gua_names)
            bian_gua = random.choice(gua_names)
            dong_yao = random.randint(1, 6)
            
            st.session_state.gua_result = {
                "question": question,
                "ben_gua": ben_gua,
                "bian_gua": bian_gua,
                "dong_yao": dong_yao
            }
            st.session_state.ai_reading = None

# 主界面
if st.session_state.gua_result:
    res = st.session_state.gua_result
    st.subheader(f"你问的问题是：{res['question']}")
    
    # 渲染签筒和签子的 HTML
    st.markdown(f"""
    <div style="position: relative; height: 250px; display: flex; justify-content: center;">
        <div class="qian-tong"></div>
        <div class="qian-zi">第{random.randint(1,100)}签<br>{res['ben_gua']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"**本卦**：{res['ben_gua']}　|　**变卦**：{res['bian_gua']}　|　**动爻**：第 {res['dong_yao']} 爻")
    
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
            
    st.markdown("### 📜 AI 解签：")
    st.success(st.session_state.ai_reading)
    st.caption("⚠️ 免责声明：本产品仅供娱乐和文化交流，请理性看待。")
else:
    st.write("👈 请在左侧输入你的问题，然后点击“摇一摇签筒”。")
