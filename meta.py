import json
from pathlib import Path
from pprint import pprint


index_path = "public/profiles.json"

exclude_dirs = {".unvalidated"}

files = Path("gallery").rglob("*.a7p")

filtered_files = tuple(
    f for f in files if not any(exclude_dir in f.parts for exclude_dir in exclude_dirs)
)


try:
    with open(index_path, 'r', encoding="utf-8") as fp:
        index = json.load(fp)
except OSError as err:
    raise Exception("Error on reading ")


profiles_meta = index.get("profiles", {})

print(len(filtered_files), len(profiles_meta))

files_match = 0

pop_keys = {
    "id",
    "diameter",
    "weight",
    "caliber",
    "path",
    "profileName",
    "cartridge",
    "bullet",
    "dragModelType",
}

for meta in profiles_meta:
    path = Path(meta.get("path", ""))
    if path in filtered_files:
        files_match += 1
        for k in pop_keys:
            meta.pop(k)
            meta_path = path.with_suffix('.meta.json')
            print(meta)
            with open(meta_path, 'w', encoding='utf-8') as fp:
                json.dump(meta, fp, indent=2)

