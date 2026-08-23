# utils/video_processor.py
import numpy as np
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip
from utils.font_loader import load_font

def draw_dialogue_box(text, width, height=130, speaker_name="旁白", accent_hex="#d3bc8e"):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, height], fill=(12, 16, 24, 215))

    accent_rgb = tuple(int(accent_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    gold_color = accent_rgb + (220,)
    draw.line([(0, 2), (width, 2)], fill=gold_color, width=2)
    draw.line([(0, height - 2), (width, height - 2)], fill=gold_color, width=2)

    name_font = load_font(20)
    text_font = load_font(24)

    speaker_color = accent_rgb + (255,)
    draw.text((width // 2, 25), speaker_name, font=name_font, fill=speaker_color, anchor="mm")
    draw.text((width // 2, 75), text, font=text_font, fill=(255, 255, 255, 255), anchor="mm")

    return ImageClip(np.array(img))

def process_video_subtitles(input_path, subtitle_data, style):
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

        dialogue_clip = (
            draw_dialogue_box(
                sub["text"], 
                width=box_width, 
                height=box_height,
                speaker_name=style["speaker"], 
                accent_hex=style["accent"]
            )
            .set_start(sub["start"])
            .set_duration(duration)
            .set_position((box_x, box_y))
        )
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
    
    video.close()
    final_video.close()
    return output_path
