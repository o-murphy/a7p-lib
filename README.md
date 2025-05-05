# Public library of .a7p profiles and json API

## Endpoints:

### Use it as CDN:
https://o-murphy.github.io/a7p-lib

#### Index of all profiles and unique keys:

Request:
```
GET https://o-murphy.github.io/a7p-lib/public/profiles.json
```

Response
```
{
  "profiles": [
    {
      "id": 8,
      "diameter": 0.172,
      "weight": 25,
      "caliber": ".17REM",
      "path": "gallery/17REM/17REM_HORNADY_25GR_HP_G1.a7p",
      "profileName": ".17REM HORNADY 25GR HP",
      "name": ".17REM HORNADY 25GR HP REM 25GR HOR HP",
      "cartridge": "HORNADY 25GR HP",
      "bullet": "REM 25GR HOR HP",
      "cartridgeVendor": null,
      "bulletVendor": null,
      "dragModelType": "G1",
      "meta": {
        "productName": "17 Cal .172 25 gr V‑MAX®",
        "vendor": "Hornady",
        "bulletVendor": "",
        "caliber": "17HMR / 17 Remington / Hornady Magnum Rifle",
        "muzzle_velocity": null,
        "bc": null,
        "g7": null,
        "bulletType": "V‑MAX®",
        "weight": 25,
        "country": "USA",
        "url": "https://www.hornady.com/bullets/rifle/17-cal-172-25-gr-v-max#!/"
      }
    },
    ...
  ],
  "uniqueKeys": {
    "calibers": [
        "300 AAC Blackout / Whisper",
        "300 Norma Magnum",
        "300 Remington Ultra Magnum",
        "308 Winchester / 7.62×51mm NATO",
        "338 Lapua Magnum",
        ...
    ],
    "diameters": [
        0.511,
        0.586,
        0.172,
        ...
    ],
    "bulletVendors": [
        "Remington",
        "Norma",
        "RWS",
        "Sierra",
        ...
    ],
    "cartridgeVendors": [
        "",
        "Hornady",
        "Remington",
        "Winchester",
        "Norma",
        "RWS",
        ...
    ]
}
```


Download `.a7p` file

Request
```
GET https://o-murphy.github.io/a7p-lib/gallery/<caliber>/<filename>.a7p
```

Get profile metadata

Request
```
GET https://o-murphy.github.io/a7p-lib/gallery/<caliber>/<filename>.meta.json
```