# Códigos postales de México (y Colombia y España)

Catálogo completo de códigos postales de **México** (Sepomex), más **Colombia** y
**España** (GeoNames), en CSV limpio y listo para usar. Es un espejo de los
datos que publica [Postali](https://postali.app) y se actualiza solo cada semana.

- Un archivo por país, UTF-8, mismas columnas en los tres.
- CSV comprimido (`.csv.gz`) y JSON indexado por código postal.
- México también dividido por estado, para quien sólo necesita uno.
- Historial de cambios con altas y bajas en [CHANGELOG.md](CHANGELOG.md).

> **¿Necesitas consultar un CP puntual?** Usa la API gratuita
> **[https://postali.app/api](https://postali.app/api)**: no hace falta bajar
> nada. Por ejemplo: `curl https://postali.app/api/v1/mx/cp/06700`

## Fuente y cita

| País | Fuente original | Licencia / términos | Página en Postali |
|---|---|---|---|
| México | Catálogo Nacional de Códigos Postales, **Servicio Postal Mexicano (Correos de México, Sepomex)** | Términos de Sepomex: gratuito, **no se permite su comercialización** | [postali.app/mx](https://postali.app/mx) |
| Colombia | **GeoNames** (geonames.org) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — atribución obligatoria | [postali.app/co](https://postali.app/co) |
| España | **GeoNames** (geonames.org) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — atribución obligatoria | [postali.app/es](https://postali.app/es) |

Lee [DATA_LICENSE.md](DATA_LICENSE.md) antes de usar los datos en un producto.

**Cómo citar** (texto sugerido):

> Códigos postales de México: Catálogo Nacional de Códigos Postales, Servicio
> Postal Mexicano (Correos de México). Limpieza y publicación:
> Postali — https://postali.app

> Códigos postales de Colombia / España: GeoNames (https://www.geonames.org),
> CC BY 4.0. Limpieza y publicación: Postali — https://postali.app

En BibTeX:

```bibtex
@misc{postali_codigos_postales,
  author       = {{Postali}},
  title        = {Códigos postales de México, Colombia y España},
  howpublished = {\url{https://postali.app}},
  note         = {México: Servicio Postal Mexicano (Sepomex). Colombia y España: GeoNames, CC BY 4.0},
  year         = {2026}
}
```

## Archivos

```
data/
  resumen.json                     filas, CPs, sha256 y fecha de cada país
  mx/codigos-postales.csv          México completo
  mx/codigos-postales.csv.gz       el mismo CSV comprimido
  mx/codigos-postales.json         {"06700": [{...}, ...], ...}
  mx/por-estado/{estado}.csv       un CSV por estado (jalisco.csv, ciudad-de-mexico.csv…)
  co/…                             Colombia (mismos formatos, sin división)
  es/…                             España (mismos formatos, sin división)
```

Conteos actuales (se regeneran en cada actualización):

<!-- conteos:inicio -->
| País | Archivo | Filas | Códigos postales | Municipios | Última actualización |
|---|---|---:|---:|---:|---|
| México | `data/mx/codigos-postales.csv` | 159,326 | 31,874 | 2,478 | 2026-09-27 |
| Colombia | `data/co/codigos-postales.csv` | 3,681 | 3,681 | 1,122 | 2026-09-27 |
| España | `data/es/codigos-postales.csv` | 37,867 | 11,150 | 6,706 | 2026-09-27 |
<!-- conteos:fin -->

Hay más filas que códigos postales porque un mismo CP cubre varios
asentamientos (en México, una colonia por fila).

## Columnas

| # | México | Colombia | España | Contenido |
|---|---|---|---|---|
| 1 | `codigo_postal` | `codigo_postal` | `codigo_postal` | CP como texto, **con ceros a la izquierda** (`01000`, `050001`) |
| 2 | `asentamiento` | `centro_poblado` | `localidad` | Colonia, barrio, pueblo, localidad… |
| 3 | `tipo` | `tipo` | `tipo` | Colonia, Fraccionamiento, Ranchería… / Zona Postal, Centro Poblado / Localidad, Zona Postal |
| 4 | `municipio` | `municipio` | `municipio` | Municipio o alcaldía |
| 5 | `estado` | `departamento` | `provincia` | Primer nivel administrativo |
| 6 | `ciudad` | `ciudad` | `ciudad` | Ciudad (sólo México; vacía en CO y ES) |
| 7 | `zona` | `zona` | `zona` | Urbano, Rural o Semiurbano (sólo México) |
| 8 | `url` | `url` | `url` | Ficha del asentamiento en postali.app |

Formato: UTF-8 **con BOM** (Excel abre los acentos bien), separador coma,
comillas sólo cuando hacen falta, saltos de línea `\n`.

**Importante:** lee siempre `codigo_postal` como texto. Si lo conviertes a
número pierdes el cero inicial y `01000` se vuelve `1000`.

## Frecuencia de actualización

Un workflow de GitHub Actions ([actualizar.yml](.github/workflows/actualizar.yml))
corre **cada lunes** y también se puede lanzar a mano. Descarga los CSV de
Postali, valida encabezado, columnas, formato de CP y que el número de filas no
caiga más de un 10 %, regenera los derivados y hace commit **sólo si algo
cambió**. Postali, a su vez, sincroniza con Sepomex a diario.

Para correrlo en local (sólo Python 3.9+, sin dependencias):

```bash
python3 scripts/actualizar.py
```

## Ejemplos

### pandas

```python
import pandas as pd

url = "https://raw.githubusercontent.com/gomflo/codigos-postales-mexico/main/data/mx/codigos-postales.csv"
cp = pd.read_csv(url, dtype=str, keep_default_na=False)

cp[cp.codigo_postal == "06700"][["asentamiento", "municipio", "estado"]]
cp.groupby("estado").codigo_postal.nunique().sort_values(ascending=False)

# Sólo Jalisco
jal = pd.read_csv("data/mx/por-estado/jalisco.csv", dtype=str, keep_default_na=False)
```

### csvkit

```bash
csvgrep -c codigo_postal -m 06700 data/mx/codigos-postales.csv | csvlook
csvgrep -c estado -m "Yucatán" data/mx/codigos-postales.csv | csvcut -c codigo_postal,asentamiento,municipio
csvstat -c estado --freq data/mx/codigos-postales.csv
```

### SQLite

```bash
sqlite3 codigos.db <<'SQL'
CREATE TABLE cp_mx (
  codigo_postal TEXT, asentamiento TEXT, tipo TEXT, municipio TEXT,
  estado TEXT, ciudad TEXT, zona TEXT, url TEXT
);
.import --csv --skip 1 data/mx/codigos-postales.csv cp_mx
CREATE INDEX cp_mx_cp ON cp_mx(codigo_postal);
SELECT asentamiento, municipio FROM cp_mx WHERE codigo_postal = '06700';
SQL
```

### PostgreSQL

```sql
CREATE TABLE cp_mx (
  codigo_postal text NOT NULL,
  asentamiento  text NOT NULL,
  tipo          text,
  municipio     text NOT NULL,
  estado        text NOT NULL,
  ciudad        text,
  zona          text,
  url           text
);
\copy cp_mx FROM 'data/mx/codigos-postales.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
CREATE INDEX ON cp_mx (codigo_postal);
```

### JSON por código postal

```python
import json
with open("data/mx/codigos-postales.json", encoding="utf-8") as f:
    por_cp = json.load(f)
por_cp["06700"]   # lista de asentamientos con ese CP
```

## Licencias

- **Scripts y documentación** de este repositorio: [MIT](LICENSE).
- **Datos** (`data/`): los términos de cada fuente, detallados en
  [DATA_LICENSE.md](DATA_LICENSE.md). La licencia MIT **no** se aplica a los datos.

---

## English

Postal code catalogs for **Mexico** (source: Servicio Postal Mexicano /
Sepomex), **Colombia** and **Spain** (source: GeoNames, CC BY 4.0), mirrored
from [Postali](https://postali.app) and refreshed weekly by GitHub Actions.
Files: `data/{mx,co,es}/codigos-postales.csv` (UTF-8 with BOM), a `.csv.gz`
copy, a JSON keyed by postal code and, for Mexico, one CSV per state in
`data/mx/por-estado/`. Always read `codigo_postal` as a string to keep leading
zeros.

For single lookups use the free API at [https://postali.app/api](https://postali.app/api).

Licensing: scripts are MIT. Mexican data is subject to Sepomex's terms (free of
charge, commercialization not permitted); Colombian and Spanish data are
GeoNames, CC BY 4.0, attribution required. See [DATA_LICENSE.md](DATA_LICENSE.md).
Please cite as “Postali — https://postali.app”, plus the original source.
