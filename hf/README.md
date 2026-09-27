---
language:
  - es
license: other
license_name: sepomex-terminos-y-cc-by-4.0
license_link: DATA_LICENSE.md
pretty_name: Códigos postales de México, Colombia y España
size_categories:
  - 100K<n<1M
tags:
  - postal-codes
  - geography
  - mexico
  - colombia
  - spain
  - sepomex
  - geonames
configs:
  - config_name: mx
    default: true
    data_files:
      - split: train
        path: data/mx/codigos-postales.csv
  - config_name: co
    data_files:
      - split: train
        path: data/co/codigos-postales.csv
  - config_name: es
    data_files:
      - split: train
        path: data/es/codigos-postales.csv
dataset_info:
  - config_name: mx
    features:
    - name: codigo_postal
      dtype: string
    - name: asentamiento
      dtype: string
    - name: tipo
      dtype: string
    - name: municipio
      dtype: string
    - name: estado
      dtype: string
    - name: ciudad
      dtype: string
    - name: zona
      dtype: string
    - name: url
      dtype: string
  - config_name: co
    features:
    - name: codigo_postal
      dtype: string
    - name: centro_poblado
      dtype: string
    - name: tipo
      dtype: string
    - name: municipio
      dtype: string
    - name: departamento
      dtype: string
    - name: ciudad
      dtype: string
    - name: zona
      dtype: string
    - name: url
      dtype: string
  - config_name: es
    features:
    - name: codigo_postal
      dtype: string
    - name: localidad
      dtype: string
    - name: tipo
      dtype: string
    - name: municipio
      dtype: string
    - name: provincia
      dtype: string
    - name: ciudad
      dtype: string
    - name: zona
      dtype: string
    - name: url
      dtype: string
---

# Códigos postales de México, Colombia y España

Catálogo completo de códigos postales de **México** (Sepomex) y de **Colombia**
y **España** (GeoNames), con el mismo esquema de 8 columnas. Espejo de los datos
de [Postali](https://postali.app), actualizado cada semana desde
[github.com/gomflo/codigos-postales-mexico](https://github.com/gomflo/codigos-postales-mexico).

> ¿Necesitas consultar un CP puntual? Usa la API gratuita
> [https://postali.app/api](https://postali.app/api).

## Uso

```python
from datasets import load_dataset

mx = load_dataset("gomflo/codigos-postales-mexico", "mx", split="train")
co = load_dataset("gomflo/codigos-postales-mexico", "co", split="train")
es = load_dataset("gomflo/codigos-postales-mexico", "es", split="train")

mx.filter(lambda r: r["codigo_postal"] == "06700")
```

Todas las columnas se declaran como `string`, así `codigo_postal` conserva los
ceros a la izquierda (`01000`).

## Configuraciones y conteos

<!-- conteos:inicio -->
| País | Archivo | Filas | Códigos postales | Municipios | Última actualización |
|---|---|---:|---:|---:|---|
| México | `data/mx/codigos-postales.csv` | 159,326 | 31,874 | 2,478 | 2026-09-27 |
| Colombia | `data/co/codigos-postales.csv` | 3,681 | 3,681 | 1,122 | 2026-09-27 |
| España | `data/es/codigos-postales.csv` | 37,867 | 11,150 | 6,706 | 2026-09-27 |
<!-- conteos:fin -->

| Config | Columnas |
|---|---|
| `mx` | codigo_postal, asentamiento, tipo, municipio, estado, ciudad, zona, url |
| `co` | codigo_postal, centro_poblado, tipo, municipio, departamento, ciudad, zona, url |
| `es` | codigo_postal, localidad, tipo, municipio, provincia, ciudad, zona, url |

`ciudad` y `zona` sólo tienen valor en México. `url` enlaza la ficha del
asentamiento en postali.app.

## Fuente, licencia y cita

- **México:** Catálogo Nacional de Códigos Postales del Servicio Postal
  Mexicano (Correos de México). Rigen los términos de Sepomex: se proporciona
  en forma gratuita y **no está permitida su comercialización**, total o
  parcial. No tiene licencia abierta estándar. Vía [postali.app/mx](https://postali.app/mx).
- **Colombia y España:** [GeoNames](https://www.geonames.org),
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); la atribución es
  obligatoria. Vía [postali.app/co](https://postali.app/co) y
  [postali.app/es](https://postali.app/es).

Detalle en [DATA_LICENSE.md](DATA_LICENSE.md).

Cita sugerida:

> Códigos postales: Servicio Postal Mexicano (México) y GeoNames, CC BY 4.0
> (Colombia, España). Limpieza y publicación: Postali — https://postali.app

## English

Postal code catalogs for Mexico (Sepomex), Colombia and Spain (GeoNames,
CC BY 4.0), cleaned by [Postali](https://postali.app) and refreshed weekly.
Mexican data follows Sepomex terms (free of charge, commercialization not
permitted); Colombian and Spanish data require GeoNames attribution.
