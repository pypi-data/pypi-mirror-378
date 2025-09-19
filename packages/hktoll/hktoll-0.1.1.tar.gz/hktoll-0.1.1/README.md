# hktoll — Python Hong Kong (HKeToll) tolls

**hktoll** is a **Python** library & CLI to compute **Hong Kong (HKeToll) tolls** from official Transport Department datasets.
Give it a route (lon/lat pairs or GeoJSON) and a timestamp; get back ordered toll events and totals (HKD).

> 適用於香港（HKeToll）收費計算的 Python 程式庫。

- **Input**: route polyline `[(lon, lat), ...]` or GeoJSON `LineString` / `FeatureCollection`
- **Output**: ordered toll events *(facility, time band, amount)* + totals (HKD)
- **Interfaces**: Python API, CLI, and a tiny REST server

---

## Install

```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install -U pip
pip install hktoll
````

> Requires Python 3.9+.

---

## Quick start

### CLI

```bash
# Route via coordinates (lon,lat;lon,lat;...)
hktoll route \
  --coords "114.1582,22.2799;114.1640,22.2801;114.1721,22.2975" \
  --vehicle private_car \
  --when "2025-09-17T08:30:00+08:00" \
  -o out.json

# Annotate a GeoJSON FeatureCollection of LineStrings in-place
hktoll annotate-geojson examples/sample_route.geojson -o annotated.geojson
```

> Tip: run `hktoll --help` for all commands and options.

### Python API

```python
from datetime import datetime
from hktoll import compute_tolls, annotate_geojson_with_tolls, TollEvent

route = [(114.1582, 22.2799), (114.1640, 22.2801), (114.1721, 22.2975)]
events, total = compute_tolls(route, vehicle="private_car", when=datetime.now())
print(total, [e.dict() for e in events])  # total in HKD
```

### REST API (language‑agnostic)

```bash
# Start the server
hktoll serve --host 0.0.0.0 --port 8000

# Call it
curl -X POST http://localhost:8000/v1/tolls/route \
  -H "content-type: application/json" \
  -d '{
        "coords": [[114.1582,22.2799],[114.1640,22.2801],[114.1721,22.2975]],
        "vehicle": "private_car",
        "when": "2025-09-17T08:30:00+08:00"
      }'
```

---

## What it does

* Computes toll **events and totals** for Hong Kong tunnels/bridges, including **time‑varying** toll bands at harbour crossings.
* Accepts routes as lon/lat pairs or GeoJSON; returns structured `TollEvent` objects.
* Ships a CLI and a tiny HTTP server for language‑agnostic use.
* Uses an **adapter** layout so other regions can be added later (e.g., ERP, AutoPASS, Salik).

---

## Data sources (official)

hktoll consumes Transport Department resources from the **Road Network (2nd Generation)** dataset and related materials:

* **Toll rates of tunnel and bridge (flat)** — `TUN_BRIDGE_TOLL.csv`
  [https://data.gov.hk/en-data/dataset/hk-td-tis\_15-road-network-v2/resource/3673f74a-ab49-4f5c-9df2-2b79569d5500](https://data.gov.hk/en-data/dataset/hk-td-tis_15-road-network-v2/resource/3673f74a-ab49-4f5c-9df2-2b79569d5500)

* **Toll rates of tunnel and bridge (time‑varying)** — `TUN_BRIDGE_TV_TOLL.csv`
  [https://data.gov.hk/en-data/dataset/hk-td-tis\_15-road-network-v2/resource/9d127737-e1e4-4081-8b58-f749bb0fe3b7](https://data.gov.hk/en-data/dataset/hk-td-tis_15-road-network-v2/resource/9d127737-e1e4-4081-8b58-f749bb0fe3b7)

* **Zebra crossing, yellow box, toll plaza and cul‑de‑sac** — `TRAFFIC_FEATURES.kmz`
  [https://data.gov.hk/en-data/dataset/hk-td-tis\_15-road-network-v2/resource/57c24df1-722d-47d7-a458-553548938f41](https://data.gov.hk/en-data/dataset/hk-td-tis_15-road-network-v2/resource/57c24df1-722d-47d7-a458-553548938f41)

> The library downloads and caches these files automatically. See `src/hktoll/resources/urls.json` for exact endpoints and `docs/GETTING_STARTED.md` for details.

For background on **HKeToll** (the free‑flow tolling system):
[https://www.hketoll.gov.hk/](https://www.hketoll.gov.hk/)

---

## Inputs & outputs

* **Route**: list of `(lon, lat)` pairs *or* GeoJSON `LineString` / `FeatureCollection`.
* **Vehicle**: string identifier (e.g., `private_car`). Run `hktoll route --help` to see the available values.
* **When**: timestamp (ISO 8601, timezone aware) used to apply correct time‑varying toll band.

**Returns:**

* **TollEvents**: list of `TollEvent`
* **Total**: Decimal value of total tolls

Each `TollEvent` includes at minimum: `facility`, `time_band` (if applicable), `amount_hkd`, and `timestamp`.

---

## Examples

See the [examples/](examples/) folder for ready‑to‑run samples.

---

## Contributing

PRs and issues welcome! Please read the [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
If you use hktoll in a paper or product, consider citing it via [CITATION.cff](CITATION.cff).

---

## Attribution & terms

* Data © Transport Department, HKSAR Government; sourced via DATA.GOV.HK.
* Reuse of data is subject to DATA.GOV.HK Terms and Conditions.
* hktoll is an independent open‑source project and is **not affiliated** with the Government.

---

## License

[MIT](LICENSE)

---

### Keywords

`python hong kong tolls`, `hong-kong`, `HKeToll`, `tolls`, `routing`, `gis`, `transport`

```

