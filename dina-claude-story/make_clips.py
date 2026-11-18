"""يقص مقاطع الشاشة المتحركة من الفيديو المرجعي (1024x576) إلى clips/*.mp4.
الاستخدام:  python make_clips.py path/to/reference.mp4
كل مقطع: (الاسم, بداية بالثواني في الفيديو المرجعي, المدة = مدة المشهد, x, y, w, h)
"""
import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).parent.resolve()
CLIPS = [
    ("apps",        117.2, 3.2, 49, 102, 628, 353),   # 3.6-6.8   شعارات التطبيقات تدخل
    ("wb_title",     24.0, 2.0, 49, 102, 628, 353),   # 9.0-11.0  الخط الزمني ينرسم
    ("wb",           29.5, 5.6, 49, 102, 628, 353),   # 11.0-16.6 مؤشرات الزملاء ثم مربع التحديد
    ("sh_title",     47.2, 1.8, 49, 102, 628, 353),   # 16.6-18.4 الجدول يتبنى
    ("sh",           50.0, 3.0, 49, 102, 628, 353),   # 18.4-21.4 تعديل الخلايا
    ("budget",      149.0, 3.2, 177, 101, 367, 353),  # 21.4-24.6 الميزانية
    ("dt_title",     81.8, 2.2, 49, 102, 628, 353),   # 24.6-26.8 الداشبورد يتعبى
    ("design",       89.0, 3.6, 49, 102, 628, 353),   # 28.4-32.0 لوحة Design
    ("share",       103.2, 2.2, 49, 102, 628, 353),   # 32.0-34.2 زر Share
    ("confluence",  121.0, 2.4, 49, 102, 628, 353),   # 36.8-39.2 Confluence داخل Claude
    ("speed",       132.6, 2.0, 49, 102, 628, 353),   # 39.2-41.2 at the speed of thought
]

def main():
    src = sys.argv[1]
    out = ROOT / "clips"; out.mkdir(exist_ok=True)
    for n, ss, d, x, y, w, h in CLIPS:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", src, "-t", str(d + 0.2),
                        "-vf", f"crop={w}:{h}:{x}:{y},fps=30", "-an", "-c:v", "libx264", "-crf", "10",
                        "-preset", "slow", "-pix_fmt", "yuv444p", str(out / f"{n}.mp4")], check=True)
        print(n)

if __name__ == "__main__":
    main()
