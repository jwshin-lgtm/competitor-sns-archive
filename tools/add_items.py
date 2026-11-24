"""새 항목을 추가한다.
사용: python tools/add_items.py <items.json>
items.json = [{brand, channel, url, title, date, topic, note, image_url, image_name}, ...]
 - 이미 있는 URL은 건너뛴다.
 - 같은 브랜드에서 썸네일이 같은 인스타그램/DA 쌍이면 인스타그램만 남긴다
   (새 DA는 추가하지 않고, 새 인스타그램이 기존 DA와 같으면 그 DA를 삭제한다).
 - 이미지는 320x320 검은 배경 레터박스(잘림·왜곡 없음)로 images/<image_name>에 저장한다.
 - 끝에 index.html을 재생성하고 건수·썸네일 존재·URL 중복을 검증한다. git 커밋/푸시는 하지 않는다."""
import os
import sys
import json
import subprocess
import sitelib as L

new = json.load(open(sys.argv[1], encoding="utf-8"))
# 인스타그램을 먼저 처리해야 DA 중복 판정이 안정적이다
new.sort(key=lambda x: 0 if L.is_ig(x["channel"]) else 1)
s = L.read(L.SITE)
nl = L.nl_of(s)
existing = [d for _, _, d in L.blocks(s)]
urls = {d["url"] for d in existing}
added, skipped, removed_da = [], [], []
for it in new:
    if it["url"] in urls:
        skipped.append(("이미 있음", it["url"]))
        continue
    try:
        L.letterbox_save(L.download(it["image_url"]), it["image_name"])
    except Exception as e:
        skipped.append(("이미지 실패 %s" % e, it["url"]))
        continue
    nv = L.vec(os.path.join("images", it["image_name"]))
    skip_reason = None
    for d in existing:
        if d["brand"] != it["brand"] or d["url"] in removed_da:
            continue
        try:
            ev = L.vec(L.thumb_path(d["thumb"]))
        except Exception:
            continue
        if L.mad(nv, ev) < 1.5:
            if L.is_da(it["channel"]) and L.is_ig(d["channel"]):
                skip_reason = "DA 건너뜀(같은 이미지의 인스타그램이 있음: %s)" % d["url"]
                break
            if L.is_ig(it["channel"]) and L.is_da(d["channel"]):
                removed_da.append(d["url"])
    if skip_reason:
        os.remove(os.path.join("images", it["image_name"]))
        skipped.append((skip_reason, it["url"]))
        continue
    added.append(it)
    existing.append({"brand": it["brand"], "channel": it["channel"], "url": it["url"], "thumb": "images/" + it["image_name"]})
    urls.add(it["url"])
if added:
    marker = nl + "    }" + nl + "  ];"
    assert s.count(marker) == 1, "ITEMS 끝 위치를 찾지 못함"
    body = ("," + nl).join(L.make_block(it, nl) for it in added)
    s = s.replace(marker, nl + "    }," + nl + body + nl + "  ];")
    L.write(L.SITE, s)
if removed_da:
    subprocess.run([sys.executable, os.path.join("tools", "remove_items.py")] + removed_da, check=True)
L.regenerate_index()
final = [d for _, _, d in L.blocks(L.read(L.SITE))]
bad = [d["thumb"] for d in final if d["thumb"] and not os.path.exists(L.thumb_path(d["thumb"]))]
dups = len(final) - len({d["url"] for d in final})
print("추가 %d건 / 건너뜀 %d건 / 같은 이미지로 삭제한 DA %d건" % (len(added), len(skipped), len(removed_da)))
for a in added:
    print("  +", a["brand"], a["channel"], a["date"], a["title"][:36], a["image_name"])
for r, u in skipped:
    print("  -", r, u)
print("총 %d건 / 썸네일 누락 %d / URL 중복 %d" % (len(final), len(bad), dups))
