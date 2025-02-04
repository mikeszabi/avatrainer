import os
import sys
from pathlib import Path
import base64
import shutil

# Add parent directory to path
#ROOT_DIR = Path(__file__).parent.parent
#sys.path.append(str(ROOT_DIR))
sys.path.append(r'../zedtools')

import streamlit as st
import tempfile
from svo_processor import SVOProcessor

def get_video_html(video_path):
    """Generate HTML to embed video directly"""
    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()
        video_base64 = base64.b64encode(video_bytes).decode()
        video_html = f'''
            <video width="100%" controls>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        '''
    return video_html

# App configuration
st.set_page_config(
    page_title="SVO Processor",
    page_icon="🎥",
    layout="wide"
)

# Initialize session state
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = r'./uploads' #tempfile.mkdtemp()
    st.session_state.json_output_path = None
    st.session_state.video_output_path = None

def process_svo(file, process_type="video"):
    """Process SVO file and return output path"""
    try:
        processor = SVOProcessor(file)
        if process_type == "video":
            return processor.svo2video()
        else:
            return processor.svo2json()
    except Exception as e:
        st.error(f"Processing failed: {e}")
        return None

# Main UI
st.title("SVO Processor App 🎥")

uploaded_file = st.file_uploader("Upload SVO File", type=["svo"])

if uploaded_file:
    # Save uploaded file
    svo_path = Path(st.session_state.temp_dir) / uploaded_file.name
    with open(svo_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate JSON"):
            with st.spinner("Processing..."):
                output_path = process_svo(str(svo_path), "json")
                if output_path:
                    st.session_state.json_output_path = output_path
                    with open(output_path, "rb") as f:
                        st.download_button(
                            "Download JSON",
                            f,
                            file_name=Path(output_path).name,
                            mime="application/json"
                        )
    
    with col2:
        if st.button("Generate Video"):
            with st.spinner("Processing..."):
                progress = st.progress(0)
                output_path = process_svo(str(svo_path), "video")
                if output_path:
                    st.session_state.video_output_path = output_path
                    # Use HTML embedding instead of st.video()
                    st.markdown(get_video_html(output_path), unsafe_allow_html=True)
                    #st.video('http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4')
                    with open(output_path, "rb") as f:
                        st.download_button(
                            "Download Video",
                            f,
                            file_name=Path(output_path).name,
                            mime="video/mp4"
                        )

# Cleanup on session end
def cleanup():
    try:
        if os.path.exists(st.session_state.temp_dir):
            shutil.rmtree(st.session_state.temp_dir)
    except Exception as e:
        st.error(f"Cleanup failed: {e}")

st.session_state['cleanup'] = cleanup