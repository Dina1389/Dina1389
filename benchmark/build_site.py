#!/usr/bin/env python3
"""Builds mokha-benchmark.html (interactive page) from ./data and site_template.html."""
import json, os, re
from build_workbook import CENTERS, EXACTNESS, load, num, find, P90
HERE = os.path.dirname(os.path.abspath(__file__))
SHORT = {"mokha": "مركز المخا", "sanaa": "مركز صنعاء", "abaad": "أبعاد", "ypc": "السياسات اليمنية", "deeproot": "ديب روت",
         "semc": "الإعلام الاقتصادي", "ajcs": "الجزيرة للدراسات", "acrps": "المركز العربي", "ahram": "الأهرام",
         "epc": "الإمارات للسياسات", "chatham": "Chatham House", "carnegie": "Carnegie", "icg": "Crisis Group",
         "brookings": "Brookings", "csis": "CSIS"}
GL = {"نحن": "مركزنا", "يمني مماثل": "يمني", "عربي": "عربي", "أجنبي": "دولي"}
D = load()
XP = json.load(open(os.path.join(HERE, "data", "x_profiles.json"), encoding="utf8"))
centers, posts = [], []
for slug, name, grp, country in CENTERS:
    d = D[slug]; wc = d["website_counts"]; x = XP.get(slug)
    fo, ch = d.get("followers", []), d.get("social_channels_observed", [])
    def fol(p):
        f = find(fo, "platform", p)
        return num(f["value"]) if f and "actual" in str(f.get("type")) and num(f.get("value")) is not None else None
    t90 = wc["d90"].get("total"); bl = wc["d90"].get("by_language", {})
    tb = d["type_breakdown_90d"]; g = lambda k: num(tb.get(k)) or 0
    mix = None
    if any(tb.get(k) is not None for k in ("research", "reports", "analysis")):
        mix = {"research": g("research"), "reports": g("reports"), "analysis": g("analysis"), "newsev": g("news") + g("events"),
               "media": g("video") + g("podcast") + (0 if slug == "brookings" else g("infographic")), "other": g("other")}
    tgc = find(ch, "platform", "telegram")
    centers.append({
        "slug": slug, "name": name.replace(" (حسابنا)", ""), "short": SHORT[slug], "group": "يمني" if grp == "يمني مماثل" else ("يمني" if grp == "نحن" else grp),
        "groupLabel": GL[grp], "site30": wc["d30"].get("total"), "site90": t90, "ar90": bl.get("ar") if t90 is not None else None,
        "en90": bl.get("en") if t90 is not None else None, "exact": EXACTNESS.get(slug, ""), "lower": "حدّ أدنى" in EXACTNESS.get(slug, ""),
        "x_followers": x["followers"] if x else None, "x_total": x["total_posts"] if x else None,
        "x_views": x["sample_median_views"] if x else None, "x_rate": round(x["view_rate"] * 100, 1) if x and x.get("view_rate") else None,
        "yt": fol("youtube"), "tg": fol("telegram"), "tg90": (tgc or {}).get("posts_90d"),
        "mix": mix, "mixTotal": sum(mix.values()) if mix else 0,
        "strengths": d.get("strengths", []), "weaknesses": d.get("weaknesses", []), "opps": d.get("opportunities_for_mokha", []),
    })
    for p in d.get("social_posts", []):
        v = num(p.get("views"))
        if v is None: continue
        posts.append({"c": SHORT[slug], "p": str(p.get("platform")).split(" ")[0], "d": str(p.get("date"))[:10], "t": (p.get("summary") or "")[:150], "v": v, "e": num(p.get("likes")), "u": p.get("url")})
    if x:
        for t in x["tweets"]:
            st = t.get("stats") or {}
            if "view" not in st: continue
            posts.append({"c": SHORT[slug], "p": "X", "d": t["date"][:10], "t": ("[مثبّت] " if t.get("pinned") else "") + t.get("text", "")[:150], "v": st["view"],
                          "e": st.get("like", 0) + st.get("repost", 0) + st.get("repl", 0), "u": t["url"]})
me = next(c for c in centers if c["slug"] == "mokha")
me["opps"] = ["إنشاء صفحة مؤسسة على لينكد إن بدل الملف الشخصي", "فيديو قصير أسبوعي من الأوراق الحديثة", "حزمة من 4 منشورات لكل إصدار بدل منشور واحد",
              "ملء الفراغ الإنجليزي عن اليمن: YPC وDeepRoot بلا نشر في الفترة", "الإحاطة الشهرية بصيغة «3 اتجاهات و3 تنبيهات»",
              "عناوين رقمية قصيرة: منشور «3 ساعات صارت 26 ساعة» المثبّت نال 1,485 مشاهدة على X"]
posts.sort(key=lambda p: -p["v"])
data = {"centers": centers, "posts": posts, "plan": json.load(open(os.path.join(HERE, "plan_30d.json"), encoding="utf8")),
        "mokha_other": XP["_mokha_other"], "mokha_tr": {k: XP["mokha_tr"][k] for k in ("followers", "total_posts", "url")}}
tpl = open(os.path.join(HERE, "site_template.html"), encoding="utf8").read()
out = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
open(os.path.join(HERE, "mokha-benchmark.html"), "w", encoding="utf8").write(out)
print("posts", len(posts), "bytes", len(out))
