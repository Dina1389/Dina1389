#!/usr/bin/env python3
"""Builds the Mokha Center benchmarking workbook from the per-center JSON files in ./data.

Usage: python3 build_workbook.py   (writes مقارنة_معيارية_مركز_المخا.xlsx next to this script)
"""
import json, os, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "مقارنة_معيارية_مركز_المخا.xlsx")

P30 = ("2026-10-15", "2026-11-13")
P90 = ("2026-08-16", "2026-11-13")
NA = "غير متاح"
PENDING = "لم يكتمل الجمع"

CENTERS = [  # slug, name, group, country  (order of the original file)
    ("mokha", "مركز المخا للدراسات الاستراتيجية (حسابنا)", "نحن", "تركيا/اليمن"),
    ("sanaa", "مركز صنعاء للدراسات الاستراتيجية", "يمني مماثل", "اليمن"),
    ("abaad", "مركز أبعاد للدراسات والبحوث", "يمني مماثل", "اليمن"),
    ("ypc", "مركز السياسات اليمنية (Yemen Policy Center)", "يمني مماثل", "ألمانيا"),
    ("deeproot", "ديب روت (DeepRoot Consulting)", "يمني مماثل", "بريطانيا/اليمن"),
    ("semc", "مركز الدراسات والإعلام الاقتصادي", "يمني مماثل", "اليمن"),
    ("ajcs", "مركز الجزيرة للدراسات", "عربي", "قطر"),
    ("acrps", "المركز العربي للأبحاث ودراسة السياسات", "عربي", "قطر"),
    ("ahram", "مركز الأهرام للدراسات السياسية والاستراتيجية", "عربي", "مصر"),
    ("epc", "مركز الإمارات للسياسات", "عربي", "الإمارات"),
    ("chatham", "Chatham House", "أجنبي", "بريطانيا"),
    ("carnegie", "Carnegie Endowment", "أجنبي", "أمريكا"),
    ("icg", "International Crisis Group", "أجنبي", "بلجيكا"),
    ("brookings", "Brookings Institution", "أجنبي", "أمريكا"),
    ("csis", "CSIS", "أجنبي", "أمريكا"),
]

# How complete the website count is, per center (from the collectors' method notes)
EXACTNESS = {
    "mokha": "عدّ كامل (واجهة WordPress)",
    "sanaa": "عدّ مرصود؛ العربية حدّ أدنى",
    "abaad": "عدّ كامل (مسح معرّفات المواد)",
    "ypc": "عدّ كامل (لا نشر في الفترتين)",
    "deeproot": "عدّ كامل (لا نشر في الفترتين)",
    "semc": "عدّ كامل (واجهة WordPress)",
    "ajcs": "عدّ كامل تقريبًا (100 أو 101)",
    "acrps": "حدّ أدنى مرصود (الموقع يحجب القوائم)",
    "carnegie": "عدّ كامل (خريطة الموقع + فتح الصفحات)",
    "chatham": "حدّ أدنى (الموقع يحجب القراءة الآلية؛ RSS + فهرس أخبار)",
    "icg": "حدّ أدنى (الموقع يحجب القراءة الآلية؛ RSS + فهرس أخبار)",
}

FONT = "Arial"
HFILL = PatternFill("solid", fgColor="1F4E79")
SUBFILL = PatternFill("solid", fgColor="DDEBF7")
OWNFILL = PatternFill("solid", fgColor="FFF2CC")
INFILL = PatternFill("solid", fgColor="FFFF00")
GREY = PatternFill("solid", fgColor="F2F2F2")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def load():
    d = {}
    for slug, *_ in CENTERS:
        p = os.path.join(DATA, slug + ".json")
        if os.path.exists(p):
            d[slug] = json.load(open(p, encoding="utf8"))
    return d


def num(v):
    """Numeric value or None (handles '2.82K', '1,402', 'غير متاح')."""
    if isinstance(v, (int, float)):
        return v
    if not isinstance(v, str):
        return None
    s = v.strip().replace(",", "")
    m = re.fullmatch(r"([\d.]+)\s*([KkMm]?)", s)
    if not m:
        return None
    x = float(m.group(1)) * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()]
    return int(x) if x == int(x) else x


def val(v):
    n = num(v)
    if n is not None:
        return n
    return v if (isinstance(v, str) and v.strip()) else NA


def sheet(wb, title, headers, widths, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.sheet_view.rightToLeft = True
    ws.append(headers)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in ws[1]:
        c.font = Font(name=FONT, bold=True, color="FFFFFF", size=11)
        c.fill = HFILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[1].height = 42
    ws.freeze_panes = "B2"
    return ws


def finish(ws, own_col=1, link_cols=(), wrap=True):
    for row in ws.iter_rows(min_row=2):
        own = isinstance(row[own_col - 1].value, str) and "المخا" in row[own_col - 1].value
        for c in row:
            if c.font.name != FONT or not c.font.bold:
                c.font = Font(name=FONT, size=10, bold=c.font.bold, color=c.font.color)
            c.alignment = Alignment(vertical="top", wrap_text=wrap,
                                    horizontal="right" if isinstance(c.value, str) else "center")
            c.border = BORDER
            if own and c.fill.fgColor.rgb in (None, "00000000"):
                c.fill = OWNFILL
        for i in link_cols:
            c = row[i - 1]
            if isinstance(c.value, str) and c.value.startswith("http"):
                c.hyperlink = c.value
                c.font = Font(name=FONT, size=10, color="0563C1", underline="single")
    ws.auto_filter.ref = ws.dimensions


def find(lst, key, *names):
    for x in lst or []:
        p = str(x.get(key, "")).lower()
        if any(p.startswith(n) for n in names):
            return x
    return None


def build():
    D = load()
    wb = Workbook()

    # ---------- 1. README ----------
    ws = wb.active
    ws.title = "اقرأني والمنهجية"
    ws.sheet_view.rightToLeft = True
    ws.column_dimensions["A"].width = 150
    missing = [n for s, n, *_ in CENTERS if s not in D]
    lines = [
        ("مقارنة معيارية: مركز المخا للدراسات الاستراتيجية مقابل 14 مركز فكر", "t"),
        ("تاريخ الجمع: 13–16 نوفمبر 2026. الملف الأصلي المرفق لم يُعدَّل؛ هذا ملف جديد.", ""),
        ("الفترتان الزمنيتان", "h"),
        (f"آخر 30 يومًا: من {P30[0]} إلى {P30[1]}", ""),
        (f"آخر 90 يومًا: من {P90[0]} إلى {P90[1]}", ""),
        ("قيد أساسي على البيانات (يجب قراءته قبل استخدام الأرقام)", "h"),
        ("منصات X وفيسبوك ولينكد إن تحجب القراءة بلا تسجيل دخول (جدار دخول أو رفض 402/403). لم يُجرَ أي تجاوز لهذه الحواجز. لذلك: عدد المنشورات والتفاعل والمتابعين على هذه المنصات الثلاث «غير متاح» لكل المراكز، عدا عيّنة واحدة من لينكد إن (Chatham House، 10 منشورات).", ""),
        ("البديل المستخدم: (1) المواقع الرسمية — عدّ فعلي لكل ما نُشر في الفترتين بتاريخه ورابطه؛ (2) قنوات تيليغرام العامة — عدد المنشورات والمشاهدات؛ (3) يوتيوب — المشتركون ومشاهدات الفيديو؛ (4) روابط الحسابات الرسمية مأخوذة من ترويسة/تذييل موقع كل مركز.", ""),
        ("إنتاج الموقع ليس عدد منشورات المنصات: هو مؤشر على حجم المحتوى المتاح للترويج، لا على نشاط الحسابات.", ""),
        ("أرقام المتابعين المعروضة لقطة حالية فقط، ولا تدل على نمو خلال الفترة. ورقة «النمو» في الملف الأصلي تبقى بلا بيانات.", ""),
        ("المشاهدات على يوتيوب وتيليغرام وعدّادات المواقع تراكمية حتى تاريخ الرصد، لا خاصة بالفترة.", ""),
        ("دليل الأوراق", "h"),
        ("ملخص المقارنة: صف لكل مركز — إنتاج الموقع في الفترتين، المعدل الأسبوعي (محسوب بمعادلة)، اللغات، المتابعون المتاحون.", ""),
        ("تحليل المنصات: صف لكل مركز × منصة — رابط الحساب الرسمي، المتابعون، المنشورات، التفاعل المرصود، وحالة الإتاحة.", ""),
        ("أنواع المحتوى / الموضوعات: توزيع إصدارات 90 يومًا حسب النوع، وأكثر الموضوعات تناولًا.", ""),
        ("أبرز المنشورات: كل منشور اجتماعي أمكن رصده بأرقامه ورابطه.  |  الإصدارات التفصيلية: كل مادة موقع مرصودة.", ""),
        ("الأساليب والترويج / قوة وضعف وفرص: ملاحظات نوعية مع رابط الدليل.  |  المصادر والقيود: كل مصدر وما استُخدم فيه.", ""),
        ("خطة 30 يومًا: خطة تنفيذية لحسابات مركز المخا.  |  إدخال بيانات المخا: قالب لتعبئة أرقام X وفيسبوك ولينكد إن من لوحات التحليلات الداخلية.", ""),
        ("دلالات الألوان والقيم", "h"),
        ("الصف الأصفر الفاتح = مركز المخا.  الخلية الصفراء الفاقعة = مطلوب تعبئتها من بياناتكم الداخلية.  الخط الأزرق = رقم مرصود مُدخل؛ الخط الأسود = معادلة.", ""),
        ("«غير متاح» = غير معروض للعامة بلا تسجيل دخول.  «حدّ أدنى» = الموقع حجب جزءًا من قوائمه فالعدد الحقيقي أكبر.  «مقتطف بحث/طرف ثالث» = رقم غير مؤكد من المنصة نفسها.", ""),
    ]
    if missing:
        lines.append(("مراكز لم يكتمل جمع بياناتها في هذه النسخة: " + "، ".join(missing), "w"))
    for i, (t, k) in enumerate(lines, 1):
        c = ws.cell(i, 1, t)
        c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="right")
        c.font = Font(name=FONT, size=14 if k == "t" else 11, bold=k in ("t", "h", "w"),
                      color="FFFFFF" if k == "h" else ("C00000" if k == "w" else "000000"))
        if k == "h":
            c.fill = HFILL

    # ---------- 2. Summary ----------
    H = ["المركز", "المجموعة", "الدولة", "إصدارات الموقع — 30 يومًا", "إصدارات الموقع — 90 يومًا",
         "المعدل الأسبوعي (30 يومًا)", "المعدل الأسبوعي (90 يومًا)", "عربي — 90 يومًا", "إنجليزي — 90 يومًا",
         "لغات أخرى — 90 يومًا", "دقة العدّ", "مشتركو يوتيوب", "مشتركو تيليغرام",
         "متابعو X", "متابعو فيسبوك", "متابعو لينكد إن", "ملاحظة على أرقام المتابعين", "الموقع"]
    ws = sheet(wb, "ملخص المقارنة", H, [38, 12, 13, 12, 12, 12, 12, 10, 10, 10, 30, 13, 13, 14, 14, 14, 44, 30])
    blue = Font(name=FONT, size=10, color="0000FF")
    for r, (slug, name, grp, country) in enumerate(CENTERS, 2):
        d = D.get(slug)
        if not d:
            ws.append([name, grp, country] + [PENDING] * 15)
            continue
        wc = d["website_counts"]
        bl = wc["d90"].get("by_language", {})
        other = sum(v for k, v in bl.items() if k not in ("ar", "en") and isinstance(v, (int, float)))
        fo = d.get("followers", [])
        notes = []

        def fol(*names):
            x = find(fo, "platform", *names)
            if not x or num(x.get("value")) is None:
                return NA
            if "actual" not in str(x.get("type", "")):
                notes.append(f"{x['platform']}: {x.get('type')}، تاريخ الرقم: {x.get('figure_date') or 'غير مؤرخ'}")
            return num(x["value"])
        row = [name, grp, country, wc["d30"]["total"], wc["d90"]["total"],
               f"=IF(ISNUMBER(D{r}),ROUND(D{r}/(30/7),1),\"-\")", f"=IF(ISNUMBER(E{r}),ROUND(E{r}/(90/7),1),\"-\")",
               bl.get("ar", 0), bl.get("en", 0), other, EXACTNESS.get(slug, ""),
               fol("youtube"), fol("telegram"), fol("x"), fol("facebook"), fol("linkedin"),
               "؛ ".join(notes) if notes else ("أرقام يوتيوب/تيليغرام فعلية من المنصة" if any(num(x.get("value")) is not None for x in fo) else "لا رقم متابعين متاح للعامة"),
               d["website"]]
        ws.append(row)
        for col in (4, 5, 8, 9, 10, 12, 13, 14, 15, 16):
            if isinstance(ws.cell(r, col).value, (int, float)):
                ws.cell(r, col).font = blue
                ws.cell(r, col).number_format = "#,##0"
    n = len(CENTERS) + 1
    ws.append([])
    ws.append(["متوسط المراكز اليمنية المماثلة (دون المخا)", "", "", f'=ROUND(AVERAGEIF(B2:B{n},"يمني مماثل",D2:D{n}),1)',
               f'=ROUND(AVERAGEIF(B2:B{n},"يمني مماثل",E2:E{n}),1)'])
    ws.append(["ترتيب المخا بين المراكز المكتمل جمعها حسب إصدارات 90 يومًا", "", "", "", f"=RANK(E2,E2:E{n})"])
    ws.append(["تنبيه: المراكز ذات «حدّ أدنى» إنتاجها الحقيقي أكبر؛ لا تُقارن أحجام المراكز الدولية الكبرى بمركز متخصص صغير مباشرة."])
    finish(ws, link_cols=(18,))
    for rr in (n + 2, n + 3, n + 4):
        ws.cell(rr, 1).font = Font(name=FONT, size=10, bold=True)

    # ---------- 3. Platforms ----------
    H = ["المركز", "المنصة", "رابط الحساب الرسمي", "طريقة التحقق من الحساب", "المتابعون/المشتركون", "تاريخ الرقم",
         "نوع الرقم", "منشورات — 30 يومًا", "منشورات — 90 يومًا", "المعدل الأسبوعي (30)", "المعدل الأسبوعي (90)",
         "التفاعل الظاهر (مشاهدات/إعجابات)", "حالة الإتاحة والملاحظات"]
    ws = sheet(wb, "تحليل المنصات", H, [34, 12, 40, 34, 14, 13, 18, 11, 11, 11, 11, 46, 60])
    r = 2
    WALL = "محجوب بلا تسجيل دخول — عدد المنشورات والتفاعل والمتابعين غير متاح للعامة"
    for slug, name, grp, country in CENTERS:
        d = D.get(slug)
        if not d:
            for pf in ("X", "Facebook", "LinkedIn"):
                ws.append([name, pf] + [PENDING] * 11)
                r += 1
            continue
        acc = d["accounts"]
        fo = d.get("followers", [])
        ch = d.get("social_channels_observed", [])
        plats = [("X", "x", ("x",)), ("Facebook", "facebook", ("facebook",)), ("LinkedIn", "linkedin", ("linkedin",))]
        others = {str(o.get("platform", "")).lower(): o.get("url", "") for o in acc.get("other", [])}
        for pf, key, pre in plats:
            a = acc.get(key, {}) or {}
            if slug == "chatham" and pf == "LinkedIn":
                a = {"url": "https://www.linkedin.com/company/chathamhouse", "verified_via": "فُتحت الصفحة العامة مباشرة في 13 نوفمبر 2026"}
            f = find(fo, "platform", *pre)
            fv = num(f.get("value")) if f else None
            note = WALL
            if slug == "chatham" and pf == "LinkedIn":
                note = "عيّنة مرصودة: 10 منشورات بين 10 و13 نوفمبر 2026 (≈2.5 منشور/يوم) — انظر «أبرز المنشورات». باقي الفترة غير متاح."
            if "/in/" in str(a.get("url", "")):
                note = "تنبيه: الرابط المنشور في الموقع ملف شخصي (/in/) وليس صفحة مؤسسة (/company/). " + note
            ws.append([name, pf, a.get("url") or NA, a.get("verified_via") or NA,
                       fv if fv is not None else NA,
                       (f.get("figure_date") or "غير مؤرخ") if fv is not None else "",
                       (f.get("type") or "") if fv is not None else "",
                       NA, NA, "-", "-",
                       "متوسط العيّنة: 48 تفاعلًا/منشور؛ الأعلى 208 (فيديو)" if (slug == "chatham" and pf == "LinkedIn") else NA,
                       note])
            r += 1
        for pf, pre in (("Telegram", ("telegram",)), ("YouTube", ("youtube",))):
            f = find(fo, "platform", *pre)
            c = find(ch, "platform", *pre)
            url = (c or {}).get("url") or next((u for k, u in others.items() if k.startswith(pre[0])), "")
            fv = num(f.get("value")) if f else None
            p30, p90 = (c or {}).get("posts_30d"), (c or {}).get("posts_90d")
            if fv is None and not isinstance(p30, (int, float)) and not isinstance(p90, (int, float)):
                continue
            ws.append([name, pf, url or NA, "مرتبط من موقع المركز / معاينة عامة", fv if fv is not None else NA,
                       (f or {}).get("figure_date", ""), (f or {}).get("type", "") if fv is not None else "",
                       p30 if isinstance(p30, (int, float)) else NA, p90 if isinstance(p90, (int, float)) else NA,
                       f'=IF(ISNUMBER(H{r}),ROUND(H{r}/(30/7),1),"-")', f'=IF(ISNUMBER(I{r}),ROUND(I{r}/(90/7),1),"-")',
                       str((c or {}).get("typical_views") or NA), str((c or {}).get("note") or "")])
            r += 1
        wc = d["website_counts"]
        ws.append([name, "الموقع", d["website"], "الموقع الرسمي", "", "", "", wc["d30"]["total"], wc["d90"]["total"],
                   f'=IF(ISNUMBER(H{r}),ROUND(H{r}/(30/7),1),"-")', f'=IF(ISNUMBER(I{r}),ROUND(I{r}/(90/7),1),"-")',
                   "", EXACTNESS.get(slug, "") + " — " + str(wc.get("method", ""))[:400]])
        r += 1
    finish(ws, link_cols=(3,))
    for row in ws.iter_rows(min_row=2):
        for i in (4, 7, 8):
            if isinstance(row[i].value, (int, float)):
                row[i].font = blue
                row[i].number_format = "#,##0"
        if row[7].value == NA and row[1].value in ("X", "Facebook", "LinkedIn"):
            for c in row[7:9]:
                c.fill = GREY

    # ---------- 4. Content types ----------
    keys = [("research", "أبحاث/دراسات"), ("reports", "تقارير"), ("analysis", "تحليلات/تقدير موقف"), ("news", "أخبار/بيانات"),
            ("video", "فيديو"), ("infographic", "إنفوجرافيك"), ("podcast", "بودكاست"), ("events", "فعاليات"), ("other", "أخرى/غير مصنف")]
    H = ["المركز", "المجموعة"] + [k[1] for k in keys] + ["المجموع", "النوع الأكثر", "حصة النوع الأكثر", "ملاحظة التصنيف"]
    ws = sheet(wb, "أنواع المحتوى (90 يومًا)", H, [38, 12] + [11] * 9 + [10, 18, 11, 70])
    for r, (slug, name, grp, _) in enumerate(CENTERS, 2):
        d = D.get(slug)
        if not d:
            ws.append([name, grp] + [PENDING] * 9)
            continue
        tb = d["type_breakdown_90d"]
        vals = [num(tb.get(k)) or 0 for k, _ in keys]
        note = tb.get("note") or d.get("type_breakdown_note") or ("المواد العربية فقط (33)؛ النسخ الإنجليزية الـ19 ترجمات لها" if slug == "mokha" else "")
        ws.append([name, grp] + vals + [f"=SUM(C{r}:K{r})",
                  f'=IF(L{r}=0,"لا نشر",INDEX($C$1:$K$1,MATCH(MAX(C{r}:K{r}),C{r}:K{r},0)))',
                  f'=IF(L{r}=0,"-",MAX(C{r}:K{r})/L{r})', str(note)[:600]])
        ws.cell(r, 14).number_format = "0%"
        for col in range(3, 12):
            ws.cell(r, col).font = blue
    ws.append(["ملاحظة: التصنيف يتبع تسميات كل موقع ثم يُجمع في فئات موحّدة؛ المجموع قد يختلف عن إصدارات الموقع عند احتساب النسخ المترجمة مرة واحدة أو إضافة فيديو يوتيوب."])
    finish(ws)

    # ---------- 5. Topics ----------
    ws = sheet(wb, "الموضوعات", ["المركز", "المجموعة", "الترتيب", "الموضوع", "عدد المواد (90 يومًا)", "ملاحظة"], [38, 12, 9, 52, 14, 70])
    for slug, name, grp, _ in CENTERS:
        d = D.get(slug)
        if not d:
            ws.append([name, grp, "", PENDING])
            continue
        tt = d.get("top_topics") or []
        if not tt:
            ws.append([name, grp, "", "لا مواد في الفترة", 0, str(d.get("top_topics_note", ""))[:300]])
        for i, t in enumerate(tt[:8], 1):
            ws.append([name, grp, i, t.get("topic"), val(t.get("count")), str(d.get("top_topics_note", ""))[:300] if i == 1 else ""])
    finish(ws)

    # ---------- 6. Top posts ----------
    H = ["المركز", "المنصة", "تاريخ المنشور", "داخل نافذة 90 يومًا؟", "ملخص المنشور", "المشاهدات", "الإعجابات/التفاعلات",
         "التعليقات", "المشاركات", "نوع البيانات", "رابط المنشور", "مصدر الرصد"]
    ws = sheet(wb, "أبرز المنشورات", H, [32, 11, 12, 11, 64, 12, 12, 11, 11, 14, 46, 46])
    rows = []
    for slug, name, grp, _ in CENTERS:
        d = D.get(slug)
        if not d:
            continue
        for p in d.get("social_posts", []):
            dt = str(p.get("date", ""))[:10]
            rows.append([name, p.get("platform"), dt, "نعم" if P90[0] <= dt <= P90[1] else "لا (خارج النافذة)",
                         p.get("summary"), val(p.get("views")), val(p.get("likes")), val(p.get("comments")),
                         val(p.get("shares")), "فعلي" if p.get("data_type") == "actual" else "مقتطف بحث",
                         p.get("url"), p.get("source_url")])
    li = os.path.join(DATA, "li_chatham_sample.json")
    if os.path.exists(li):
        for p in json.load(open(li, encoding="utf8")):
            rows.append(["Chatham House", "LinkedIn", p["date"], "نعم", f"{p['summary']} [{p['media']}]", NA, p["likes"],
                         p["comments"], NA, "فعلي (عيّنة)", p["url"], p["source_url"]])
    order = {n: i for i, (_, n, *_r) in enumerate(CENTERS)}
    rows.sort(key=lambda x: (order.get(x[0], 99), -(x[5] if isinstance(x[5], (int, float)) else (x[6] if isinstance(x[6], (int, float)) else 0))))
    for x in rows:
        ws.append(x)
    finish(ws, link_cols=(11, 12))
    for row in ws.iter_rows(min_row=2):
        for i in (5, 6, 7, 8):
            if isinstance(row[i].value, (int, float)):
                row[i].font = blue
                row[i].number_format = "#,##0"

    # ---------- 7. Items ----------
    H = ["المركز", "التاريخ", "ضمن آخر 30 يومًا؟", "العنوان", "النوع (تسمية الموقع)", "الموضوع", "اللغة", "الرابط"]
    ws = sheet(wb, "الإصدارات التفصيلية", H, [32, 12, 10, 70, 24, 34, 8, 60])
    for slug, name, grp, _ in CENTERS:
        d = D.get(slug)
        if not d:
            continue
        for it in sorted(d.get("items", []), key=lambda x: str(x.get("date")), reverse=True):
            dt = str(it.get("date", ""))[:10]
            ws.append([name, dt, "نعم" if P30[0] <= dt <= P30[1] else "لا", it.get("title"), it.get("type"),
                       it.get("topic"), it.get("language"), it.get("url")])
    ws.append(["ملاحظة: للمراكز الكبرى (Carnegie، Chatham House، Crisis Group) تُعرض أحدث 40 مادة فقط؛ الأعداد الكاملة في «ملخص المقارنة»."])
    finish(ws, link_cols=(8,))

    # ---------- 8. Styles & promotion ----------
    ws = sheet(wb, "الأساليب والترويج", ["المركز", "المحور", "الملاحظة", "رابط الدليل"], [34, 20, 110, 60])
    for slug, name, grp, _ in CENTERS:
        d = D.get(slug)
        if not d:
            ws.append([name, "", PENDING])
            continue
        ws.append([name, "أسلوب العناوين", d.get("headline_style"), d["website"]])
        ws.append([name, "أسلوب التصميم", d.get("design_style"), d["website"]])
        ws.append([name, "اللغات", "، ".join(map(str, d.get("languages", []))), d["website"]])
        for t in d.get("promotion_tactics", []):
            ws.append([name, "أسلوب ترويج", t.get("tactic"), t.get("evidence_url")])
    finish(ws, link_cols=(4,))

    # ---------- 9. SWOT ----------
    ws = sheet(wb, "قوة وضعف وفرص", ["المركز", "المجموعة", "النوع", "البند"], [34, 12, 22, 130])
    for slug, name, grp, _ in CENTERS:
        d = D.get(slug)
        if not d:
            ws.append([name, grp, "", PENDING])
            continue
        for k, lab in (("strengths", "نقطة قوة"), ("weaknesses", "نقطة ضعف"), ("opportunities_for_mokha", "فرصة لمركز المخا")):
            for x in d.get(k, []):
                ws.append([name, grp, lab, x])
    finish(ws)

    # ---------- 10. Sources ----------
    ws = sheet(wb, "المصادر والقيود", ["المركز", "النوع", "المصدر / القيد", "ما استُخدم فيه", "تاريخ الوصول"], [34, 12, 80, 70, 16])
    for slug, name, grp, _ in CENTERS:
        d = D.get(slug)
        if not d:
            ws.append([name, "قيد", "لم يكتمل جمع بيانات هذا المركز في هذه النسخة (توقف بسبب حد الاستخدام)", "", ""])
            continue
        acc = str(d.get("accessed", ""))[:60]
        for s in d.get("sources", []):
            ws.append([name, "مصدر", s.get("url"), s.get("used_for"), acc])
        for x in d.get("limitations", []):
            ws.append([name, "قيد", x, "", acc])
    finish(ws, link_cols=(3,))

    # ---------- 11. 30-day plan ----------
    plan = json.load(open(os.path.join(HERE, "plan_30d.json"), encoding="utf8"))
    H = ["الأسبوع", "اليوم", "المنصة", "المهمة", "الصيغة/القالب", "المستند إليه في المقارنة", "مؤشر النجاح", "المسؤول", "الحالة"]
    ws = sheet(wb, "خطة 30 يومًا", H, [14, 9, 20, 62, 30, 44, 36, 14, 12])
    for p in plan:
        ws.append([p["week"], p["day"], p["platform"], p["task"], p["format"], p["basis"], p["kpi"], "", ""])
    finish(ws, own_col=9)
    for row in ws.iter_rows(min_row=2):
        row[7].fill = INFILL
        row[8].fill = INFILL

    # ---------- 12. Internal input template ----------
    H = ["المنصة", "الفترة", "تاريخ البداية", "تاريخ النهاية", "المتابعون أول الفترة", "المتابعون آخر الفترة", "عدد المنشورات",
         "إجمالي الظهور/الوصول", "إجمالي التفاعلات", "النمو المطلق", "نسبة النمو", "المعدل الأسبوعي للنشر", "معدل التفاعل لكل منشور", "رابط أعلى منشور"]
    ws = sheet(wb, "إدخال بيانات المخا", H, [16, 12, 13, 13, 14, 14, 12, 14, 14, 12, 11, 13, 14, 44])
    ex = ["(مثال) X", "30 يومًا", P30[0], P30[1], 4200, 4350, 26, 58000, 1900]
    rows = [ex] + [[pf, per, a, b, None, None, None, None, None] for pf in ("X", "Facebook", "LinkedIn", "Telegram")
                   for per, (a, b) in (("30 يومًا", P30), ("90 يومًا", P90))]
    for i, x in enumerate(rows, 2):
        days = 30 if x[1] == "30 يومًا" else 90
        ws.append(x + [f'=IF(OR(E{i}="",F{i}=""),"",F{i}-E{i})', f'=IF(OR(E{i}="",F{i}="",E{i}=0),"",F{i}/E{i}-1)',
                       f'=IF(G{i}="","",ROUND(G{i}/({days}/7),1))', f'=IF(OR(G{i}="",I{i}="",G{i}=0),"",ROUND(I{i}/G{i},1))', ""])
        ws.cell(i, 11).number_format = "0.0%"
    ws.append(["التعبئة: الخلايا الصفراء من لوحات التحليلات (X Analytics، Meta Business Suite، LinkedIn Page Analytics). الصف الأول مثال توضيحي بأرقام افتراضية — احذفوه. تيليغرام 30/90 يومًا: 11/42 منشورًا مرصودة فعليًا."])
    finish(ws, own_col=14)
    for row in ws.iter_rows(min_row=3, max_row=len(rows) + 1):
        for c in row[4:9]:
            c.fill = INFILL
        row[13].fill = INFILL
    ws["G9"], ws["G10"] = 11, 42
    ws["G9"].font = ws["G10"].font = blue
    for c in ws[2]:
        c.fill = GREY

    wb.save(OUT)
    print("saved", OUT, "centers with data:", len(D), "/", len(CENTERS))


if __name__ == "__main__":
    build()
