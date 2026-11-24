"""같은 브랜드에서 썸네일이 같은 인스타그램/DA 쌍을 찾는다(삭제하지 않음).
사용: python tools/dedupe_scan.py"""
import sitelib as L

items = [d for _, _, d in L.blocks(L.read(L.SITE))]
pairs = L.same_image_pairs(items)
for ig, da in pairs:
    print("남김(IG):", ig["date"], ig["url"], "|", ig["title"][:30])
    print("삭제(DA):", da["date"], da["url"], "|", da["title"][:30], "\n")
print("쌍", len(pairs))
