import requests
import pandas as pd

# 2020 Decennial Census - P.L. 94-171 Redistricting Data
# P1_001N = Total Population
API_URL = "https://api.census.gov/data/2020/dec/pl"

STATE = "22"  # Louisiana

# VTDs grouped by county
COUNTIES = {
    "047": [  # Iberville Parish
        {"GEOID20": "22047000001", "VTDST20": "000001"},
        {"GEOID20": "22047000010", "VTDST20": "000010"},
        {"GEOID20": "22047000011", "VTDST20": "000011"},
        {"GEOID20": "22047000012", "VTDST20": "000012"},
        {"GEOID20": "2204700013C", "VTDST20": "00013C"},
        {"GEOID20": "2204700014A", "VTDST20": "00014A"},
        {"GEOID20": "22047000015", "VTDST20": "000015"},
        {"GEOID20": "22047000016", "VTDST20": "000016"},
        {"GEOID20": "22047000019", "VTDST20": "000019"},
        {"GEOID20": "22047000020", "VTDST20": "000020"},
        {"GEOID20": "22047000021", "VTDST20": "000021"},
        {"GEOID20": "22047000022", "VTDST20": "000022"},
        {"GEOID20": "22047000023", "VTDST20": "000023"},
        {"GEOID20": "22047000003", "VTDST20": "000003"},
        {"GEOID20": "22047000006", "VTDST20": "000006"},
        {"GEOID20": "22047000007", "VTDST20": "000007"},
        {"GEOID20": "22047000009", "VTDST20": "000009"},
    ],
    "121": [  # West Baton Rouge Parish
        {"GEOID20": "2212100001C", "VTDST20": "00001C"},
    ],
}

COUNTY_NAMES = {
    "047": "Iberville Parish",
    "121": "West Baton Rouge Parish",
}

def fetch_vtd_population(county):
    params = {
        "get": "NAME,P1_001N",
        "for": "voting district:*",
        "in": f"state:{STATE} county:{county}",
        # "key": "YOUR_API_KEY_HERE"  # Optional
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

def main():
    all_records = []

    for county, vtds in COUNTIES.items():
        county_name = COUNTY_NAMES.get(county, f"County {county}")
        print(f"Fetching VTD population for {county_name} (County {county})...")

        vtd_lookup  = {v["VTDST20"]: v["GEOID20"] for v in vtds}
        target_vtds = set(vtd_lookup.keys())

        data    = fetch_vtd_population(county)
        headers = data[0]
        rows    = data[1:]

        found = []
        for row in rows:
            record   = dict(zip(headers, row))
            vtd_code = record["voting district"]
            if vtd_code in target_vtds:
                all_records.append({
                    "COUNTY":     county_name,
                    "GEOID20":    vtd_lookup[vtd_code],
                    "VTDST20":    vtd_code,
                    "NAME":       record["NAME"],
                    "POPULATION": int(record["P1_001N"]),
                })
                found.append(vtd_code)

        missing = target_vtds - set(found)
        if missing:
            print(f"  WARNING: VTDs not matched: {sorted(missing)}")
        else:
            print(f"  Matched all {len(vtds)} VTDs")

    df = pd.DataFrame(all_records).reset_index(drop=True)

    total_vtds = sum(len(v) for v in COUNTIES.values())
    print(f"\nMatched {len(df)} of {total_vtds} total VTDs\n")
    print("=== Precinct Population (2020 Decennial Census) ===")
    print(df[["COUNTY", "GEOID20", "VTDST20", "NAME", "POPULATION"]].to_string(index=False))

    df.to_csv("precinct_population.csv", index=False)
    print("\nSaved to precinct_population.csv")

if __name__ == "__main__":
    main()