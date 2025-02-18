import streamlit as st
import requests
import os
import json
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components

API_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

st.title("ZED SVO Skeleton Tracker")
st.write("Upload an SVO file and watch the human skeleton movement!")

# File upload
uploaded_file = st.file_uploader("Choose an SVO file:", type=["svo"])

if uploaded_file:
    file_path = os.path.join("uploads", uploaded_file.name)
    
    # Upload file to the server
    with st.spinner("Uploading..."):
        files = {"file": uploaded_file}
        response = requests.post(f"{API_URL}/upload_svo/", files=files)
        
    if response.status_code == 200:
        st.success("File successfully uploaded!")
        
        # Start skeleton processing
        st.write("Starting processing...")
        process_response = requests.get(f"{API_URL}/process_svo/{uploaded_file.name}")
        
        if process_response.status_code == 200:
            st.success("Skeleton successfully extracted!")

            # Fetch skeleton data
            st.write("Loading skeleton data...")
            skeleton_response = requests.get(f"{API_URL}/get_skeleton/{uploaded_file.name}")
            
            if skeleton_response.status_code == 200:
                skeleton_data = skeleton_response.json()["skeleton"]
                
                if len(skeleton_data) > 0:
                    st.success("Skeleton data successfully loaded!")
                    st.write("Loading visualization...")

                    # Beágyazott WebGL Three.js oldal

                    components.iframe("http://127.0.0.1:8000/public/visualizer.html",
                                        height=600, width=800,
                                        scrolling=True,
                                        sandbox="allow-scripts allow-same-origin allow-modals")
                    
                #    # Create a figure for the animation
                #     fig = go.Figure()

                #     # Add initial frame to the figure
                #     initial_frame = np.array(skeleton_data[0])
                #     fig.add_trace(go.Scatter3d(
                #         x=initial_frame[:, 0],
                #         y=initial_frame[:, 2],
                #         z=initial_frame[:, 1],
                #         mode='markers',
                #         marker=dict(size=5, color="red"),
                #         name='Initial Frame'
                #     ))

                #     # Add frames for animation
                #     frames = [go.Frame(data=[go.Scatter3d(
                #         x=np.array(frame)[:, 0],
                #         y=np.array(frame)[:, 2],
                #         z=np.array(frame)[:, 1],
                #         mode='markers',
                #         marker=dict(size=5, color="red")
                #     )]) for frame in skeleton_data]

                #     fig.frames = frames

                #     # Update layout for the animation
                #     fig.update_layout(
                #         title="Skeleton 3D Visualization",
                #         scene=dict(
                #             xaxis=dict(title=dict(text="X"), range=[-1, 1]),  # Set the range directly on the axis
                #             yaxis=dict(title=dict(text="Z"), range=[-4, -1]),  # Set the range directly on the axis
                #             zaxis=dict(title=dict(text="Y"), range=[-2, 2]),   # Set the range directly on the axis
                #             aspectmode="manual"
                #         ),
                #         updatemenus=[{
                #             'buttons': [
                #                 {
                #                     'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True}],
                #                     'label': 'Play',
                #                     'method': 'animate'
                #                 },
                #                 {
                #                     'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                #                     'label': 'Pause',
                #                     'method': 'animate'
                #                 }
                #             ],
                #             'direction': 'left',
                #             'pad': {'r': 10, 't': 87},
                #             'showactive': False,
                #             'type': 'buttons',
                #             'x': 0.1,
                #             'xanchor': 'right',
                #             'y': 0,
                #             'yanchor': 'top'
                #         }]
                #     )

                #     # Display the figure in Streamlit
                #     st.plotly_chart(fig)

                else:
                    st.error("No skeleton data found!")
            else:
                st.error("Failed to load skeleton data!")
        else:
            st.error("Error occurred while extracting skeleton!")
    else:
        st.error("File upload failed!")