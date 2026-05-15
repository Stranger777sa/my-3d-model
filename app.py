import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

# ==========================================
# 1. الثوابت الفيزيائية الكونية (SI Units)
# ==========================================
B0 = 3.12e-5          # شدة المجال المغناطيسي عند خط الاستواء للأرض (تسلا)
RE = 6371000.0        # نصف قطر الأرض الفعلي بالأمتار (مقياس المسافة المرجعي)
q = 1.602e-19         # شحنة الجسيم المشحون (كولوم)
m = 1.673e-27         # كتلة البروتون (كيلوغرام)

# ==========================================
# 2. معادلات الحقل المغناطيسي لثنائي القطب
# ==========================================
def get_B_field(pos):
    """حساب متجه المجال المغناطيسي ثلاثي الأبعاد عند أي إحداثي"""
    r_mag = np.linalg.norm(pos)
    if r_mag < 0.1 * RE:
        return np.array([0.0, 0.0, 0.0])
    # عزم ثنائي القطب للأرض موجه للمحور Z المقلوب
    M = np.array([0.0, 0.0, -B0 * (RE**3)])
    dot_prod = 3.0 * np.dot(M, pos) / (r_mag**5)
    B = dot_prod * pos - M / (r_mag**3)
    return B

def trace_field_line(start_pos, steps=200, ds=0.05*RE):
    """تتبع ورسم خط مجال مغناطيسي منفرد من نقطة البداية"""
    line = [start_pos]
    pos = np.array(start_pos)
    for _ in range(steps):
        B = get_B_field(pos)
        B_norm = np.linalg.norm(B)
        if B_norm == 0: break
        # التحرك باتجاه متجه الحقل
        pos = pos + (B / B_norm) * ds
        if np.linalg.norm(pos) < RE: break  # التوقف إذا ضرب الأرض
        line.append(pos)
    return np.array(line)

# ==========================================
# 3. محرك المحاكاة الفيزيائي (قوة لورنتز)
# ==========================================
def simulate_particle(start_pos, start_vel, dt, max_steps=5000):
    """محاكاة حركة جسيم مشحون تحت تأثير قوة لورنتز خطوة بخطوة"""
    pos = np.array(start_pos, dtype=float)
    vel = np.array(start_vel, dtype=float)
    
    pos_hist = []
    vel_hist = []
    
    for _ in range(max_steps):
        r_mag = np.linalg.norm(pos)
        # شروط التوقف: الاصطدام بالأرض أو الهروب بعيداً في الفضاء
        if r_mag < RE or r_mag > 6.0 * RE:
            break
            
        pos_hist.append(pos.copy())
        vel_hist.append(np.linalg.norm(vel))
        
        # F = q * (V x B)
        B = get_B_field(pos)
        F = q * np.cross(vel, B)
        acc = F / m
        
        # تحديث الحركة (Boris/Euler-Cromer Algorithm)
        vel += acc * dt
        pos += vel * dt
        
    return np.array(pos_hist), np.array(vel_hist)

# ==========================================
# 4. تشغيل السيناريو الشامل للمشروع
# ==========================================
print("[-] جاري بناء البيئة المغناطيسية الفلكية...")

# تحديد نقطة الانطلاق فوق إحداثيات الجزائر بارتفاع (1.5 من نصف قطر الأرض)
# تحويل الإحداثيات الجغرافية (شمال 28، شرق 2) إلى كارتيزية
lat, lon = np.radians(28.0), np.radians(2.0)
r_start = 1.6 * RE
x0 = r_start * np.cos(lat) * np.cos(lon)
y0 = r_start * np.cos(lat) * np.sin(lon)
z0 = r_start * np.sin(lat)
injection_point = np.array([x0, y0, z0])

# إعداد خطوط المجال المغناطيسي الخلفية (للعرض الجمالي والفيزيائي)
field_lines = []
for phi in np.linspace(0, 2*np.pi, 8):
    for r_edge in [1.5*RE, 2.0*RE]:
        st = np.array([r_edge*np.cos(phi), r_edge*np.sin(phi), 0.1*RE])
        field_lines.append(trace_field_line(st, steps=150, ds=0.08*RE))
        field_lines.append(trace_field_line(st, steps=150, ds=-0.08*RE))

# توليد دفق الجسيمات (3 جسيمات بزوايا حقن مختلفة لإنشاء شكل الحزام)
particles_data = []
dt = 2e-6  # خطوة زمنية متناهية الصغر لتلائم سرعة الجسيمات العالية
v_mag = 4.5e6  # سرعة الجسيمات (متر/ثانية) - سرعة الرياح الشمسية النمطية

# زوايا الحقن المختلفة لصنع المظهر الحلزوني المتشعب
injection_angles = [
    np.array([-0.3, 0.9, -0.2]),
    np.array([-0.25, 0.85, -0.35]),
    np.array([-0.35, 0.95, -0.1])
]

print("[-] جاري بث الجسيمات المشحونة وحساب نقاط المرآة والمغزلية...")
for idx, angle in enumerate(injection_angles):
    v_dir = angle / np.linalg.norm(angle)
    v_start = v_dir * v_mag
    p_hist, v_mags = simulate_particle(injection_point, v_start, dt, max_steps=6000)
    particles_data.append((p_hist, v_mags))

# ==========================================
# 5. التصميم والرسم ثلاثي الأبعاد الاحترافي
# ==========================================
fig = plt.figure(figsize=(14, 11))
ax = fig.add_subplot(111, projection='3d')

# أ. رسم كوكب الأرض في المركز ككرة مرجعية زرقاء
u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
xs = RE * np.cos(u) * np.sin(v)
ys = RE * np.sin(u) * np.sin(v)
zs = RE * np.cos(v)
ax.plot_surface(xs, ys, zs, color="#104E8B", alpha=0.3, edgecolor='#4682B4', linewidth=0.3)

# ب. رسم خطوط الشبكة المغناطيسية لحماية الكوكب
for line in field_lines:
    if len(line) > 1:
        ax.plot(line[:,0], line[:,1], line[:,2], color="cyan", alpha=0.15, linestyle="--")

# ج. رسم وتلوين مسارات الجسيمات (الشرر النحاسي المتأرجح) بشكل ديناميكي
for idx, (p_hist, v_mags) in enumerate(particles_data):
    if len(p_hist) < 2: continue
    
    # تقسيم المسار لقطع صغيرة لتلوينها ديناميكياً حسب السرعة
    points = p_hist.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # استخدام التدرج اللوني النحاسي المتوهج (Copper/YlOrRd)
    norm = plt.Normalize(v_mags.min(), v_mags.max())
    lc = Line3DCollection(segments, cmap='copper', norm=norm, alpha=0.85)
    lc.set_array(v_mags[:-1])
    lc.set_linewidth(1.8)
    line_ref = ax.add_collection3d(lc)

# د. إسقاط وتحديد نقاط التحكم والمرايا الأساسية
ax.scatter(injection_point[0], injection_point[1], injection_point[2], 
           color="#FFD700", s=150, edgecolor='black', marker='*', label="نقطة بث البلازما (فوق الجزائر)")

# تحديد أقصى نقطة وصل إليها الجسيم الأول قبل الارتداد (نقطة المرآة الجنوبية)
p_hist_1 = particles_data[0][0]
mirror_idx = np.argmin(particles_data[0][1]) # المكان الذي تباطأت فيه السرعة لأقل حد قبل الارتداد
if mirror_idx < len(p_hist_1):
    ax.scatter(p_hist_1[mirror_idx, 0], p_hist_1[mirror_idx, 1], p_hist_1[mirror_idx, 2], 
               color="#FF3030", s=120, edgecolor='black', label="منطقة حبس وانعكاس الجسيمات (المرآة المغناطيسية)")

# ==========================================
# 6. اللمسات النهائية للمخطط وحفظه
# ==========================================
ax.set_title("المشروع النهائي: نظام الحبس المغناطيسي الشامل وأحزمة الجسيمات المتأرجحة", fontsize=16, pad=20)
ax.set_xlabel("X (أمتار)")
ax.set_ylabel("Y (أمتار)")
ax.set_zlabel("Z (أمتار)")

# إضافة شريط التدرج اللوني لمعرفة سرعة الجسيم اللحظية
cbar = fig.colorbar(line_ref, ax=ax, pad=0.1, shrink=0.6)
cbar.set_label('السرعة اللحظية للجسيم (متر / ثانية)', rotation=270, labelpad=20)

# موازنة أبعاد الرؤية الفضائية ثلاثية الأبعاد
limit = 3.5 * RE
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-limit, limit)
ax.legend(loc="upper left")

# حفظ وعرض النتيجة النهائية للمشروع الشامل
plt.savefig("comprehensive_plasma_simulation.png", dpi=300, bbox_inches='tight')
plt.show()

print("[+] مبروك! تم تشغيل النظام الشامل وحفظ التصميم الفلكي فائق الدقة باسم: comprehensive_plasma_simulation.png")
