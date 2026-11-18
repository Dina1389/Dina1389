"""يرندر index.html إلى فيديو ستوري 1080x1920 مع الصوت.
الاستخدام:  python render.py            (الفيديو كامل)
            python render.py --stills    (لقطات فحص فقط في مجلد stills/)
"""
import pathlib, subprocess, sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent.resolve()
FPS, DUR = 30, 55.28
W, H = 1080, 1920
OUT = ROOT / "dina_claude_story_1080x1920.mp4"
CHECK_TIMES = [2.5, 5.5, 8.5, 10.5, 15.5, 20.5, 24, 27.8, 30.5, 33.5, 35.8, 41.8, 44.5, 46.5, 48.8, 54.5]


def main():
    stills = "--stills" in sys.argv
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium") if pathlib.Path("/opt/pw-browsers/chromium").exists() else p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.goto((ROOT / "index.html").as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("""Promise.all(['500','700','800'].flatMap(w => [
            document.fonts.load(w + ' 60px Tajawal', 'كلود abc'),
            document.fonts.load(w + ' 60px "IBM Plex Mono"', 'abc')])).then(() => document.fonts.ready)""")
        if not page.evaluate("document.fonts.check('800 60px Tajawal', 'كلود')"):
            sys.exit("خط Tajawal ما تحمّل — تأكد من الاتصال بالإنترنت (Google Fonts).")

        if stills:
            out = ROOT / "stills"
            out.mkdir(exist_ok=True)
            for t in CHECK_TIMES:
                page.evaluate(f"render({t})")
                page.screenshot(path=str(out / f"t_{t:05.1f}.png"))
            print("Stills saved to", out)
        else:
            ff = subprocess.Popen(
                ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                 "-i", str(ROOT / "voice.mp3"), "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                 "-movflags", "+faststart", str(OUT)],
                stdin=subprocess.PIPE)
            n = int(DUR * FPS)
            for i in range(n):
                page.evaluate(f"render({i / FPS})")
                ff.stdin.write(page.screenshot(type="png"))
                if i % 150 == 0:
                    print(f"{i}/{n}")
            ff.stdin.close()
            ff.wait()
            print("Done:", OUT)
        browser.close()


if __name__ == "__main__":
    main()
