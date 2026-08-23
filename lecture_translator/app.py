# app.py
import time
import streamlit as st
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator, MyMemoryTranslator

from config import STYLES, UNIVERSITIES, get_theme_css
from utils.translator import translate_safely
from utils.video_processor import process_video_subtitles

st.set_page_config(page_title="LectureBridge", page_icon="🌉", layout="wide")

# Session State Initialization
if "jobs" not in st.session_state:
    st.session_state.jobs = [
        {"title": "COMP20003 Lecture 1", "meta": "UniMelb • 58 Mins", "status": "queued"},
    ]
if "selected_style" not in st.session_state:
    st.session_state.selected_style = "storytelling"

selected_key = st.session_state.selected_style
st.markdown(get_theme_css(selected_key), unsafe_allow_html=True)

# Navigation & Header
st.markdown("""
<div class="lb-navbar">
    <div class="lb-logo">
        <div class="lb-logo-box"></div>
        <div>
            <div class="lb-logo-text">LectureBridge</div>
            <div class="lb-logo-sub">QUICK TRANSLATIONS</div>
        </div>
    </div>
    <div class="lb-nav-links">
        <span class="lb-nav-link-active">Home 首页</span>
        <span class="lb-nav-link">My Videos 我的视频</span>
        <span class="lb-nav-link">Library 公共库</span>
    </div>
    <div class="lb-user">
        <div>
            <div class="lb-user-name">Ian Tie</div>
            <div class="lb-user-sub">UniMelb Student</div>
        </div>
        <div class="lb-avatar"></div>
    </div>
</div>

<div class="lb-hero">
    <h1>Summon Your Lecture <span>/ 请将录音投入传送门，旅行者</span></h1>
    <p>Transform your Australian university lectures into highly engaging, culturally native Chinese dialogues.</p>
</div>
""", unsafe_allow_html=True)

# Main UI Layout
main_col, side_col = st.columns([2, 1], gap="large")

with main_col:
    with st.container(key="lecture_card"):
        st.markdown("### Lecture Details / 课程详情")

        c1, c2 = st.columns(2)
        with c1:
            video_title = st.text_input("Video Title 视频标题", placeholder="e.g., Intro to Financial Accounting Week 3")
        with c2:
            course_code = st.text_input("Course / Subject Code 课程/科目代码", placeholder="e.g., COMP10003")

        c3, c4 = st.columns(2)
        with c3:
            university = st.selectbox("University 就读大学", UNIVERSITIES)
        with c4:
            st.selectbox("Language Pair 语伴选择", ["English (Aussie)  →  Chinese captions"])

        st.markdown('<div style="font-weight:700;font-size:13px;color:#1a1f2b;margin:8px 0 6px 0;">Select Capture &amp; Captioning Style 选择字幕翻译风格</div>', unsafe_allow_html=True)
        style_cols = st.columns(4)
        for col, key in zip(style_cols, STYLES.keys()):
            with col:
                with st.container(key=f"style_btn_{key}"):
                    check = "✓ " if key == selected_key else ""
                    if st.button(f"{check}{STYLES[key]['label']}", key=f"pick_{key}", use_container_width=True):
                        st.session_state.selected_style = key
                        st.rerun()

        style = STYLES[st.session_state.selected_style]
        st.markdown(
            f'<div style="background:{style["bg"]};border:1px solid {style["accent"]}55;border-radius:10px;'
            f'padding:10px 14px;font-size:13px;color:#2a2a2a;margin:10px 0 6px 0;">'
            f'<b style="color:{style["accent"]};">{style["label"]}</b> — {style["desc"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Place Your Recording Here, Traveler — supports drag-and-drop or direct upload (MP4, MOV, AVI, M4A, MP3, up to 2GB)",
            type=["mp4", "mov"],
        )

        generate_clicked = st.button("Begin Translation! 开始翻译！", use_container_width=True)

with side_col:
    with st.container(key="recent_card"):
        st.markdown("#### Recent Translations 近期翻译进度")
        for job in st.session_state.jobs[-6:][::-1]:
            badge_class = {"done": "lb-badge-done", "translating": "lb-badge-progress", "queued": "lb-badge-queued"}.get(job["status"], "lb-badge-queued")
            badge_label = {"done": "Done 已完成", "translating": "Translating 翻译中", "queued": "Queued 排队中"}.get(job["status"], "Queued 排队中")
            st.markdown(f"""
            <div class="lb-recent-row">
                <div>
                    <div class="lb-recent-title">{job["title"]}</div>
                    <div class="lb-recent-sub">{job["meta"]}</div>
                </div>
                <span class="lb-badge {badge_class}">{badge_label}</span>
            </div>
            """, unsafe_allow_html=True)

    with st.container(key="demo_card"):
        st.markdown(f"#### Live Style Demo 当前风格对比示例 ({style['label']})")
        st.markdown(f"""
        <div class="lb-demo-quote" style="background:#eeeae0;color:#333;">
            <b>LECTURER SAYS:</b><br/>
            "Now, marginal utility is basically the extra satisfaction a consumer gets from having one more unit of a good or service..."
        </div>
        <div class="lb-demo-quote" style="background:{style['bg']};color:{style['accent']};font-weight:600;">
            {style['label'].upper()} STYLE CHINESE SUBTITLE:<br/>
            <span style="color:#2a2a2a;font-weight:500;">
            "{style['prefix']}想象一下，边际效用就是你多吃一块西瓜时，比上一块多得到的那一点点满足感……"
            </span>
        </div>
        """, unsafe_allow_html=True)

if uploaded_file is not None:
    input_path = "input_temp.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.markdown("### Original Video")
    st.video(input_path)

if uploaded_file is not None and generate_clicked:
    display_title = video_title.strip() or uploaded_file.name
    job_label = f"{course_code.strip()} — {display_title}" if course_code.strip() else display_title
    job = {"title": job_label, "meta": f"{university.split(' (')[0]} • processing", "status": "translating"}
    st.session_state.jobs.append(job)

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Loading AI model...")
        progress_bar.progress(10)
        model = WhisperModel("base", device="cpu", compute_type="int8")

        status_text.text("Transcribing English audio...")
        progress_bar.progress(30)
        segments, info = model.transcribe(input_path, beam_size=5)

        status_text.text(f"Translating to Mandarin ({style['label']})...")
        progress_bar.progress(50)
        google_translator = GoogleTranslator(source="en", target="zh-CN")
        fallback_translator = MyMemoryTranslator(source="en-GB", target="zh-CN")
        
        subtitle_data = []
        for segment in segments:
            en_text = segment.text.strip()
            if not en_text:
                continue
            zh_text = translate_safely(en_text, google_translator, fallback_translator)
            styled_zh_text = f"{style['prefix']}{zh_text}" if style["prefix"] else zh_text
            subtitle_data.append({
                "start": segment.start,
                "end": segment.end,
                "english": en_text,
                "chinese": zh_text,
                "text": styled_zh_text,
            })
            time.sleep(0.3)

        status_text.text("Rendering dialogue boxes...")
        progress_bar.progress(75)

        output_path = process_video_subtitles(input_path, subtitle_data, style)

        progress_bar.progress(100)
        status_text.text("Done!")
        job["status"] = "done"
        job["meta"] = f"{university.split(' (')[0]} • {style['label']}"

        st.markdown("### Your LectureBridge Translated Video")
        st.video(output_path)

    except Exception as e:
        job["status"] = "queued"
        st.error(f"An error occurred during processing: {e}")

    except Exception as e:
        job["status"] = "queued"
        st.error(f"An error occurred during processing: {e}")
