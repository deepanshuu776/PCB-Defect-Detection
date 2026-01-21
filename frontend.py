import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# Configuration
API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="PCB Defect Detector", layout="wide")

st.title("🔍 PCB Defect Detection System")
st.markdown("### Major Project Implementation")
st.markdown("Upload a PCB image to detect manufacturing defects (Open, Short, Mousebite, Spur, etc.)")

# Sidebar
st.sidebar.header("Control Panel")
uploaded_file = st.sidebar.file_uploader("Choose a PCB Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Display original image
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Original Image", use_container_width=True)
        
    if st.sidebar.button("Analyze PCB"):
        with st.spinner("Scanning for defects..."):
            try:
                # Send to backend
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Decode and display processed image
                    img_data = base64.b64decode(data["image_base64"])
                    result_img = Image.open(BytesIO(img_data))
                    
                    with col2:
                        st.image(result_img, caption="Detected Defects", use_container_width=True)
                    
                    # Display Stats
                    st.success(f"Analysis Complete! Found {data['defect_count']} defects.")
                    
                    if data["defect_count"] > 0:
                        st.write("### Detailed Defect Report")
                        for det in data["detections"]:
                            st.warning(f"⚠️ **{det['class']}** - Confidence: {det['confidence']:.2%}")
                    else:
                        st.balloons()
                        st.info("✅ No defects detected. PCB is clean.")
                        
                else:
                    st.error("Error connecting to backend.")
            except Exception as e:
                st.error(f"Connection failed. Is the backend running? Error: {e}")

else:
    st.info("Please upload an image to begin.")