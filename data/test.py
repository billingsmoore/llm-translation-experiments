import re
from pathlib import Path

from antx import transfer

data_path = Path(__file__).parent / "chonjuk"
root_stanzas_fn = data_path / "chonjuk_root_stanzas.txt"
chonjuk_bo_fn = data_path / "chonjuk-bo.txt"

assert root_stanzas_fn.is_file()
assert chonjuk_bo_fn.is_file()

root_stanzas = root_stanzas_fn.read_text().replace("\ufeff", "").strip()
chonjuk_bo = chonjuk_bo_fn.read_text().strip().replace("\n", " ").replace("།", "")
print(chonjuk_bo)

annotations = [("newlines", r"(\n)"), ("shed", r"(།)")]
result = transfer(root_stanzas, annotations, chonjuk_bo)

new_chonjuk_bo_fn = data_path / "chonjuk-bo-new.txt"
new_chonjuk_bo_fn.write_text(result)
