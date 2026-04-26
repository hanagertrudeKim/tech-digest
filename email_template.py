"""Tech Digest - Email HTML Template Builder"""
from collections import defaultdict

TAG_COLORS = {
    "AI/ML": ("EEF2FF","4338CA"), "Infrastructure": ("ECFDF5","065F46"),
    "Security": ("FFF1F2","9F1239"), "Research": ("FDF4FF","7E22CE"),
    "Engineering": ("FFF7ED","9A3412"), "DevOps": ("FFF7ED","9A3412"),
    "Business": ("F0F9FF","075985"), "Community": ("FFF8F0","9A3412"),
    "Tech": ("F8F8F8","444444"), "Web Dev": ("F0FDF4","166534"),
}

CSS = """* {margin:0;padding:0;box-sizing:border-box;}
body {background:#F0F0F0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:24px 16px;}
.wrap {max-width:640px;margin:0 auto;}
.header {background:#111;border-radius:16px 16px 0 0;padding:28px 32px;}
.badge {display:inline-block;background:#1c1c2e;color:#818CF8;font-size:10px;letter-spacing:.12em;padding:4px 12px;border-radius:20px;margin-bottom:14px;border:1px solid #3730A3;}
.h-title {font-size:26px;font-weight:700;color:#fff;line-height:1.2;}
.h-sub {font-size:12px;color:#666;margin-top:8px;}
.statsbar {background:#161616;display:flex;}
.stat {flex:1;padding:16px 8px;text-align:center;border-right:1px solid #222;}
.stat:last-child {border-right:none;}
.sn {font-size:22px;font-weight:700;color:#fff;}
.sl {font-size:10px;color:#555;margin-top:3px;text-transform:uppercase;}
.body {background:#fff;padding:28px 32px;}
.tip-box {background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:14px 18px;margin-bottom:22px;}
.tip-label {font-size:10px;font-weight:700;color:#16A34A;letter-spacing:.1em;margin-bottom:6px;}
.tip-text {font-size:12px;color:#374151;line-height:1.7;}
.src-box {background:#F8F8FF;border:1px solid #E0E0FF;border-radius:10px;padding:14px 18px;margin-bottom:24px;}
.src-box-label {font-size:10px;font-weight:700;color:#6366F1;letter-spacing:.1em;margin-bottom:8px;}
.src-links {font-size:12px;color:#555;line-height:2;}
.src-links a {color:#6366F1;text-decoration:none;}
.section {margin-bottom:28px;}
.src-row {display:flex;align-items:center;gap:8px;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #F5F5F5;}
.src-dot {width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.src-name {font-size:11px;font-weight:700;letter-spacing:.1em;}
.src-count {font-size:11px;color:#bbb;margin-left:auto;}
.card {border:1px solid #F0F0F0;border-radius:10px;padding:16px;margin-bottom:10px;}
.ctop {display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:10px;}
.ctitle {font-size:14px;font-weight:600;color:#111;line-height:1.45;}
.tag {font-size:10px;padding:3px 10px;border-radius:20px;white-space:nowrap;flex-shrink:0;font-weight:600;}
.cbody {font-size:13px;color:#555;line-height:1.8;}
.vocab-box {background:#FFFBEB;border-left:3px solid #F59E0B;padding:10px 14px;margin-top:12px;border-radius:0 8px 8px 0;}
.vocab-label {font-size:10px;font-weight:700;color:#D97706;letter-spacing:.08em;margin-bottom:5px;}
.vocab-text {font-size:12px;color:#555;line-height:1.8;}
.cfoot {font-size:11px;color:#bbb;margin-top:12px;}
.cfoot a {color:#6366F1;text-decoration:none;font-weight:500;}
.divider {height:1px;background:#F5F5F5;margin:24px 0;}
.trends {background:#FAFAFA;border-radius:10px;padding:18px 22px;}
.trends-label {font-size:10px;font-weight:700;color:#999;letter-spacing:.1em;margin-bottom:14px;}
.trend-item {display:flex;gap:10px;margin-bottom:10px;}
.trend-item:last-child {margin-bottom:0;}
.trend-arrow {color:#6366F1;font-size:14px;flex-shrink:0;margin-top:1px;font-weight:700;}
.trend-text {font-size:13px;color:#333;line-height:1.65;}
.footer {background:#111;border-radius:0 0 16px 16px;padding:16px 32px;display:flex;justify-content:space-between;align-items:center;}
.ft {font-size:11px;color:#444;}"""


def tag_badge(tag):
    bg, fg = TAG_COLORS.get(tag, ("F5F5F5","444444"))
    return f'<span class="tag" style="background:#{bg};color:#{fg};">{tag}</span>'


def build_email_html(lang, date_str, articles, trends, learning_tip):
    is_ko = lang == "ko"
    by_source = defaultdict(list)
    source_meta = {}
    for a in articles:
        by_source[a["source"]].append(a)
        source_meta[a["source"]] = {"color": a["source_color"]}

    badge = "DAILY TECH DIGEST · 한국어 버전" if is_ko else "DAILY TECH DIGEST · ENGLISH EDITION"
    title = "빅테크 & 개발자 뉴스 요약" if is_ko else "Big Tech & Dev News Digest"
    sub = f"{date_str} · Claude AI 자동 요약" if is_ko else f"{date_str} · Curated by Claude AI"
    al = "새 글" if is_ko else "Articles"
    sl = "출처" if is_ko else "Sources"
    rl = "읽기 시간" if is_ko else "Read time"
    tl = "핵심 트렌드" if is_ko else "Key Trends"
    orig = "원문 읽기 →" if is_ko else "Read full article →"
    th = "🔍 오늘의 핵심 트렌드" if is_ko else "🔍 KEY TRENDS TODAY"
    fl = f"Claude AI 자동 요약 · hanakimhereiam@gmail.com" if is_ko else "Curated by Claude AI · hanakimhereiam@gmail.com"
    rt = f"~{max(5,len(articles))}분" if is_ko else f"~{max(5,len(articles))}min"

    sections = ""
    for sname, arts in by_source.items():
        color = source_meta[sname]["color"]
        cnt = f"{len(arts)}개" if is_ko else f"{len(arts)} article{'s' if len(arts)>1 else ''}"
        cards = ""
        for a in arts:
            t = a["title_ko"] if is_ko else a["title_en"]
            s = a["summary_ko"] if is_ko else a["summary_en"]
            vh = ""
            if not is_ko and a.get("vocab"):
                vi = "".join(f"<br><strong>{v.split(':')[0]}</strong>:{':'.join(v.split(':')[1:])}" for v in a["vocab"])
                vh = f'<div class="vocab-box"><div class="vocab-label">KEY VOCAB</div><div class="vocab-text">{vi}</div></div>'
            cards += f'<div class="card"><div class="ctop"><div class="ctitle">{t}</div>{tag_badge(a.get("tag","Tech"))}</div><div class="cbody">{s}</div>{vh}<div class="cfoot"><a href="{a["url"]}">{orig}</a></div></div>'
        sections += f'<div class="section"><div class="src-row"><div class="src-dot" style="background:{color}"></div><span class="src-name" style="color:{color}">{sname.upper()}</span><span class="src-count">{cnt}</span></div>{cards}</div>'

    trends_html = "".join(f'<div class="trend-item"><span class="trend-arrow">→</span><span class="trend-text">{t}</span></div>' for t in trends)
    tip = f'<div class="tip-box"><div class="tip-label">ENGLISH TIP OF THE DAY</div><div class="tip-text">{learning_tip}</div></div>' if not is_ko and learning_tip else ""
    src_links = " · ".join(f'<a href="#">{s}</a>' for s in by_source.keys())

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style></head><body><div class="wrap">
<div class="header"><div class="badge">{badge}</div><div class="h-title">{title}</div><div class="h-sub">{sub}</div></div>
<div class="statsbar"><div class="stat"><div class="sn">{len(articles)}</div><div class="sl">{al}</div></div><div class="stat"><div class="sn">{len(by_source)}</div><div class="sl">{sl}</div></div><div class="stat"><div class="sn">{rt}</div><div class="sl">{rl}</div></div><div class="stat"><div class="sn">3</div><div class="sl">{tl}</div></div></div>
<div class="body">{tip}<div class="src-box"><div class="src-box-label">📚 SOURCES</div><div class="src-links">{src_links}</div></div>{sections}<div class="divider"></div><div class="trends"><div class="trends-label">{th}</div>{trends_html}</div></div>
<div class="footer"><span class="ft">{fl}</span><span class="ft">{date_str}</span></div></div></body></html>"""
