import os
import streamlit as st
from tkinter import Tk, filedialog
from yt_dlp import YoutubeDL

# Streamlit UI configuration (MUST be the first Streamlit command)
st.set_page_config(page_title="YouTube Downloader", layout="centered", initial_sidebar_state="collapsed")

# Function to open folder picker dialog (always on top)
def select_folder():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return folder_selected

# Function for browser notification (JavaScript injection)
def browser_notification(title, message):
    st.components.v1.html(
        f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                if (Notification.permission !== "granted") {{
                    Notification.requestPermission();
                }}
            }});

            function showNotification() {{
                if (Notification.permission === "granted") {{
                    new Notification("{title}", {{ body: "{message}" }});
                }}
            }}
            showNotification();
        </script>
        """,
        height=0,
    )

# Custom CSS for responsive design
st.markdown("""
    <style>
        @media (max-width: 768px) {
            h1 {font-size: 1.8rem !important;}
            .stButton > button {font-size: 0.9rem; padding: 0.6rem 1rem;}
            .stTextInput > div > div > input {font-size: 0.9rem;}
            .stRadio > div {font-size: 0.9rem;}
        }
        @media (min-width: 769px) {
            h1 {font-size: 2.5rem !important;}
            .stButton > button {font-size: 1rem; padding: 0.8rem 1.2rem;}
            .stTextInput > div > div > input {font-size: 1rem;}
            .stRadio > div {font-size: 1rem;}
        }
        .stMarkdown p {font-size: 1rem;}
        .stSelectbox div, .stTextArea textarea {font-size: 1rem !important;}
    </style>
""", unsafe_allow_html=True)

st.title("📥 YouTube Video/Audio Downloader")

st.markdown("""
This tool allows you to download YouTube videos or extract audio.  
Paste the link, choose your preferred format, select the output path, and click **Download**.
""")

# Input fields
url = st.text_input("🔗 Paste the YouTube video or playlist link:")

# Download options
st.subheader("🎚️ Select Download Options:")
download_type = st.radio("Choose the type of download:",
                         ("Video", "Audio", "Best Quality", "Custom Command"))

video_quality = None
audio_format = None

if download_type == "Video":
    video_quality = st.selectbox("📺 Select Video Quality:",
                                 ("1080p", "720p", "480p", "360p", "240p", "144p"))
elif download_type == "Audio":
    audio_format = st.selectbox("🎵 Select Audio Format:",
                                ("mp3", "wav", "aac", "flac", "m4a"))

# Folder picker for output path
if st.button("📁 Select Download Folder"):
    selected_folder = select_folder()
    if selected_folder:
        st.session_state["output_folder"] = selected_folder
        st.success(f"Selected folder: {selected_folder}")
    else:
        st.warning("⚠️ No folder selected.")

output_folder = st.session_state.get("output_folder", "downloads")
os.makedirs(output_folder, exist_ok=True)

advanced_options = ""
if download_type == "Custom Command":
    advanced_options = st.text_area("⚙️ Enter custom yt-dlp command options:",
                                    help="Example: -f bestvideo+bestaudio --merge-output-format mp4")

# Progress and status
progress_bar = st.progress(0)
status_text = st.empty()

# Download button and command execution
if st.button("⬇️ Download"):
    if url:
        st.info("⏳ Download in progress. Please wait...")

        # Progress hook function
        def progress_hook(d):
            if d['status'] == 'downloading':
                percentage = float(d.get('downloaded_bytes', 0)) / float(d.get('total_bytes', 1))
                progress_bar.progress(int(percentage * 100))
                status_text.text(f"⬇️ Downloading: {d['_percent_str'].strip()} at {d['_speed_str']} - ETA {d['_eta_str']}")
            elif d['status'] == 'finished':
                progress_bar.progress(100)
                status_text.text("✅ Download complete! Processing file...")

        # yt-dlp options
        ydl_opts = {
            'progress_hooks': [progress_hook],
            'outtmpl': f"{output_folder}/%(title)s.%(ext)s"
        }

        if download_type == "Best Quality":
            ydl_opts['format'] = 'best'

        elif download_type == "Video" and video_quality:
            resolution = video_quality.replace("p", "")
            ydl_opts['format'] = f"bestvideo[height<={resolution}]+bestaudio/best"

        elif download_type == "Audio" and audio_format:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': '192',
                }]
            })

        elif download_type == "Custom Command" and advanced_options.strip():
            ydl_opts['postprocessors'] = []

        else:
            st.error("⚠️ Missing selection or options.")
            ydl_opts = None

        # Execute download
        if ydl_opts:
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                st.toast(f"✅ Download complete! Check the '{output_folder}' folder.", icon='🎉')
                browser_notification("✅ Download Complete!", f"Check the '{output_folder}' folder.")

            except Exception as e:
                st.error(f"❌ Download failed: {e}")
    else:
        st.warning("⚠️ Please enter a valid YouTube URL.")

st.markdown("---")
st.caption("Copyright © 2025 ChhinlungTech. All rights reserved.")