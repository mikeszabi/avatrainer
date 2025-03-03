import os
import sys
from pathlib import Path
import base64
import shutil
import streamlit as st

# App configuration must be first Streamlit command
st.set_page_config(
    page_title="Exercise Viewer",
    page_icon="🏃",
    layout="wide"
)

sys.path.append(r'../zedtools')
#from svo_processor import SVOProcessor


def get_video_html(video_path):
    """Generate HTML to embed video directly"""
    with open(video_path, "rb") as video_file:
        print(video_path)
        video_bytes = video_file.read()
        video_base64 = base64.b64encode(video_bytes).decode()
        video_html = f'''
            <video width="100%" controls>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        '''
    return video_html

# Setup directories
DIRS = {
    'json': Path('./public/json'),
    'svo': Path('./public/svo'),
    'video': Path('./public/video') 
}

# Create directories if they don't exist
for dir_path in DIRS.values():
    dir_path.mkdir(parents=True, exist_ok=True)

def check_server_running(port):
    """Check if server is running on specified port"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_server(directory, port):
    """Start HTTP server if not running"""
    if not check_server_running(port):
        os.system(f'python3 -m http.server {port} --directory {directory} &')
        return True
    return False

# Replace existing server setup with:
static_dir = Path(__file__).parent / 'public'
if 'static_served' not in st.session_state:
    if start_server(static_dir, 8001):
        st.session_state.static_served = True
        st.success("Started HTTP server on port 8001")
    else:
        st.info("HTTP server already running on port 8001")

# Add server status display
server_status = "🟢 Running" if check_server_running(8001) else "🔴 Stopped"
st.sidebar.markdown(f"### Server Status: {server_status}")

# def get_available_exercises():
#     """Get list of JSON files in the json directory"""
#     return [f.stem for f in DIRS['json'].glob('*.json')]

# def process_svo(file, process_type="video"):
#     """Process SVO file and return output path"""
#     try:
#         # Convert Path to string for processor
#         processor = SVOProcessor(str(file))
#         return processor.svo2video()

#     except Exception as e:
#         st.error(f"Processing failed: {e}")
#         return None

def get_available_videos():
    """Get list of SVO files in the video directory"""
    return [f.stem.replace('_compressed', '') for f in DIRS['video'].glob('*_compressed.mp4')]

def display_video_sidebar():
    """Display videos in sidebar and return selected exercise"""
    st.sidebar.markdown("### Available Videos")
    videos = get_available_videos()
    
    if not videos:
        st.sidebar.warning("No videos available")
        return None
    
    selected_video = None
    for video in videos:
        st.sidebar.markdown(f"#### {video}")
        video_path = DIRS['video'] / f"{video}_compressed.mp4"
        if video_path.exists():
            video_html = get_video_html(video_path)
            st.sidebar.markdown(video_html, unsafe_allow_html=True)
            if st.sidebar.button(f"Select {video}", key=f"btn_{video}"):
                selected_video=video
    
    return selected_video
    

# Main UI
st.title("Exercise Viewer 🏃")

# Replace exercise selection with video selection
selected_exercise = display_video_sidebar()

if selected_exercise:
    json_path = DIRS['json'] / f"{selected_exercise}.json"
    
    # Main content area - Avatar visualization
    st.markdown("### 3D Avatar Visualization")
    viewer_url = f"http://localhost:8001/index.html?jsonPath=json/{selected_exercise}.json"
    st.markdown(
        f'<iframe src="{viewer_url}" width="100%" height="600" frameborder="0"></iframe>',
        unsafe_allow_html=True
    )
else:
    st.info("Select a video from the sidebar to view the exercise")

