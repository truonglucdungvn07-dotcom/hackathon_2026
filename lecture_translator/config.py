# config.py

STYLES = {
    "storytelling": {
        "label": "Storytelling 故事风",
        "accent": "#c9366a",
        "bg": "#f7d9e1",
        "speaker": "旁白",
        "desc": "Rewrites complex business/humanities theories as vivid historical parables and case stories.",
        "prefix": "【故事风】",
    },
    "casual": {
        "label": "Casual Chat 闲聊风",
        "accent": "#1d63a8",
        "bg": "#d7e6f5",
        "speaker": "同学",
        "desc": "Translates dense formulas and concepts into relaxed, casual gossip style.",
        "prefix": "",
    },
    "academic": {
        "label": "Academic 学术风",
        "accent": "#8a5c15",
        "bg": "#efe0bd",
        "speaker": "教授",
        "desc": "Direct, highly structured, standardized academic terminology.",
        "prefix": "",
    },
    "comic": {
        "label": "Comic / Funny 搞笑风",
        "accent": "#5f3fc4",
        "bg": "#e3ddf7",
        "speaker": "梗王",
        "desc": "Infuses internet slang and memes to explain dry points.",
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

def get_theme_css(selected_key):
    style_selected_css = "\n".join(
        f'.st-key-style_btn_{key} button {{ border: 2.5px solid {s["accent"]} !important; box-shadow: 0 0 0 3px {s["accent"]}33 !important; }}'
        for key, s in STYLES.items()
        if key == selected_key
    )

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Noto+Sans+SC:wght@500;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Poppins', 'Noto Sans SC', sans-serif; }}
    .stApp {{ background: #0d1420; color: #ece8de; }}
    #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1300px; }}

    .lb-navbar {{
        display: flex; align-items: center; justify-content: space-between;
        background: #0d1420; border-bottom: 1px solid #1f2937;
        padding: 14px 4px 18px 4px; margin-bottom: 18px;
    }}
    .lb-logo {{ display: flex; align-items: center; gap: 12px; }}
    .lb-logo-box {{ width: 38px; height: 38px; background: #f0ebe0; border-radius: 8px; }}
    .lb-logo-text {{ font-weight: 800; font-size: 20px; color: #f0ebe0; line-height: 1.1; }}
    .lb-logo-sub {{ font-size: 10px; letter-spacing: 1px; color: #8b93a5; }}
    .lb-nav-links {{ display: flex; gap: 32px; font-weight: 600; font-size: 15px; }}
    .lb-nav-link-active {{ color: #e8c468; }}
    .lb-nav-link {{ color: #ccd1db; }}
    .lb-user {{ display: flex; align-items: center; gap: 10px; text-align: right; }}
    .lb-user-name {{ font-weight: 700; font-size: 14px; color: #f0ebe0; }}
    .lb-user-sub {{ font-size: 11px; color: #8b93a5; }}
    .lb-avatar {{ width: 34px; height: 34px; border-radius: 50%; background: #3a4256; }}

    .lb-hero {{ background: #151d2c; border: 1px solid #232c3d; border-radius: 14px; padding: 28px 32px; margin-bottom: 22px; }}
    .lb-hero h1 {{ color: #f0ebe0 !important; font-size: 30px; font-weight: 800; margin: 0 0 6px 0; }}
    .lb-hero h1 span {{ color: #e8c468; }}
    .lb-hero p {{ color: #9aa2b3; margin: 0; font-size: 15px; }}

    .st-key-lecture_card, .st-key-recent_card, .st-key-demo_card {{
        background: #f4f1e8 !important; border-radius: 14px !important; padding: 26px 28px !important; margin-bottom: 18px !important;
    }}
    .st-key-lecture_card *, .st-key-recent_card *, .st-key-demo_card * {{ color: #1a1f2b; }}

    div[data-testid="stTextInput"] label p, div[data-testid="stSelectbox"] label p {{ color: #1a1f2b !important; font-weight: 700 !important; font-size: 13px !important; }}
    div[data-testid="stTextInput"] input {{ background-color: #ffffff !important; border: 1px solid #cfc8b4 !important; border-radius: 8px !important; color: #000000 !important; }}
    div[data-testid="stSelectbox"] > div > div {{ background-color: #ffffff !important; border: 1px solid #cfc8b4 !important; border-radius: 8px !important; }}
    div[data-testid="stSelectbox"] span {{ color: #000000 !important; }}

    .st-key-style_btn_storytelling button {{ background: {STYLES['storytelling']['bg']} !important; color: {STYLES['storytelling']['accent']} !important; }}
    .st-key-style_btn_casual button       {{ background: {STYLES['casual']['bg']} !important;       color: {STYLES['casual']['accent']} !important; }}
    .st-key-style_btn_academic button     {{ background: {STYLES['academic']['bg']} !important;     color: {STYLES['academic']['accent']} !important; }}
    .st-key-style_btn_comic button        {{ background: {STYLES['comic']['bg']} !important;        color: {STYLES['comic']['accent']} !important; }}
    div[class*="st-key-style_btn_"] button {{ border: 2.5px solid transparent !important; border-radius: 10px !important; font-weight: 700 !important; font-size: 13.5px !important; padding: 10px 8px !important; min-height: 44px !important; }}
    {style_selected_css}

    div[data-testid="stFileUploaderDropzone"] {{ background-color: #16325c !important; border: 2px dashed #3a5d8f !important; border-radius: 12px !important; }}
    div[data-testid="stFileUploaderDropzone"] span, div[data-testid="stFileUploaderDropzone"] small, div[data-testid="stFileUploaderDropzone"] p {{ color: #ffffff !important; }}
    div[data-testid="stFileUploaderDropzone"] button {{ background-color: #25487e !important; color: #ffffff !important; border: 1px solid #3a5d8f !important; font-weight: 700 !important; }}
    div[data-testid="stFileUploaderFile"], div[data-testid="stFileUploaderFile"] * {{ color: #1a1f2b !important; }}

    .stButton > button {{ background: #f2d98d; color: #14181f; border: none; border-radius: 10px; font-weight: 700; font-size: 15px; padding: 12px 20px; transition: all 0.2s ease; }}
    .stButton > button:hover {{ background: #e8c468; box-shadow: 0 0 12px rgba(232, 196, 104, 0.5); }}
    div[data-testid="stProgress"] > div > div > div {{ background-color: #e8c468 !important; }}

    .lb-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11.5px; font-weight: 800; letter-spacing: 0.2px; white-space: nowrap; }}
    .lb-badge-done {{ background: #1c7a3b; color: #ffffff; }}
    .lb-badge-progress {{ background: #b23a3a; color: #ffffff; }}
    .lb-badge-queued {{ background: #a56a10; color: #ffffff; }}

    .lb-recent-row {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; padding: 10px 0; border-bottom: 1px solid #e4dfd0; }}
    .lb-recent-sub {{ font-size: 11.5px; color: #55524a; margin-top: 2px; }}
    .lb-demo-quote {{ border-radius: 8px; padding: 12px 14px; font-size: 13px; margin-top: 10px; }}
</style>
"""
