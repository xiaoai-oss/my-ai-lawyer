import streamlit as st
import requests

st.set_page_config(page_title="AI 短剧分镜大师", page_icon="🎬", layout="wide")

st.title("🎬 AI 短剧分镜提示词生成器")
st.caption("输入你的小说/剧本片段，一键生成用于【即梦/可灵/剪映】的英文画面提示词。")

# 侧边栏设置
with st.sidebar:
    st.header("🎨 视觉风格设定")
    style = st.selectbox(
        "选择视频画风",
        ["赛博朋克风 (Cyberpunk)", "古风仙侠 (Chinese Xianxia)", "现代都市写实 (Realistic)", "皮克斯 3D 动画风 (Pixar 3D)", "暗黑哥特风 (Dark Gothic)"]
    )
    
    st.markdown("---")
    st.info("💡 提示：生成的英文提示词，直接复制到即梦、Midjourney 或可灵中即可生成图片。")

# 主界面：剧本输入
script_text = st.text_area("粘贴你的剧本片段（建议 100-300 字）：", height=200, placeholder="比如：外卖小哥走到别墅门口，被保安拦住嘲笑。小哥冷笑一声，直接掏出全球限量版黑卡，保安瞬间跪地...")

if st.button("✨ 一键生成分镜和提示词", type="primary"):
    if not script_text.strip():
        st.warning("请先粘贴剧本内容哦！")
    else:
        with st.spinner("AI 导演正在构思画面..."):
            api_key = st.secrets["API_KEY"]
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            prompt = f"""
            你是一位顶级的 AI 短剧导演和分镜师。
            画风设定：{style}
            剧本内容：{script_text}
            
            请根据剧本，拆解出 3 到 4 个最核心的分镜。严格按照以下格式输出每一个分镜：
            
            🎬 【分镜 X】
            - 【画面描述】：(用简短的中文描述这一镜发生了什么)
            - 【英文提示词】：(极其详细的英文生图提示词，必须包含：镜头景别(如Close-up, Wide shot)、画面主体、动作、环境光影、画质词(如8k, highly detailed)。不同词组用逗号隔开。)
            - 【配音/台词】：(这一镜的台词或旁白)
            
            不要输出多余的废话，直接给我分镜表。
            """
            
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]
            
            st.success("🎉 分镜生成完毕！你可以直接复制英文提示词去生成画面。")
            
            # 将生成的内容用好看的框展示出来
            st.markdown(reply)

st.markdown("---")
st.caption("🎬 创作流程：用本工具生成提示词 -> 去【即梦/可灵】生成画面 -> 去【剪映】配音加字幕。")
