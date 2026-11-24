"""site.html ITEMS 배열을 다루는 공용 함수. 모든 수집/정리 스크립트가 이 모듈을 쓴다."""
import re
import sys
import io
import os
import urllib.request
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SITE = "site.html"
INDEX = "index.html"
UA = {"User-Agent": "Mozilla/5.0"}


def read(p):
    return open(p, encoding="utf-8", newline="").read()


def write(p, s):
    open(p, "w", encoding="utf-8", newline="").write(s)


def nl_of(s):
    return "\r\n" if "\r\n" in s else "\n"


def _field(blk, key):
    m = re.search(r'\b%s:"((?:[^"\\]|\\.)*)"' % key, blk)
    return m.group(1) if m else ""


def blocks(s):
    """ITEMS 배열 안의 각 항목을 (start, end, dict)로 돌려준다. end는 닫는 중괄호 바로 뒤."""
    a = s.index("var ITEMS = [")
    b = s.index("\n  ];", a)
    out = []
    for m in re.finditer(r"(?m)^    \{\r?\n", s[a:b + 1]):
        st = a + m.start()
        en = s.index("\n    }", st) + len("\n    }")
        blk = s[st:en]
        d = {k: _field(blk, k) for k in ("brand", "channel", "url", "title", "thumb", "date", "topic", "status", "note")}
        out.append((st, en, d))
    return out


def thumb_path(t):
    t = t.replace("/_blob/", "images/")
    if t and not t.endswith(".jpg"):
        t += ".jpg"
    return t


def vec(path):
    im = Image.open(path).convert("L").resize((48, 48), Image.LANCZOS)
    return im.tobytes()


def mad(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def esc(v):
    return str(v).replace("\\", "\\\\").replace('"', '\\"')


def make_block(it, nl):
    lines = [
        "    {",
        '      brand:"%s", channel:"%s",' % (esc(it["brand"]), esc(it["channel"])),
        '      url:"%s",' % esc(it["url"]),
        '      title:"%s",' % esc(it["title"]),
        '      thumb:"images/%s",' % esc(it["image_name"]),
        '      date:"%s", topic:"%s", status:"실측",' % (esc(it["date"]), esc(it["topic"])),
        '      note:"%s"' % esc(it["note"]),
        "    }",
    ]
    return nl.join(lines)


def letterbox_save(raw, out_name):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = im.size
    s = 320 / max(w, h)
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    c = Image.new("RGB", (320, 320), (0, 0, 0))
    c.paste(im, ((320 - im.width) // 2, (320 - im.height) // 2))
    c.save(os.path.join("images", out_name), quality=90)


def download(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()


def regenerate_index():
    s = read(SITE)
    s = re.sub(r'/_blob/([a-f0-9]+)"', r'images/\1.jpg"', s)
    write(INDEX, s)


def is_ig(ch):
    return ch.startswith("인스타그램")


def is_da(ch):
    return ch == "DA"


def same_image_pairs(items):
    """같은 브랜드에서 썸네일이 같은 (인스타그램, DA) 쌍 목록."""
    V = []
    for d in items:
        p = thumb_path(d["thumb"])
        if not p:
            continue
        try:
            V.append((d, vec(p)))
        except Exception:
            pass
    pairs = []
    for i, (a, va) in enumerate(V):
        for b, vb in V[i + 1:]:
            if a["brand"] != b["brand"]:
                continue
            if (is_ig(a["channel"]) and is_da(b["channel"])) or (is_da(a["channel"]) and is_ig(b["channel"])):
                if mad(va, vb) < 1.5:
                    pairs.append((a, b) if is_ig(a["channel"]) else (b, a))
    return pairs
