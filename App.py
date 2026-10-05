import colorsys
import math
import streamlit as st

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Color Match Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: #777;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .color-box {
            height: 180px;
            border-radius: 18px;
            margin: 10px 0 20px 0;
            border: 2px solid rgba(0,0,0,0.12);
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }

        .result-card {
            padding: 20px;
            border-radius: 15px;
            background-color: #f7f7f7;
            border: 1px solid #e5e5e5;
            margin-bottom: 15px;
        }

        .match-score {
            font-size: 42px;
            font-weight: 800;
            text-align: center;
        }

        .small-label {
            color: #777;
            font-size: 13px;
            font-weight: 600;
        }

        div[data-testid="stMetric"] {
            background-color: #fafafa;
            padding: 12px;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def normalize_hex(hex_color):
    """Validate and normalize HEX color."""
    value = hex_color.strip().replace("#", "")

    if len(value) == 3:
        value = "".join(char * 2 for char in value)

    if len(value) != 6:
        raise ValueError("HEX color must contain 6 characters.")

    try:
        int(value, 16)
    except ValueError:
        raise ValueError("Invalid HEX color.")

    return f"#{value.upper()}"


def hex_to_rgb(hex_color):
    """Convert HEX to RGB."""
    value = normalize_hex(hex_color).replace("#", "")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def rgb_to_hex(r, g, b):
    """Convert RGB to HEX."""
    return "#{:02X}{:02X}{:02X}".format(
        int(r), int(g), int(b)
    )


def rgb_to_hsl(r, g, b):
    """Convert RGB to HSL."""
    r_norm = r / 255
    g_norm = g / 255
    b_norm = b / 255

    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

    return (
        round(h * 360),
        round(s * 100),
        round(l * 100),
    )


def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV."""
    r_norm = r / 255
    g_norm = g / 255
    b_norm = b / 255

    h, s, v = colorsys.rgb_to_hsv(
        r_norm,
        g_norm,
        b_norm,
    )

    return (
        round(h * 360),
        round(s * 100),
        round(v * 100),
    )


def relative_luminance(r, g, b):
    """Calculate WCAG relative luminance."""
    values = [r / 255, g / 255, b / 255]

    converted = []

    for value in values:
        if value <= 0.03928:
            converted.append(value / 12.92)
        else:
            converted.append(
                ((value + 0.055) / 1.055) ** 2.4
            )

    return (
        0.2126 * converted[0]
        + 0.7152 * converted[1]
        + 0.0722 * converted[2]
    )


def contrast_ratio(rgb1, rgb2):
    """Calculate WCAG contrast ratio."""
    lum1 = relative_luminance(*rgb1)
    lum2 = relative_luminance(*rgb2)

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    return (lighter + 0.05) / (darker + 0.05)


def color_distance(rgb1, rgb2):
    """
    Calculate normalized RGB Euclidean distance.
    Returns a value between 0 and 1.
    """
    distance = math.sqrt(
        (rgb1[0] - rgb2[0]) ** 2
        + (rgb1[1] - rgb2[1]) ** 2
        + (rgb1[2] - rgb2[2]) ** 2
    )

    maximum_distance = math.sqrt(3 * (255 ** 2))

    return distance / maximum_distance


def similarity_percentage(rgb1, rgb2):
    """Calculate approximate RGB similarity."""
    distance = color_distance(rgb1, rgb2)
    similarity = (1 - distance) * 100

    return max(0, min(100, similarity))


def get_match_label(score):
    """Return a human-readable match description."""
    if score >= 95:
        return "Excellent Match 🎯"
    elif score >= 85:
        return "Very Good Match 🟢"
    elif score >= 70:
        return "Good Match 🔵"
    elif score >= 50:
        return "Moderate Match 🟡"
    elif score >= 30:
        return "Low Match 🟠"
    else:
        return "Very Different 🔴"


def get_color_values(hex_color):
    """Return all major color values."""
    rgb = hex_to_rgb(hex_color)

    hsl = rgb_to_hsl(*rgb)
    hsv = rgb_to_hsv(*rgb)

    return {
        "HEX": normalize_hex(hex_color),
        "RGB": rgb,
        "HSL": hsl,
        "HSV": hsv,
        "Luminance": relative_luminance(*rgb),
    }


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">🎨 Color Match Studio</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Analyze colors, compare color values, and find out how closely two colors match."
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("🎨 Color Settings")

st.sidebar.markdown(
    "Enter colors using HEX values or choose them visually."
)

color_1 = st.sidebar.color_picker(
    "Primary Color",
    "#3366FF",
)

color_2 = st.sidebar.color_picker(
    "Comparison Color",
    "#33CC99",
)

st.sidebar.divider()

st.sidebar.info(
    """
    **Supported values**

    • HEX  
    • RGB  
    • HSL  
    • HSV  
    • Relative luminance  
    • Contrast ratio  
    • Color similarity
    """
)

# ---------------------------------------------------------
# Main columns
# ---------------------------------------------------------
try:
    color_1 = normalize_hex(color_1)
    color_2 = normalize_hex(color_2)

    rgb_1 = hex_to_rgb(color_1)
    rgb_2 = hex_to_rgb(color_2)

except ValueError as error:
    st.error(str(error))
    st.stop()

values_1 = get_color_values(color_1)
values_2 = get_color_values(color_2)

# ---------------------------------------------------------
# Color Preview
# ---------------------------------------------------------
st.subheader("Color Preview")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="color-box"
             style="background-color:{color_1};">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"### Primary Color `{color_1}`")

with col2:
    st.markdown(
        f"""
        <div class="color-box"
             style="background-color:{color_2};">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"### Comparison Color `{color_2}`")

# ---------------------------------------------------------
# Color Values
# ---------------------------------------------------------
st.divider()
st.subheader("Color Values")

value_col1, value_col2 = st.columns(2)

with value_col1:
    st.markdown("### Primary Color")

    st.metric(
        "HEX",
        values_1["HEX"],
    )

    st.metric(
        "RGB",
        str(values_1["RGB"]),
    )

    st.metric(
        "HSL",
        str(values_1["HSL"]),
    )

    st.metric(
        "HSV",
        str(values_1["HSV"]),
    )

with value_col2:
    st.markdown("### Comparison Color")

    st.metric(
        "HEX",
        values_2["HEX"],
    )

    st.metric(
        "RGB",
        str(values_2["RGB"]),
    )

    st.metric(
        "HSL",
        str(values_2["HSL"]),
    )

    st.metric(
        "HSV",
        str(values_2["HSV"]),
    )

# ---------------------------------------------------------
# Matching Analysis
# ---------------------------------------------------------
st.divider()
st.subheader("🔍 Color Matching Analysis")

similarity = similarity_percentage(
    rgb_1,
    rgb_2,
)

contrast = contrast_ratio(
    rgb_1,
    rgb_2,
)

label = get_match_label(similarity)

match_col1, match_col2, match_col3 = st.columns(3)

with match_col1:
    st.metric(
        "Color Similarity",
        f"{similarity:.2f}%",
    )

with match_col2:
    st.metric(
        "Contrast Ratio",
        f"{contrast:.2f}:1",
    )

with match_col3:
    st.metric(
        "Match Result",
        label,
    )

st.progress(
    int(round(similarity)),
    text=f"Similarity: {similarity:.2f}%",
)

# ---------------------------------------------------------
# Difference
# ---------------------------------------------------------
st.subheader("📊 Color Difference")

difference_col1, difference_col2, difference_col3 = st.columns(3)

difference_r = abs(rgb_1[0] - rgb_2[0])
difference_g = abs(rgb_1[1] - rgb_2[1])
difference_b = abs(rgb_1[2] - rgb_2[2])

with difference_col1:
    st.metric(
        "Red Difference",
        difference_r,
    )

with difference_col2:
    st.metric(
        "Green Difference",
        difference_g,
    )

with difference_col3:
    st.metric(
        "Blue Difference",
        difference_b,
    )

# ---------------------------------------------------------
# Accessibility
# ---------------------------------------------------------
st.divider()
st.subheader("♿ Accessibility Check")

if contrast >= 7:
    accessibility = "AAA — Excellent contrast"
elif contrast >= 4.5:
    accessibility = "AA — Good contrast for normal text"
elif contrast >= 3:
    accessibility = "AA Large Text — Suitable for large text"
else:
    accessibility = "Low contrast — May be difficult to read"

st.info(
    f"**WCAG Contrast Result:** {accessibility}"
)

# ---------------------------------------------------------
# CSS Color Code
# ---------------------------------------------------------
st.divider()
st.subheader("💻 CSS Usage")

css_code = f"""/* Primary Color */
.primary-color {{
    color: {color_1};
    background-color: {color_1};
}}

/* Comparison Color */
.comparison-color {{
    color: {color_2};
    background-color: {color_2};
}}
"""

st.code(
    css_code,
    language="css",
)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.divider()

st.caption(
    "🎨 Color Match Studio • Built with Python & Streamlit"
)
