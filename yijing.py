import streamlit as st
import requests
import random

st.set_page_config(page_title="AI 周易解卦助手", page_icon="☯️", layout="wide")
st.title("☯️ AI 周易解卦助手")
st.caption("心诚则灵，点击起卦，让 AI 为你解读当下的困惑。")

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
    st.header("🔮 摇卦")
    question = st.text_input("默念你的问题（比如：我最近的事业运势如何？）：")
    
    if st.button("开始起卦"):
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

if st.session_state.gua_result:
    res = st.session_state.gua_result
    st.subheader(f"你问的问题是：{res['question']}")
    st.info(f"**本卦**：{res['ben_gua']}　|　**变卦**：{res['bian_gua']}　|　**动爻**：第 {res['dong_yao']} 爻")
    
    if st.session_state.ai_reading is None:
        with st.spinner("AI 道长正在为你解卦..."):
            api_key = st.secrets["API_KEY"]
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            prompt = f"""
            你是一位精通周易、说话温和睿智的解卦大师。请为用户解读以下卦象。
            用户的问题：{res['question']}
            本卦：{res['ben_gua']}
            变卦：{res['bian_gua']}
            动爻：第 {res['dong_yao']} 爻
            
            请给出解读，要求：
            1. 语气要温暖、积极，提供情绪价值。
            2. 结合卦象的本意，给出现实生活中（如工作、感情、生活）的具体建议。
            3. 不要说绝对的“吉”或“凶”，而是强调人自身的努力和心态。
            4. 字数控制在 300 字左右。
            """
            
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]
            
            st.session_state.ai_reading = reply
            
    st.markdown("### 📜 AI 解卦：")
    st.success(st.session_state.ai_reading)
    st.caption("⚠️ 免责声明：本产品仅供娱乐和文化交流，请理性看待。")
else:
    st.write("👈 请在左侧输入你的问题，然后点击“开始起卦”。")
