import streamlit as st
import requests
import asyncio
import edge_tts
import re

# 1. 页面配置
st.set_page_config(page_title="AI 短剧分镜大师", page_icon="🎬", layout="centered")

# 2. 👇 最新版“终极隐藏” CSS（干掉右上角 Fork 和右下角红条）👇
hide_st_style = """
            <style>
            /* 隐藏顶部工具栏（Fork, GitHub, 菜单） */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            [data-testid="stDecoration"] {visibility: hidden !important;}
            header {visibility: hidden !important;}
            
            /* 隐藏右下角红条水印和底部管理按钮 */
            [data-testid="stStatusWidget"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            [data-testid="stFooter"] {visibility: hidden !important;}
            
            /* 隐藏主菜单 */
            #MainMenu {visibility: hidden !important;}
            
            /* 减少顶部空白 */
            [data-testid="stAppViewContainer"] > .main { padding-top: 2rem !important; }
            
            /* 手机端按钮铺满 */
            .stButton>button { width: 100% !important; }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. 页面标题
st.title("🎬 AI 短剧分镜大师")
st.caption("输入剧本，一键生成电影级英文提示词与配音。")

# 4. 语音生成函数
def generate_voice(text, voice_name="zh-CN-YunjianNeural", filename="drama_voice.mp3"):
    async def _generate():
        communicate = edge_tts.Communicate(text, voice_name, rate="+10%")
        await communicate.save(filename)
    asyncio.run(_generate())
    return filename

# 5. 主界面操作区
style = st.selectbox(
    "选择视频画风",
    ["赛博朋克风 (Cyberpunk)", "古风仙侠 (Chinese Xianxia)", "现代都市写实 (Realistic)", "皮克斯 3D 动画风 (Pixar 3D)", "暗黑哥特风 (Dark Gothic)"]
)

script_text = st.text_area(
    "粘贴你的剧本片段：", 
    height=120, 
    placeholder="比如：外卖小哥走到别墅门口，被保安拦住嘲笑。小哥冷笑一声，直接掏出全球限量版黑卡..."
)

if st.button("✨ 一键生成分镜和配音", type="primary", use_container_width=True):
    if not script_text.strip():
        st.warning("请先粘贴剧本内容哦！")
    else:
        with st.spinner("AI 导演正在构思画面并配音..."):
            api_key = st.secrets["API_KEY"]
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            prompt = f"""
            你是一位顶级的 AI 短剧导演。画风设定：{style}。剧本内容：{script_text}。
            请拆解出 3 个核心分镜。严格按照以下格式输出：
            🎬 【分镜 X】
            - 【画面描述】：简短中文描述。
            - 【英文提示词】：英文生图提示词（包含景别、光影、画质词，用逗号隔开）。
            - 【配音/台词】：这一镜的台词。
            """
            
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]
            
            st.success("🎉 生成完毕！提示词可直接复制。")
            st.markdown(reply)
            st.write("---")
            
            # 提取台词并配音
            with st.spinner("正在提取台词并配音..."):
                try:
                    dialogue_matches = re.findall(r"【配音/台词】：(.*)", reply)
                    if dialogue_matches:
                        full_dialogue = "。".join([d.strip() for d in dialogue_matches])
                        audio_file = generate_voice(full_dialogue)
                        st.write("🔊 **短剧原声配音（可下载）：**")
                        st.audio(audio_file, format="audio/mp3", autoplay=True)
                    else:
                        st.info("没有在分镜中检测到明显的台词，不生成配音。")
                except Exception as e:
                    st.error(f"配音生成失败：{e}")

st.caption("🎬 创作流程：生成提示词 -> 即梦/可灵出图 -> 剪映合成。")
