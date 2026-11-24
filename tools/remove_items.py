"""항목 삭제 후 index.html 재생성.
사용:
  python tools/remove_items.py <url> [<url> ...]   지정한 URL의 항목만 삭제
  python tools/remove_items.py --dedupe             같은 이미지의 인스타그램/DA 쌍에서 DA를 삭제(인스타그램만 남김)
이미지 파일은 지우지 않는다(되돌리기 위해)."""
import sys
import sitelib as L

args = sys.argv[1:]
s = L.read(L.SITE)
nl = L.nl_of(s)
if "--dedupe" in args:
    items = [d for _, _, d in L.blocks(s)]
    targets = [da["url"] for ig, da in L.same_image_pairs(items)]
else:
    targets = [a for a in args if a.startswith("http")]
targets = list(dict.fromkeys(targets))
removed = 0
for u in targets:
    found = [x for x in L.blocks(s) if x[2]["url"] == u]
    if len(found) != 1:
        print("건너뜀(없거나 여러 건):", u)
        continue
    st, en, d = found[0]
    if s[en] == ",":
        end = en + 1
        if s[end:end + len(nl)] == nl:
            end += len(nl)
        s = s[:st] + s[end:]
    else:
        # 마지막 항목: 앞 항목의 뒤 쉼표를 지운다
        prev_comma = s.rfind(",", 0, st)
        s = s[:prev_comma] + s[prev_comma + 1:st].rstrip() + s[en:]
    print("삭제:", d["brand"], d["channel"], d["date"], d["title"][:30], u)
    removed += 1
L.write(L.SITE, s)
L.regenerate_index()
print("삭제 건수", removed, "/ 남은 건수", len(L.blocks(L.read(L.SITE))))
