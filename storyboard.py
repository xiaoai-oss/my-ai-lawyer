import streamlit as st
import requests
import asyncio
import edge_tts
import re
# 👇 必须引入这个组件用于执行 JS 👇
import streamlit.components.v1 as components

# 1. 页面配置
st.set_page_config(
    page_title="AI 短剧分镜大师", 
    page_icon="🎬", 
    layout="centered", 
    menu_items={}
)

# 2. 传统 CSS 隐藏（尽量隐藏头部）
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden !important;}
            header {visibility: hidden !important;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            [data-testid="stDecoration"] {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. 👇 JS 物理删除大招（干掉红条）👇
components.html(
    """
    <script>
    // 延迟 1 秒执行，确保页面加载完毕
    setTimeout(function() {
        // 穿透到最外层的父级网页
        var parentDoc = window.parent.document;
        
        // 找到所有包含 Streamlit 标识的元素
        var badges = parentDoc.querySelectorAll('[data-testid="stStatusWidget"]');
        badges.forEach(function(badge) {
            badge.style.display = 'none';
            badge.remove(); // 直接从代码里物理删除
        });
        
        var footers = parentDoc.querySelectorAll('footer');
        footers.forEach(function(footer) {
            footer.style.display = 'none';
            footer.remove();
        });

        // 强行隐藏右上角
        var toolbars = parentDoc.querySelectorAll('[data-testid="stToolbar"]');
        toolbars.forEach(function(toolbar) {
            toolbar.style.display = 'none';
        });
    }, 1000);
    </script>
    """,
    height=0,
    width=0
)

# 4. 页面标题
st.title("🎬 AI 短剧分镜大师")
st.caption("输入剧本，一键生成电影级英文提示词与配音。")

# 5. 语音生成函数
def generate_voice(text, voice_name="zh-CN-YunjianNeural", filename="drama_voice.mp3"):
    async def _generate():
        communicate = edge_tts.Communicate(text, voice_name, rate="+10%")
        await communicate.save(filename)
    asyncio.run(_generate())
    return filename

# 6. 主界面操作区
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
