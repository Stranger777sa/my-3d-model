import streamlit as st
import plotly.graph_objects as go
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="تحليل النموذج التفاعلي", layout="wide")

# العنوان العربي
st.title("تفاعلي")
st.write("يمكنك تحريك هذه الكرة بلمس الشاشة")

# --- محاكاة البيانات ---
# توليد سطح الكرة الأرضية (تقريبي)
lons = np.linspace(-180, 180, 50)
lats = np.linspace(-90, 90, 50)
lons, lats = np.meshgrid(lons, lats)
x = np.cos(np.radians(lats)) * np.cos(np.radians(lons))
y = np.cos(np.radians(lats)) * np.sin(np.radians(lons))
z = np.sin(np.radians(lats))

# --- محاكاة المؤثرات (بلازما) ---
# بلازما متوهجة على خط الاستواء
plasma_eq = 1.0 - np.abs(np.radians(lats)) * 2.0
plasma_eq = np.clip(plasma_eq, 0, 1)

# بلازما إضافية لتمثيل "نيفادا" و "اليابان"
plasma_spots = np.zeros_like(lats)
# نيفادا
plasma_spots[ (np.abs(lons - -116) < 10) & (np.abs(lats - 38) < 10) ] = 0.8
# اليابان
plasma_spots[ (np.abs(lons - 138) < 10) & (np.abs(lats - 36) < 10) ] = 0.9
# أفريقيا (منطقة التفريغ)
plasma_spots[ (np.abs(lons - 20) < 10) & (np.abs(lats - 10) < 10) ] = 0.7

plasma_intensity = np.maximum(plasma_eq * 0.7, plasma_spots)

# --- بناء المجسم ثلاثي الأبعاد ---
fig = go.Figure()

# 1. طبقة السطح التفاعلي (الأرض + البلازما)
fig.add_trace(go.Surface(
    x=x, y=y, z=z,
    surfacecolor=plasma_intensity, # استخدام شدة البلازما لتحديد الألوان
    colorscale=[
        [0, 'rgb(30, 40, 50)'],    # خلفية داكنة للأرض
        [0.4, 'rgb(100, 150, 200)'], # محيطات (تقريبي)
        [0.6, 'rgb(255, 100, 0)'],  # برتقالي (بداية التوهج)
        [1.0, 'rgb(255, 200, 50)']   # أصفر (أعلى توهج)
    ],
    showscale=True, # إظهار مقياس الألوان (Colorbar)
    colorbar=dict(
        title="",
        tickvals=[0, 1],
        ticktext=["MIN", "MAX"],
        thickness=15,
        len=0.5,
        x=1.05
    ),
    hovertemplate='Intensity: %{surfacecolor:.2f}<extra></extra>'
))

# 2. طبقة خطوط الحقل المغناطيسي (تقريبية)
theta = np.linspace(0, 2*np.pi, 24)
for t in theta:
    r = np.linspace(1.2, 1.8, 10)
    mag_x = r * np.cos(t)
    mag_y = r * np.sin(t)
    mag_z = np.zeros_like(mag_x)
    fig.add_trace(go.Scatter3d(
        x=mag_x, y=mag_y, z=mag_z,
        mode='lines',
        line=dict(color='rgba(100, 200, 255, 0.3)', width=1),
        showlegend=False,
        hoverinfo='none'
    ))

# إعدادات العرض
fig.update_layout(
    scene=dict(
        xaxis_visible=False,
        yaxis_visible=False,
        zaxis_visible=False,
        bgcolor='rgb(10, 15, 20)', # خلفية فضاء داكنة
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
)

# عرض المجسم في Streamlit
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- إضافة مقاييس البيانات المحاكية (كما في الصورة المرجعية) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("---")
    st.markdown("**بيانات التيار الأرضي المحاكية:**")
    st.info("أنشطة غير مسبوقة على خط الاستواء")
    st.info("شدة البلازما: 0.85 (في نيفادا)")
    st.info("شدة البلازما: 0.91 (في اليابان)")

with col2:
    st.markdown("---")
    st.markdown("**مقياس الحقل المغناطيسي (محاكاة):**")
    # محاكاة الرسم البياني للانخفاض
    mag_field_data = np.linspace(100, 85, 20) + np.random.normal(0, 1, 20)
    chart_data = {"الوقت": np.arange(20), "شدة الحقل (%)": mag_field_data}
    st.line_chart(chart_data, x="الوقت", y="شدة الحقل (%)", color="#ff5555")
    st.warning("انخفاض بنسبة 15%")
