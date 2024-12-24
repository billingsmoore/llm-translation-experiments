from pathlib import Path

data_path = Path(__file__).parent / "chonjuk"
commentary_fn = data_path / "chonjuk_commentary.csv"
root_en = data_path / "new_chonjuk-en-root.txt"

segment_pairs = commentary_fn.read_text().strip().split("\n")[1:]
verses_en = [verse for verse in root_en.read_text().strip().split("\n\n")]

print(len(segment_pairs), len(verses_en))

# bo_en = list(zip(segment_pairs, verses_en))

# i = len(bo_en) - 1
# print("translation")
# print(bo_en[i][0].split(",")[0])
# print(bo_en[i][1])
# print("-" * 100)

for i, verse in enumerate(verses_en):
    parts = verse.splitlines()
    if len(parts) < 4:
        print(i + 1)
        print(len(parts), verse)
        print("-" * 100)

alignmments = []
for i, segment_pair in enumerate(segment_pairs):
    root, cmt = segment_pair.split(",")
    parts = root.replace("།", "").strip().split()
    if len(parts) > 4:
        print(i + 1, len(parts), root)
