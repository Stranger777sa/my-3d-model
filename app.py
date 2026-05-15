import streamlit as st
import plotly.graph_objects as go
import numpy as np

# دعم اللغة العربية في العنوان
st.title("نموذج ثلاثي أبعاد تفاعلي")

# صنع بيانات لشكل كروي (3D Sphere)
phi = np.linspace(0, 2*np.pi, 100)
theta = np.linspace(0, np.pi, 100)
phi, theta = np.meshgrid(phi, theta)

x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale='Viridis')])

fig.update_layout(title='يمكنك تحريك هذه الكرة بلمس الشاشة', 
                  scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))

st.plotly_chart(fig)
