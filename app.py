import os
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip

# Helper function to render text via PIL (No ImageMagick required)
def create_subtitle_clip(text, width, height, fontsize=28):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try loading a system Chinese font (Windows uses msyh.ttc for YaHei)
    font = None
    font_names = ["msyh.ttc", "simhei.ttf", "msyhbd.ttc", "PingFang.ttc"]
    
    for font_name in font_names:
        try:
            font = ImageFont.truetype(font_name, fontsize)
            break
        except IOError:
            continue
            
    if font is None:
        font = ImageFont.load_default()

    # Draw centered white text
    draw.text((width // 2, height // 2), text, font=font, fill="white", anchor="mm")
    
    # Convert PIL Image array to MoviePy ImageClip
    return ImageClip(np.array(img))

# --- Streamlit UI ---
st.set_page_config(page_title="Genshin Video Translator", page_icon="✨", layout="centered")

st.title("✨ Genshin-Style Video Translator")
st.write("Upload an English video, and turn it into a Mandarin RPG cutscene!")

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
            translator = GoogleTranslator(source='en', target='zh-CN')

            subtitle_data = []
            for segment in segments:
                en_text = segment.text.strip()
                zh_text = translator.translate(en_text)
                subtitle_data.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": zh_text
                })

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
                box_height = 80
                box_x = (video.w - box_width) // 2
                box_y = video.h - 150

                # Semi-transparent dark background rectangle
                box_clip = (ColorClip(size=(box_width, box_height), color=(30, 30, 30))
                            .set_opacity(0.75)
                            .set_start(sub["start"])
                            .set_duration(duration)
                            .set_position((box_x, box_y)))

                # Text overlay using PIL (no ImageMagick dependency)
                txt_clip = (create_subtitle_clip(sub["text"], box_width - 40, box_height)
                            .set_start(sub["start"])
                            .set_duration(duration)
                            .set_position((box_x + 20, box_y)))

                clips.append(box_clip)
                clips.append(txt_clip)

            final_video = CompositeVideoClip(clips)
            output_path = "output_mandarin.mp4"
            final_video.write_videofile(output_path, fps=video.fps, codec="libx264", audio_codec="aac")

            progress_bar.progress(100)
            status_text.text("Done!")

            st.subheader("Your Genshin-Style Translated Video:")
            st.video(output_path)

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")