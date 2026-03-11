import pandas as pd
import geopandas as gpd
from shapely.validation import make_valid
import json
from datetime import datetime
from pathlib import Path

Path("data/validation_reports").mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("RUNNING DATA VALIDATION PIPELINE")
print("=" * 60)

# Load from CSV (clean column names, no merge artifacts)
df = pd.read_csv("data/processed/all_regions_metrics.csv")
boundaries = gpd.read_file("data/raw/boundaries/pilot_regions.geojson")

print(f"Total records to validate: {len(df)}")
print(f"CSV Columns: {list(df.columns)}")
print(f"Boundary rows: {len(boundaries)}")
print()

results = {}
all_failed = set()

def run_rule(name, failed_indices, errors):
    passed = len(df) - len(failed_indices)
    rate   = passed / len(df) * 100
    status = "PASS" if len(failed_indices) == 0 else "FAIL"
    print(f"  [{status}] {name}: {rate:.1f}% ({len(failed_indices)} failures)")
    for e in errors[:2]:
        print(f"           --> {e}")
    results[name] = {"passed": passed, "failed": len(failed_indices),
                     "pass_rate": round(rate, 2), "errors": errors[:5]}
    all_failed.update(failed_indices)

# Rule 1: Valid lat/lon coordinates from CSV columns
failed, errors = [], []
for idx, row in df.iterrows():
    lat = row.get("lat")
    lon = row.get("lon")
    if pd.isna(lat) or pd.isna(lon):
        failed.append(idx); errors.append(f"Row {idx}: null lat/lon")
    elif not (-90 <= float(lat) <= 90):
        failed.append(idx); errors.append(f"Row {idx}: lat={lat} out of range")
    elif not (-180 <= float(lon) <= 180):
        failed.append(idx); errors.append(f"Row {idx}: lon={lon} out of range")
run_rule("valid_coordinates", failed, errors)

# Rule 2: Valid geometry in boundary file
failed, errors = [], []
for idx, row in boundaries.iterrows():
    if row.geometry is None or not row.geometry.is_valid:
        repaired = make_valid(row.geometry) if row.geometry else None
        failed.append(idx)
        errors.append(f"Row {idx}: invalid geometry")
run_rule("valid_geometry", failed, errors)

# Rule 3: No missing values in required columns
required = ["region_name", "year", "tree_cover_pct", "tree_cover_ha", "total_area_ha"]
failed, errors = [], []
for idx, row in df.iterrows():
    missing = [c for c in required if c not in df.columns or pd.isna(row.get(c))]
    if missing:
        failed.append(idx); errors.append(f"Row {idx}: missing {missing}")
run_rule("no_missing_values", failed, errors)

# Rule 4: No duplicate region + year combinations
dupes = df.duplicated(subset=["region_name", "year"], keep="first")
failed = list(df[dupes].index)
run_rule("no_duplicates", failed, [f"Duplicate at idx {i}" for i in failed])

# Rule 5: Year in valid range
failed, errors = [], []
for idx, row in df.iterrows():
    yr = row.get("year")
    if pd.isna(yr) or not (2010 <= int(yr) <= 2030):
        failed.append(idx); errors.append(f"Row {idx}: year={yr}")
run_rule("valid_year_range", failed, errors)

# Rule 6: Tree cover percentage 0-100
failed, errors = [], []
for idx, row in df.iterrows():
    pct = row.get("tree_cover_pct")
    if pd.isna(pct) or not (0 <= float(pct) <= 100):
        failed.append(idx); errors.append(f"Row {idx}: pct={pct}")
run_rule("valid_pct_range", failed, errors)

# Rule 7: Tree cover ha must not exceed total area ha (5% tolerance)
failed, errors = [], []
for idx, row in df.iterrows():
    trees = float(row.get("tree_cover_ha") or 0)
    total = float(row.get("total_area_ha") or 0)
    if total <= 0:
        failed.append(idx); errors.append(f"Row {idx}: total_area_ha={total}")
    elif trees > total * 1.05:
        failed.append(idx); errors.append(f"Row {idx}: tree={trees:.0f} > total={total:.0f}")
run_rule("area_consistency", failed, errors)

# Final score
clean         = len(df) - len(all_failed)
quality_score = clean / len(df) * 100

print()
print("=" * 60)
print(f"  OVERALL DATA QUALITY SCORE: {quality_score:.1f}%")
print(f"  Clean records:   {clean} / {len(df)}")
print(f"  Flagged records: {len(all_failed)}")
print("=" * 60)

report = {
    "dataset": "all_regions_metrics",
    "timestamp": datetime.now().isoformat(),
    "total_records": len(df),
    "clean_records": clean,
    "quality_score": round(quality_score, 2),
    "rules": results
}
ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
path = f"data/validation_reports/validation_{ts}.json"
with open(path, "w") as f:
    json.dump(report, f, indent=2)
print(f"  Report saved: {path}")

