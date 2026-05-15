import numpy as np
import matplotlib.pyplot as plt

# إحداثيات النقاط (نصف قطر الأرض الافتراضي = 1)
# الجزائر (شمال) والقطب الجنوبي (جنوب)
lat_algeria, lon_algeria = 28.0, 2.0
lat_south, lon_south = -80.0, 0.0

def geo_to_cartesian(lat, lon, r=1.0):
    theta = np.radians(90 - lat)
    phi = np.radians(lon)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.cos(theta)
    z = r * np.sin(theta) * np.sin(phi)
    return np.array([x, y, z])

p_algeria = geo_to_cartesian(lat_algeria, lon_algeria)
p_south = geo_to_cartesian(lat_south, lon_south)

# محاكاة خط المجال المغناطيسي كمنحنى بين النقطتين
t = np.linspace(0, 1, 200)
# نقطة الانبعاج المغناطيسي (الارتفاع في الغلاف المغناطيسي)
control_point = (p_algeria + p_south) * 1.5 

# حساب مسار خط المجال (Bezier Curve)
field_line = np.zeros((200, 3))
for i, tv in enumerate(t):
    field_line[i] = (1-tv)**2 * p_south + 2*(1-tv)*tv * control_point + tv**2 * p_algeria

# توليد حركة الجسيمات الحلزونية (الشرر النحاسي) وحساب نقاط المرآة
steps = 500
particle_path = []

print("[-] جاري حساب نقاط المرآة المغناطيسية (B_m)...")
for i in range(steps):
    # حركة ترددية ذهاباً وإياباً
    tv = np.abs(np.sin(i * 0.02)) 
    
    # تحديد موقع الجسيم الأساسي على خط المجال
    idx = int(tv * 199)
    base_pos = field_line[idx]
    
    # تأثير الحركة المغزلية (Gyro-motion) الذي يضيق عند الاقتراب من الأرض
    gyro_radius = 0.15 * np.sin(tv * np.pi) 
    angle = i * 0.5
    
    x = base_pos[0] + np.cos(angle) * gyro_radius
    y = base_pos[1]
    z = base_pos[2] + np.sin(angle) * gyro_radius
    
    particle_path.append([x, y, z])

particle_path = np.array(particle_path)

# إعداد الرسم ثلاثي الأبعاد
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# رسم الأرض كمرجع مبسط
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
xs = np.cos(u)*np.sin(v)
ys = np.cos(v)
zs = np.sin(u)*np.sin(v)
ax.plot_wireframe(xs, ys, zs, color="blue", alpha=0.1)

# رسم خط المجال المغناطيسي الرئيسي
ax.plot(field_line[:,0], field_line[:,1], field_line[:,2], color="cyan", label="خط المجال المغناطيسي", alpha=0.6)

# رسم خيوط التفريغ البلازمي النحاسي (حركة الجسيمات المتأرجحة)
ax.plot(particle_path[:,0], particle_path[:,1], particle_path[:,2], color="#D2691E", linewidth=1.5, label="الشرر النحاسي (تفريغ البلازما)")

# تحديد نقاط المرآة
ax.scatter(p_algeria[0], p_algeria[1], p_algeria[2], color="orange", s=100, label="نقطة المرآة: الجزائر")
ax.scatter(p_south[0], p_south[1], p_south[2], color="red", s=100, label="نقطة المرآة: القطب الجنوبي")

ax.set_title("تصور ثلاثي الأبعاد لصورة المرآة والشرر النحاسي")
ax.legend()

# إذا كانت المنصة تدعم العرض المباشر (مثل Colab) سيعرضها فوراً، وإلا فسيحفظها كصورة
plt.savefig("mirror_image_output.png")
plt.show() 
print("[+] تم توليد التصور وحفظه بنجاح باسم: mirror_image_output.png")
