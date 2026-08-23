# utils/font_loader.py
import os
import urllib.request
import streamlit as st
from PIL import ImageFont

def get_chinese_font_path():
    font_filename = "NotoSansSC-Regular.ttf"
    if not os.path.exists(font_filename):
        font_url = "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
        try:
            urllib.request.urlretrieve(font_url, font_filename)
        except Exception as e:
            st.warning(f"Could not download custom font: {e}")
    return font_filename if os.path.exists(font_filename) else None

def load_font(size):
    font_path = get_chinese_font_path()
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
            
    for fn in ["msyh.ttc", "simhei.ttf", "msyhbd.ttc", "PingFang.ttc"]:
        try:
            return ImageFont.truetype(fn, size)
        except IOError:
            continue

    return ImageFont.load_default()
