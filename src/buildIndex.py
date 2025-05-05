from pathlib import Path
import json
import a7p
from pprint import pprint

dir = "gallery"
exclude_dirs = {".unvalidated"}
files = Path("gallery").rglob("*.a7p")


filtered_files = tuple(
    f for f in files if not any(exclude_dir in f.parts for exclude_dir in exclude_dirs)
)

bc_type = {
    0: "G1",
    1: "G7",
    2: "CUSTOM",
}


def new_index(p):
    with open(p, "rb") as fp:
        pay = a7p.load(fp)
        return {
            "diameter": pay.profile.b_diameter / 1000,
            "weight": pay.profile.b_weight / 10,
            "length": pay.profile.b_length / 1000,
            "muzzleVelocity": pay.profile.c_muzzle_velocity / 10,
            "dragModelType": bc_type.get(pay.profile.bc_type),
        }


id_ = 0
profs = []
vendors = []
for p in filtered_files:
    meta = p.with_suffix(".meta.json")
    if meta.exists():
        with open(meta, "r", encoding="utf-8") as fp:
            metadata = json.load(fp)

        new_prof = {
            "id": id_,
            "path": p.as_posix(),
            **new_index(p),
            "meta": {"path": meta.as_posix(), **metadata},
        }
        # pprint(new_prof)
        profs.append(new_prof)
        vendors.append(metadata.get("bulletVendor"))
        vendors.append(metadata.get("cartridgeVendor"))
        

with open("public/profiles_index.json", "w", encoding="utf-8") as fp:
    json.dump(profs, fp)
