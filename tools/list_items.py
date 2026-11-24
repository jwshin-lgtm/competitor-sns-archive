"""기존 항목 요약(중복 방지용).
사용: python tools/list_items.py [--urls]
전체 건수와 브랜드별 최근 항목을 보여주고, --urls를 주면 모든 URL을 한 줄씩 출력한다."""
import sys
import collections
import sitelib as L

s = L.read(L.SITE)
items = [d for _, _, d in L.blocks(s)]
print("총", len(items), "건")
by = collections.defaultdict(list)
for d in items:
    by[d["brand"]].append(d)
for b, ds in by.items():
    print("\n##", b, len(ds), "건")
    for d in ds[-8:]:
        print(" ", d["date"], d["channel"], d["url"], "|", d["title"][:40])
if "--urls" in sys.argv:
    print("\n".join(d["url"] for d in items))
