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
    with open(index_path, "r", encoding="utf-8") as fp:
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
    "cartridge",
}

# {
#   "id": 97,
#   "diameter": 0.308,
#   "weight": 168,
#   "caliber": ".308 Winchester",
#   "path": "gallery/308W/308W_BLACK_HILLS_168GR_A_MAX_G7.a7p",
#   "profileName": "308W BLACK HILLS A-MAX 168GR",
#   "name": ".308 Winchester BH A-MAX 168GR BH A-MAX 168GR",
#   "cartridge": "BH A-MAX 168GR",
#   "bullet": "BH A-MAX 168GR",
#   "cartridgeVendor": null,
#   "bulletVendor": null,
#   "dragModelType": "G7",
#   "meta": {
#     "productName": "308 Win 168 gr A‑MAX® Hornady BLACK®",
#     "vendor": "Black Hills",
#     "bulletVendor": "",
#     "caliber": "308 Winchester / 7.62×51mm NATO",
#     "muzzle_velocity": null,
#     "bc": 0.475,
#     "g7": null,
#     "bulletType": "A‑MAX®",
#     "weight": 168,
#     "country": "",
#     "url": "https://www.hornady.com/ammunition/rifle/308-win-168-gr-a-max-black#!/",
#     "_fields": {
#       "productLine": "Hornady BLACK"
#     }
#   }
# },




for meta in profiles_meta:
    path = Path(meta.get("path", ""))
    if path in filtered_files:
        files_match += 1
        meta_path = path.with_suffix(".meta.json")
        _meta = meta.get("meta", {})

        new_meta = {
            "name": meta.get("name"),
            "productName": _meta.get("productName"),
            "caliber": _meta.get("caliber"),
            "bulletType": _meta.get("bulletType"),
            "bulletVendor": _meta.get("bulletVendor"),
            "cartridge": meta.get("cartridge"),
            "cartridgeVendor": _meta.get("vendor"),
            "url": _meta.get("url"),
            "country": _meta.get("country"), 
            "bc": _meta.get("bc"),
            "g7": _meta.get("g7"),
            "weight": _meta.get("weight"),
            "muzzleVelocity": _meta.get("muzzle_velocity"),
            "author": None,
            "note": None,
            "extra": _meta.get("_fields")
        }

        new_meta_json = new_meta

        with open(meta_path, "w", encoding="utf-8") as fp:
            json.dump(new_meta_json, fp)

    else:
        print("NOT FOUND: ", path)

print(files_match)