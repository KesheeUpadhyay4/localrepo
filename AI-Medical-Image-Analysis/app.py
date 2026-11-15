
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageStat, ImageDraw
from datetime import datetime
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Medical Image Analysis",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.main {
    background-color: #f5f8fc;
}
.main-title {
    font-size: 35px;
    font-weight: bold;
    color: #12345a;
}
.subtitle {
    color: #536579;
    font-size: 16px;
}
.info-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #dce5ef;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def make_histogram(gray_image):
    """Create a brightness histogram using Pillow."""
    histogram = gray_image.histogram()

    chart = Image.new("RGB", (520, 190), "white")
    draw = ImageDraw.Draw(chart)

    left = 35
    top = 15
    width = 465
    height = 135

    draw.line(
        (left, top + height, left + width, top + height),
        fill="black",
        width=2
    )

    max_value = max(histogram) if max(histogram) > 0 else 1

    points = []

    for i, value in enumerate(histogram):
        x = left + int((i / 255) * width)
        y = top + height - int((value / max_value) * height)
        points.append((x, y))

    draw.line(points, fill="#1677c8", width=2)

    draw.text((left, 158), "Dark (0)", fill="black")
    draw.text((left + width - 65, 158), "Bright (255)", fill="black")
    draw.text((220, 175), "Pixel brightness distribution", fill="black")

    return chart


def analyze_image(image):
    """Calculate basic image statistics."""
    gray = ImageOps.grayscale(image)
    stats = ImageStat.Stat(gray)

    histogram = gray.histogram()
    total_pixels = sum(histogram)

    dark_pixels = sum(histogram[:86])
    middle_pixels = sum(histogram[86:171])
    bright_pixels = sum(histogram[171:])

    return {
        "width": image.width,
        "height": image.height,
        "mean_brightness": round(stats.mean[0], 2),
        "contrast_stddev": round(stats.stddev[0], 2),
        "dark_percentage": round(dark_pixels / total_pixels * 100, 2),
        "middle_percentage": round(middle_pixels / total_pixels * 100, 2),
        "bright_percentage": round(bright_pixels / total_pixels * 100, 2),
        "gray_image": gray
    }


def process_image(image, operation, contrast, brightness):
    """Apply the selected image-processing operation."""

    result = image.convert("RGB")

    if operation == "Grayscale":
        result = ImageOps.grayscale(result).convert("RGB")

    elif operation == "Noise Reduction":
        result = result.filter(ImageFilter.MedianFilter(size=3))

    elif operation == "Edge Detection":
        result = result.filter(ImageFilter.FIND_EDGES)

    elif operation == "Sharpen":
        result = result.filter(ImageFilter.SHARPEN)

    elif operation == "Auto Contrast":
        result = ImageOps.autocontrast(result)

    elif operation == "Original":
        pass

    result = ImageEnhance.Contrast(result).enhance(contrast)
    result = ImageEnhance.Brightness(result).enhance(brightness)

    return result


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🏥 Medical AI System")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Image Analysis",
        "Image Processing",
        "Image Statistics",
        "About Project"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Educational image-processing prototype. "
    "Not intended for medical diagnosis."
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "file_size" not in st.session_state:
    st.session_state.file_size = None

if "processed_image" not in st.session_state:
    st.session_state.processed_image = None


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">🏥 AI Medical Image Analysis System</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Basic medical image visualization, processing and statistical analysis</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Supported Formats", "5")

    with col2:
        st.metric("Processing Methods", "6")

    with col3:
        status = "Image Uploaded" if st.session_state.uploaded_image else "Waiting"
        st.metric("System Status", status)

    st.subheader("Available Modules")

    modules = [
        ("📤 Image Analysis", "Upload and view medical images."),
        ("🖼️ Image Processing", "Apply grayscale, smoothing, sharpening and edge detection."),
        ("📊 Image Statistics", "Calculate brightness, contrast and histogram."),
        ("📄 Report", "Download a basic image analysis report.")
    ]

    for title, description in modules:
        with st.container(border=True):
            st.subheader(title)
            st.write(description)

    st.warning(
        "This system performs general image processing. "
        "It does not provide disease detection or medical diagnosis."
    )


# --------------------------------------------------
# IMAGE ANALYSIS / UPLOAD
# --------------------------------------------------

elif page == "Image Analysis":

    st.title("📤 Medical Image Upload and Analysis")

    uploaded_file = st.file_uploader(
        "Upload a medical image",
        type=["jpg", "jpeg", "png", "bmp", "tif", "tiff"]
    )

    if uploaded_file is not None:

        try:
            image = Image.open(uploaded_file)
            image.load()

            # Use the first frame for multi-frame TIFF files.
            if getattr(image, "n_frames", 1) > 1:
                image.seek(0)
                image.load()

            image = ImageOps.exif_transpose(image).convert("RGB")

            st.session_state.uploaded_image = image.copy()
            st.session_state.file_name = uploaded_file.name
            st.session_state.file_size = len(uploaded_file.getvalue())

        except Exception as error:
            st.error(f"Unable to open this image: {error}")

    if st.session_state.uploaded_image is not None:

        image = st.session_state.uploaded_image

        st.success("Image uploaded successfully!")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Original Medical Image")
            st.image(image, use_container_width=True)

        with col2:
            st.subheader("Image Information")

            st.write("**File Name:**", st.session_state.file_name)
            st.write("**Image Format:**", "Supported image")
            st.write("**Width:**", image.width, "pixels")
            st.write("**Height:**", image.height, "pixels")
            st.write("**Colour Mode:** RGB")
            st.write(
                "**File Size:**",
                round(st.session_state.file_size / 1024, 2),
                "KB"
            )

        st.info(
            "Image successfully loaded. You can now use the "
            "Image Processing and Image Statistics modules."
        )

    else:
        st.info("Please upload an image to begin.")


# --------------------------------------------------
# IMAGE PROCESSING
# --------------------------------------------------

elif page == "Image Processing":

    st.title("🖼️ Medical Image Processing")

    if st.session_state.uploaded_image is None:

        st.warning("Please upload an image in the Image Analysis module first.")

    else:

        original = st.session_state.uploaded_image

        operation = st.selectbox(
            "Choose Image Processing Method",
            [
                "Original",
                "Grayscale",
                "Noise Reduction",
                "Edge Detection",
                "Sharpen",
                "Auto Contrast"
            ]
        )

        contrast = st.slider(
            "Contrast",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )

        brightness = st.slider(
            "Brightness",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )

        if st.button("Process Image", type="primary"):

            result = process_image(
                original,
                operation,
                contrast,
                brightness
            )

            st.session_state.processed_image = result

        if st.session_state.processed_image is not None:

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original Image")
                st.image(original, use_container_width=True)

            with col2:
                st.subheader("Processed Image")
                st.image(
                    st.session_state.processed_image,
                    use_container_width=True
                )

            buffer = BytesIO()
            st.session_state.processed_image.save(buffer, format="PNG")

            st.download_button(
                "⬇️ Download Processed Image",
                data=buffer.getvalue(),
                file_name="processed_medical_image.png",
                mime="image/png"
            )


# --------------------------------------------------
# IMAGE STATISTICS
# --------------------------------------------------

elif page == "Image Statistics":

    st.title("📊 Medical Image Statistics")

    if st.session_state.uploaded_image is None:

        st.warning("Upload an image first in the Image Analysis module.")

    else:

        image = st.session_state.uploaded_image
        result = analyze_image(image)

        st.subheader("Statistical Analysis")

        col1, col2, col3 = st.columns(3)

        col1.metric("Width", f"{result['width']} px")
        col2.metric("Height", f"{result['height']} px")
        col3.metric(
            "Total Pixels",
            f"{result['width'] * result['height']:,}"
        )

        st.divider()

        col1, col2 = st.columns(2)

        col1.metric(
            "Mean Brightness",
            result["mean_brightness"]
        )

        col2.metric(
            "Contrast (Standard Deviation)",
            result["contrast_stddev"]
        )

        st.subheader("Brightness Distribution")

        col1, col2, col3 = st.columns(3)

        col1.metric("Dark Pixels", f"{result['dark_percentage']}%")
        col2.metric("Middle Pixels", f"{result['middle_percentage']}%")
        col3.metric("Bright Pixels", f"{result['bright_percentage']}%")

        st.subheader("Image Histogram")

        histogram_image = make_histogram(result["gray_image"])

        st.image(histogram_image, use_container_width=True)

        st.caption(
            "The histogram shows how pixel brightness values are distributed. "
            "These statistics are not clinical measurements."
        )

        # Download report

        report = f"""
AI MEDICAL IMAGE ANALYSIS SYSTEM
================================

Analysis Date: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}

File Name: {st.session_state.file_name}

Image Dimensions:
Width: {result['width']} pixels
Height: {result['height']} pixels
Total Pixels: {result['width'] * result['height']}

IMAGE STATISTICS
----------------

Mean Brightness: {result['mean_brightness']}
Contrast Standard Deviation: {result['contrast_stddev']}

Dark Pixels: {result['dark_percentage']}%
Middle Brightness Pixels: {result['middle_percentage']}%
Bright Pixels: {result['bright_percentage']}%

DISCLAIMER
----------

This report contains basic image-processing statistics only.
It does not provide a medical diagnosis or disease prediction.
Consult a qualified medical professional for interpretation.
"""

        st.download_button(
            "⬇️ Download Analysis Report",
            data=report,
            file_name="medical_image_analysis_report.txt",
            mime="text/plain"
        )


# --------------------------------------------------
# ABOUT PROJECT
# --------------------------------------------------

elif page == "About Project":

    st.title("ℹ️ About the Project")

    st.write("""
    ### AI Medical Image Analysis System

    This is an educational Python project designed to demonstrate
    basic medical image visualization and processing.

    ### Technologies Used

    - Python
    - Streamlit
    - Pillow (PIL)
    - Python datetime
    - Python BytesIO

    ### Image Processing Techniques

    1. Grayscale conversion
    2. Median filtering
    3. Edge detection
    4. Image sharpening
    5. Automatic contrast enhancement
    6. Brightness and contrast statistics

    ### Supported Image Formats

    - JPG
    - JPEG
    - PNG
    - BMP
    - TIFF

    ### Limitations

    - Does not diagnose diseases.
    - Does not identify the medical scan type.
    - Does not use a trained medical AI model.
    - Does not support DICOM in this version.
    - Does not replace a radiologist or doctor.
    """)

    st.warning(
        "Never use this educational application to make medical decisions."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Medical Image Analysis System | Python & Streamlit | "
    "Educational use only – Not for clinical diagnosis."
)
