import streamlit as st
import requests
import asyncio
import edge_tts
import re  # 用于正则提取台词

st.set_page_config(page_title="AI 短剧分镜大师", page_icon="🎬", layout="wide")

st.title("🎬 AI 短剧分镜提示词生成器")
st.caption("输入你的小说/剧本片段，一键生成用于【即梦/可灵/剪映】的英文画面提示词，并自动配音。")

# --- 语音生成函数 ---
def generate_voice(text, voice_name="zh-CN-YunjianNeural", filename="drama_voice.mp3"):
    async def _generate():
        # 语速稍微快一点点，更有短剧的节奏感
        communicate = edge_tts.Communicate(text, voice_name, rate="+10%")
        await communicate.save(filename)
    asyncio.run(_generate())
    return filename

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

if st.button("✨ 一键生成分镜、提示词和配音", type="primary"):
    if not script_text.strip():
        st.warning("请先粘贴剧本内容哦！")
    else:
        with st.spinner("AI 导演正在构思画面并指导配音..."):
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
            - 【英文提示词】：(极其详细的英文生图提示词，包含镜头景别、画面主体、动作、环境光影、画质词。不同词组用逗号隔开。)
            - 【配音/台词】：(这一镜的台词或旁白)
            
            不要输出多余的废话，直接给我分镜表。
            """
            
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post(url, headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]
            
            st.success("🎉 分镜生成完毕！你可以直接复制英文提示词去生成画面。")
            
            # 展示生成的 Markdown 内容
            st.markdown(reply)
            
            st.write("---")
            # 提取台词并生成语音
            with st.spinner("正在为角色配音..."):
                try:
                    # 使用正则表达式提取【配音/台词】后面的内容
                    dialogue_matches = re.findall(r"【配音/台词】：(.*)", reply)
                    
                    if dialogue_matches:
                        # 把提取到的台词拼成一段话
                        full_dialogue = "。".join([d.strip() for d in dialogue_matches])
                        
                        # 调用语音生成函数
                        audio_file = generate_voice(full_dialogue)
                        
                        st.write("🔊 **短剧原声配音预览（可下载）：**")
                        st.audio(audio_file, format="audio/mp3", autoplay=True)
                    else:
                        st.info("没有在分镜中检测到明显的台词，不生成配音。")
                except Exception as e:
                    st.error(f"配音生成失败：{e}")

st.markdown("---")
st.caption("🎬 创作流程：用本工具生成提示词 -> 去【即梦/可灵】生成画面 -> 去【剪映】配音加字幕。")
