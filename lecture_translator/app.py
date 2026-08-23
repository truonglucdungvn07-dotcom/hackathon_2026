import time
import os
import urllib.request
import numpy as np
import streamlit as st
st.set_page_config(page_title="Genshin Video Translator", page_icon="🥰", layout="centered")

# --- Custom Genshin Impact Theme CSS ---
genshin_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Noto+Sans+SC:wght@500;700&display=swap');

    /* Global Body & Background */
    .stApp {
        background: linear-gradient(135deg, #121824 0%, #1a2332 100%);
        color: #ece5d8;
        font-family: 'Noto Sans SC', sans-serif;
    }

    /* Genshin Title Styling */
    h1 {
        font-family: 'Cinzel', serif !important;
        color: #f3e2b2 !important;
        text-shadow: 0px 0px 10px rgba(243, 226, 178, 0.4);
        font-weight: 700 !important;
        text-align: center;
    }

    /* Subheaders and Section Titles */
    h2, h3, label {
        font-family: 'Cinzel', serif !important;
        color: #d3bc8e !important;
    }

    /* Custom RPG Gold Buttons */
    .stButton > button {
        background: linear-gradient(180deg, #4a5568 0%, #2d3748 100%) !important;
        color: #f3e2b2 !important;
        border: 2px solid #d3bc8e !important;
        border-radius: 20px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #d3bc8e 0%, #b39b69 100%) !important;
        color: #1a2332 !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 15px rgba(211, 188, 142, 0.6) !important;
    }

    /* Card Box Containers */
    div[data-testid="stFileUploader"] {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid #d3bc8e;
        border-radius: 12px;
        padding: 15px;
    }
</style>
"""

st.markdown(genshin_css, unsafe_allow_html=True)
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator, MyMemoryTranslator
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip

def draw_genshin_cutscene_dialogue(text, width, height=130, speaker_name="旅行者"):
    # 1. Create transparent RGBA canvas
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 2. Wide dark semi-transparent background band (Genshin Cutscene Style)
    # Filling the banner with high opacity towards the middle
    draw.rectangle([0, 0, width, height], fill=(12, 16, 24, 215))

    # 3. Top and Bottom Gold Accent Lines (#D3BC8E)
    gold_color = (211, 188, 142, 220)
    draw.line([(0, 2), (width, 2)], fill=gold_color, width=2)
    draw.line([(0, height - 2), (width, height - 2)], fill=gold_color, width=2)

    # 4. Load CJK Fonts
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

    # 5. Draw Gold Speaker Name (Centered Top)
    speaker_color = (243, 226, 178, 255) # Genshin Gold Title Text
    draw.text((width // 2, 25), speaker_name, font=name_font, fill=speaker_color, anchor="mm")

    # 6. Draw White Chinese Dialogue Text (Centered Below Speaker Name)
    draw.text((width // 2, 75), text, font=text_font, fill=(255, 255, 255, 255), anchor="mm")

    return ImageClip(np.array(img))

def translate_safely(text, google_translator, fallback_translator):
    if not text or not text.strip():
        return ""

    # Try Google Translator twice
    for attempt in range(2):
        try:
            translated = google_translator.translate(text)

            if translated:
                return translated

        except Exception:
            if attempt == 0:
                time.sleep(1.5)

    # If Google fails, try MyMemory
    try:
        if len(text) <= 500:
            translated = fallback_translator.translate(text)

            if translated:
                return translated
    except Exception:
        pass

    # Final fallback: keep the English sentence
    return text

# Function to ensure a Chinese TTF font exists in the environment
def get_chinese_font_path():
    font_filename = "NotoSansSC-Regular.ttf"
    
    # If not already present locally, download Google's free Noto Sans SC font
    if not os.path.exists(font_filename):
        font_url = "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
        try:
            urllib.request.urlretrieve(font_url, font_filename)
        except Exception as e:
            st.warning(f"Could not download custom font: {e}")

    return font_filename if os.path.exists(font_filename) else None

# Render text via PIL using the reliable downloaded CJK font
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

    # System font fallbacks if local download fails
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

    # Draw centered white text
    draw.text((width // 2, height // 2), text, font=font, fill="white", anchor="mm")
    return ImageClip(np.array(img))

# --- Streamlit UI ---

st.title("✨ Genshin-Style Video Translator")
st.write("Upload an English video, and turn it into a Mandarin!")

uploaded_file = st.file_uploader("Choose an MP4 video (keep it under 30 seconds for speed!)", type=["mp4", "mov"])

if uploaded_file is not None:
    input_path = "input_temp.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.subheader("Original Video:")
    st.video(input_path)

    if st.button("🚀 Generate Genshin Subtitles"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # 1. Load Whisper Model
            status_text.text("Loading AI model...")
            progress_bar.progress(10)
            model = WhisperModel("base", device="cpu", compute_type="int8")

            # 2. Transcribe Audio
            status_text.text("Transcribing English audio...")
            progress_bar.progress(30)
            segments, info = model.transcribe(input_path, beam_size=5)

            # 3. Translate to Mandarin
            status_text.text("Translating to Mandarin...")
            progress_bar.progress(50)
            google_translator = GoogleTranslator(source="en", target="zh-CN")
            fallback_translator = MyMemoryTranslator(source="en-GB", target="zh-CN")
            subtitle_data = []
            for segment in segments:
                en_text = segment.text.strip()
                if not en_text:
                    continue
                zh_text = translate_safely(en_text, google_translator, fallback_translator)
                subtitle_data.append({
                    "start": segment.start,
                    "end": segment.end,
                    "english": en_text,
                    "chinese": zh_text,
                    "text": zh_text
                })
                time.sleep(0.3)

            # 4. Render Video Overlays
            status_text.text("Rendering RPG dialogue boxes...")
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


                dialogue_clip = (draw_genshin_cutscene_dialogue(sub["text"], width=box_width, height=box_height, speaker_name="派蒙")
                                 .set_start(sub["start"])
                                 .set_duration(duration)
                                .set_position((box_x, box_y))
                )
                clips.append(dialogue_clip)

            final_video = CompositeVideoClip(clips)
            output_path = "output_mandarin.mp4"

            # Added ffmpeg_params yuv420p for universal browser playback
            final_video.write_videofile(
                output_path, 
                fps=video.fps, 
                codec="libx264", 
                audio_codec="aac",
                preset="ultrafast",
                ffmpeg_params=["-pix_fmt", "yuv420p"]
            )

            progress_bar.progress(100)
            status_text.text("Done!")

            st.subheader("Your Genshin-Style Translated Video:")
            st.video(output_path)

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
