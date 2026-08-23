import time
import os
import urllib.request
import numpy as np
import streamlit as st

st.set_page_config(page_title="LectureBridge", page_icon="🌉", layout="wide")

from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator, MyMemoryTranslator
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip

# ============================================================
# STYLE PRESETS
# Each caption style maps to a speaker label, accent color and
# a light-touch phrasing template. True creative rewriting of
# the transcript (the way the mock-up's "Storytelling" example
# turns a sentence into a mini-parable) needs an LLM call, which
# isn't wired up here — deep_translator only does literal
# translation. The templates below add a believable "flavor"
# wrapper around the literal translation so each style still
# reads differently, without inventing facts that weren't said.
# ============================================================
STYLES = {
    "storytelling": {
        "label": "Storytelling 故事风",
        "accent": "#e0577a",
        "bg": "#f7d9e1",
        "speaker": "旁白",
        "desc": "Rewrites complex business/humanities theories as vivid historical parables and case stories. Highly visual.",
        "prefix": "【故事风】",
    },
    "casual": {
        "label": "Casual Chat 闲聊风",
        "accent": "#3b82c4",
        "bg": "#d7e6f5",
        "speaker": "同学",
        "desc": "Translates dense formulas and concepts into relaxed, casual gossip style. Feels like chatting with roommates.",
        "prefix": "",
    },
    "academic": {
        "label": "Academic 学术风",
        "accent": "#a6742c",
        "bg": "#efe0bd",
        "speaker": "教授",
        "desc": "Direct, highly structured, standardized academic terminology, ideal for engineering, mathematics and law papers.",
        "prefix": "",
    },
    "comic": {
        "label": "Comic / Funny 搞笑风",
        "accent": "#7c5cd6",
        "bg": "#e3ddf7",
        "speaker": "梗王",
        "desc": "Infuses internet slang and memes to explain dry points. Turn 2-hour lectures into high-quality comedy.",
        "prefix": "哈哈，",
    },
}

UNIVERSITIES = [
    "University of Melbourne (UniMelb)",
    "Monash University",
    "University of Sydney (USYD)",
    "UNSW Sydney",
    "Australian National University (ANU)",
    "University of Queensland (UQ)",
]

# ============================================================
# LECTUREBRIDGE THEME CSS
# ============================================================
lecturebridge_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Noto+Sans+SC:wght@500;700&display=swap');

    html, body, [class*="css"] { font-family: 'Poppins', 'Noto Sans SC', sans-serif; }

    .stApp {
        background: #0d1420;
        color: #ece8de;
    }

    #MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }

    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1300px; }

    /* ---- Top nav bar ---- */
    .lb-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #0d1420;
        border-bottom: 1px solid #1f2937;
        padding: 14px 4px 18px 4px;
        margin-bottom: 18px;
    }
    .lb-logo { display: flex; align-items: center; gap: 12px; }
    .lb-logo-box { width: 38px; height: 38px; background: #f0ebe0; border-radius: 8px; }
    .lb-logo-text { font-weight: 800; font-size: 20px; color: #f0ebe0; line-height: 1.1; }
    .lb-logo-sub { font-size: 10px; letter-spacing: 1px; color: #8b93a5; }
    .lb-nav-links { display: flex; gap: 32px; font-weight: 600; font-size: 15px; }
    .lb-nav-link-active { color: #e8c468; }
    .lb-nav-link { color: #ccd1db; }
    .lb-user { display: flex; align-items: center; gap: 10px; text-align: right; }
    .lb-user-name { font-weight: 700; font-size: 14px; color: #f0ebe0; }
    .lb-user-sub { font-size: 11px; color: #8b93a5; }
    .lb-avatar { width: 34px; height: 34px; border-radius: 50%; background: #3a4256; }

    /* ---- Hero ---- */
    .lb-hero {
        background: #151d2c;
        border: 1px solid #232c3d;
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 22px;
    }
    .lb-hero h1 {
        color: #f0ebe0 !important;
        font-size: 30px;
        font-weight: 800;
        margin: 0 0 6px 0;
    }
    .lb-hero h1 span { color: #e8c468; }
    .lb-hero p { color: #9aa2b3; margin: 0; font-size: 15px; }

    /* ---- Card panels ---- */
    .lb-card {
        background: #f4f1e8;
        border-radius: 14px;
        padding: 26px 28px;
        color: #1a1f2b;
    }
    .lb-card h3 { color: #1a1f2b !important; font-weight: 700; margin-top: 0; }
    .lb-side-card {
        background: #f4f1e8;
        border-radius: 14px;
        padding: 20px 22px;
        color: #1a1f2b;
        margin-bottom: 18px;
    }
    .lb-side-card h4 { color: #1a1f2b !important; font-weight: 700; margin: 0 0 12px 0; }

    /* Field labels rendered above widgets */
    .lb-field-label { font-weight: 600; font-size: 13px; color: #1a1f2b; margin-bottom: -8px; }

    /* Streamlit text inputs / selects styled like cream fields */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        border: 1px solid #d8d2c2 !important;
        border-radius: 8px !important;
        color: #1a1f2b !important;
    }

    /* Style-choice radio rendered as colored cards */
    div[role="radiogroup"] { gap: 10px; }
    div[role="radiogroup"] label {
        border-radius: 10px !important;
        padding: 4px 2px !important;
    }

    /* File uploader as dropzone */
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #c9c2ac !important;
        border-radius: 12px !important;
    }

    /* Buttons: cream RPG-free flat style */
    .stButton > button {
        background: #f0ebe0 !important;
        color: #14181f !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 20px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #e8c468 !important;
        box-shadow: 0 0 12px rgba(232, 196, 104, 0.5) !important;
    }

    /* Progress bar accent */
    div[data-testid="stProgress"] > div > div > div { background-color: #e8c468 !important; }

    /* Badges for recent translation status */
    .lb-badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
    .lb-badge-done { background: #d7f2df; color: #1c7a3b; }
    .lb-badge-progress { background: #fbdada; color: #b23a3a; }
    .lb-badge-queued { background: #fdeecb; color: #a56a10; }

    .lb-recent-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #e4dfd0; }
    .lb-recent-title { font-weight: 700; font-size: 13.5px; color: #1a1f2b; }
    .lb-recent-sub { font-size: 11.5px; color: #767162; margin-top: 2px; }

    .lb-demo-quote { border-radius: 8px; padding: 12px 14px; font-size: 13px; margin-top: 4px; }
</style>
"""
st.markdown(lecturebridge_css, unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
if "jobs" not in st.session_state:
    # seed with a couple of example rows so "Recent Translations" isn't empty on first run
    st.session_state.jobs = [
        {"title": "COMP20003 Lecture 1", "meta": "UniMelb • 58 Mins", "status": "queued", "progress": 0},
    ]
if "selected_style" not in st.session_state:
    st.session_state.selected_style = "storytelling"

# ============================================================
# TOP NAV + HERO
# ============================================================
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

# ============================================================
# MAIN LAYOUT: form (left) + recent/demo (right)
# ============================================================
main_col, side_col = st.columns([2, 1], gap="large")

with main_col:
    st.markdown('<div class="lb-card">', unsafe_allow_html=True)
    st.markdown("### Lecture Details / 课程详情")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="lb-field-label">Video Title 视频标题</div>', unsafe_allow_html=True)
        video_title = st.text_input("Video Title", placeholder="e.g., Intro to Financial Accounting Week 3", label_visibility="collapsed")
    with c2:
        st.markdown('<div class="lb-field-label">Course / Subject Code 课程/科目代码</div>', unsafe_allow_html=True)
        course_code = st.text_input("Course Code", placeholder="e.g., COMP10003", label_visibility="collapsed")

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="lb-field-label">University 就读大学</div>', unsafe_allow_html=True)
        university = st.selectbox("University", UNIVERSITIES, label_visibility="collapsed")
    with c4:
        st.markdown('<div class="lb-field-label">Language Pair 语伴选择</div>', unsafe_allow_html=True)
        st.selectbox("Language Pair", ["English (Aussie)  →  Chinese captions"], label_visibility="collapsed")

    st.markdown('<div class="lb-field-label" style="margin-top:6px;">Select Capture &amp; Captioning Style 选择字幕翻译风格</div>', unsafe_allow_html=True)
    style_key = st.radio(
        "Style",
        options=list(STYLES.keys()),
        format_func=lambda k: STYLES[k]["label"],
        horizontal=True,
        label_visibility="collapsed",
        key="selected_style",
    )
    style = STYLES[style_key]
    st.markdown(
        f'<div style="background:{style["bg"]};border:1px solid {style["accent"]}55;border-radius:10px;'
        f'padding:10px 14px;font-size:13px;color:#2a2a2a;margin-bottom:6px;">'
        f'<b style="color:{style["accent"]};">{style["label"]}</b> — {style["desc"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Place Your Recording Here, Traveler — supports drag-and-drop or direct upload (MP4, MOV, AVI, M4A, MP3, up to 2GB)",
        type=["mp4", "mov"],
    )

    generate_clicked = st.button("Begin Translation! 开始翻译！", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with side_col:
    st.markdown('<div class="lb-side-card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="lb-side-card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PROCESSING PIPELINE (unchanged backend, now style-aware)
# ============================================================

def draw_dialogue_box(text, width, height=130, speaker_name="旁白", accent_hex="#d3bc8e"):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, height], fill=(12, 16, 24, 215))

    accent_rgb = tuple(int(accent_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    gold_color = accent_rgb + (220,)
    draw.line([(0, 2), (width, 2)], fill=gold_color, width=2)
    draw.line([(0, height - 2), (width, height - 2)], fill=gold_color, width=2)

    font_path = get_chinese_font_path()
    name_font = None
    text_font = None

    if font_path:
        try:
            name_font = ImageFont.truetype(font_path, 20)
            text_font = ImageFont.truetype(font_path, 24)
        except Exception:
            pass

    if text_font is None:
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    speaker_color = accent_rgb + (255,)
    draw.text((width // 2, 25), speaker_name, font=name_font, fill=speaker_color, anchor="mm")
    draw.text((width // 2, 75), text, font=text_font, fill=(255, 255, 255, 255), anchor="mm")

    return ImageClip(np.array(img))


def translate_safely(text, google_translator, fallback_translator):
    if not text or not text.strip():
        return ""

    for attempt in range(2):
        try:
            translated = google_translator.translate(text)
            if translated:
                return translated
        except Exception:
            if attempt == 0:
                time.sleep(1.5)

    try:
        if len(text) <= 500:
            translated = fallback_translator.translate(text)
            if translated:
                return translated
    except Exception:
        pass

    return text


def get_chinese_font_path():
    font_filename = "NotoSansSC-Regular.ttf"
    if not os.path.exists(font_filename):
        font_url = "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
        try:
            urllib.request.urlretrieve(font_url, font_filename)
        except Exception as e:
            st.warning(f"Could not download custom font: {e}")
    return font_filename if os.path.exists(font_filename) else None


def create_subtitle_clip(text, width, height, fontsize=28):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_path = get_chinese_font_path()
    font = None

    if font_path:
        try:
            font = ImageFont.truetype(font_path, fontsize)
        except Exception:
            pass

    if font is None:
        font_names = ["msyh.ttc", "simhei.ttf", "msyhbd.ttc", "PingFang.ttc"]
        for fn in font_names:
            try:
                font = ImageFont.truetype(fn, fontsize)
                break
            except IOError:
                continue

    if font is None:
        font = ImageFont.load_default()

    draw.text((width // 2, height // 2), text, font=font, fill="white", anchor="mm")
    return ImageClip(np.array(img))


if uploaded_file is not None:
    input_path = "input_temp.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.markdown("### Original Video")
    st.video(input_path)

if uploaded_file is not None and generate_clicked:
    display_title = video_title.strip() or uploaded_file.name
    job_label = f"{course_code.strip()} — {display_title}" if course_code.strip() else display_title
    job = {"title": job_label, "meta": f"{university.split(' (')[0]} • processing", "status": "translating", "progress": 0}
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

        video = VideoFileClip(input_path)
        clips = [video]

        for sub in subtitle_data:
            duration = sub["end"] - sub["start"]
            if duration <= 0:
                continue

            box_width = int(video.w * 0.8)
            box_height = 120
            box_x = (video.w - box_width) // 2
            box_y = video.h - 150

        

            dialogue_clip = (draw_dialogue_box(sub["text"], width=box_width, height=box_height,
                                                speaker_name=style["speaker"], accent_hex=style["accent"])
                              .set_start(sub["start"])
                              .set_duration(duration)
                              .set_position((box_x, box_y)))
            clips.append(dialogue_clip)

        final_video = CompositeVideoClip(clips)
        output_path = "output_translated.mp4"

        final_video.write_videofile(
            output_path,
            fps=video.fps,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            ffmpeg_params=["-pix_fmt", "yuv420p"],
        )

        progress_bar.progress(100)
        status_text.text("Done!")
        job["status"] = "done"
        job["meta"] = f"{university.split(' (')[0]} • {style['label']}"

        st.markdown("### Your LectureBridge Translated Video")
        st.video(output_path)

    except Exception as e:
        job["status"] = "queued"
        st.error(f"An error occurred during processing: {e}")
