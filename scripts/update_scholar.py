"""Fetch Google Scholar stats and redraw the citation chart block in index.html.

Leaves the page untouched if Scholar blocks the request or the page layout changes.
"""
import pathlib, re, sys, urllib.request, html, datetime

USER = "oxMDd5sAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en"
PROFILE = f"https://scholar.google.ca/citations?user={USER}&hl=en"
INDEX = pathlib.Path(__file__).resolve().parent.parent / "index.html"
START, END = "<!-- scholar:start -->", "<!-- scholar:end -->"


def fetch():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def parse(page):
    stats = [int(x) for x in re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', page)]
    years = [int(x) for x in re.findall(r'<span class="gsc_g_t"[^>]*>(\d+)</span>', page)]
    counts = [int(x) for x in re.findall(r'<span class="gsc_g_al">(\d+)</span>', page)]
    if len(stats) != 6 or not years or len(years) != len(counts):
        raise ValueError("unexpected Scholar page layout")
    return stats, list(zip(years, counts))


def render(stats, series):
    w, h, gap, top, base = 230, 88, 8, 14, 17
    n = len(series)
    bw = (w - gap * (n - 1)) / n
    peak = max(c for _, c in series) or 1
    axis = h - base
    bars = [f'<line x1="0" y1="{axis}" x2="{w}" y2="{axis}" class="axis"/>']
    for i, (y, c) in enumerate(series):
        x = i * (bw + gap)
        bh = max((axis - top) * c / peak, 1)
        yy = axis - bh
        cx = x + bw / 2
        bars.append(
            f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="2" class="bar"><title>{y}: {c} citations</title></rect>'
            f'<text x="{cx:.1f}" y="{yy - 4:.1f}" class="val">{c}</text>'
            f'<text x="{cx:.1f}" y="{h - 3}" class="yr">\'{str(y)[2:]}</text>')
    tiles = "".join(f'<div><span class="num">{v}</span><span class="lbl">{k}</span></div>'
                    for k, v in [("Citations", stats[0]), ("h-index", stats[2]), ("i10-index", stats[4])])
    today = datetime.date.today().strftime("%b %Y")
    return f'''{START}
    <div class="scholar">
      <div class="tiles">{tiles}</div>
      <svg viewBox="0 0 {w} {h}" role="img" aria-label="Citations per year">{"".join(bars)}</svg>
      <p class="scholar-note"><a href="{html.escape(PROFILE)}" target="_blank" rel="noopener">Google Scholar</a> · {today}</p>
    </div>
    {END}'''


def main():
    page = fetch()
    stats, series = parse(page)
    s = INDEX.read_text()
    a, b = s.index(START), s.index(END) + len(END)
    new = s[:a] + render(stats, series) + s[b:]
    if new != s:
        INDEX.write_text(new)
    print("citations", stats[0], "h", stats[2], "years", series)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # keep last good numbers on any failure
        print("Scholar update skipped:", e)
        sys.exit(0)
