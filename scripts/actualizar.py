#!/usr/bin/env python3
"""Descarga los catálogos de códigos postales de Postali, los valida y
regenera los archivos derivados de data/.

Sólo usa la biblioteca estándar (Python 3.9+), así corre igual en local que en
GitHub Actions sin instalar nada.

Flujo:
  1. Descarga los tres CSV (mx, co, es) a memoria.
  2. Valida TODO antes de escribir nada: encabezado exacto, 8 columnas por
     fila, formato del CP, URL de Postali y que el número de filas no caiga más
     de --max-caida respecto a la versión anterior. Si un país falla, el
     script sale con código 1 sin tocar el disco.
  3. Escribe el CSV tal cual se sirvió y regenera los derivados
     (.csv.gz, .json por CP y, para México, un CSV por estado). Todos los
     derivados son deterministas: si el CSV no cambió, git no ve cambios.
  4. Si algún CSV cambió, añade una entrada a CHANGELOG.md con los deltas y
     actualiza los conteos de README.md y hf/README.md.

Uso:
  python3 scripts/actualizar.py            # actualización normal
  python3 scripts/actualizar.py --forzar   # ignora el límite de caída de filas
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
RESUMEN = DATOS / "resumen.json"
CHANGELOG = RAIZ / "CHANGELOG.md"
DOCS_CON_CONTEOS = [RAIZ / "README.md", RAIZ / "hf" / "README.md"]

BOM = b"\xef\xbb\xbf"
USER_AGENT = "codigos-postales-mexico/1.0 (+https://github.com/gomflo/codigos-postales-mexico)"

PAISES = {
    "mx": {
        "nombre": "México",
        "url": "https://postali.app/mx/datos/codigos-postales.csv",
        "encabezado": ["codigo_postal", "asentamiento", "tipo", "municipio",
                       "estado", "ciudad", "zona", "url"],
        "cp": re.compile(r"^\d{5}$"),
        "minimo": 100_000,
        "dividir_por": "estado",
    },
    "co": {
        "nombre": "Colombia",
        "url": "https://postali.app/co/datos/codigos-postales.csv",
        "encabezado": ["codigo_postal", "centro_poblado", "tipo", "municipio",
                       "departamento", "ciudad", "zona", "url"],
        "cp": re.compile(r"^\d{6}$"),
        "minimo": 2_000,
        "dividir_por": None,
    },
    "es": {
        "nombre": "España",
        "url": "https://postali.app/es/datos/codigos-postales.csv",
        "encabezado": ["codigo_postal", "localidad", "tipo", "municipio",
                       "provincia", "ciudad", "zona", "url"],
        "cp": re.compile(r"^\d{5}$"),
        "minimo": 20_000,
        "dividir_por": None,
    },
}


class ErrorValidacion(Exception):
    pass


# ── Descarga ────────────────────────────────────────────────────────────────

def descargar(url: str, intentos: int = 3) -> bytes:
    ultimo: Exception | None = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as r:
                if r.status != 200:
                    raise ErrorValidacion(f"HTTP {r.status}")
                return r.read()
        except (urllib.error.URLError, TimeoutError, ErrorValidacion) as e:
            ultimo = e
            if i + 1 < intentos:
                time.sleep(5 * (i + 1))
    raise ErrorValidacion(f"no se pudo descargar {url}: {ultimo}")


# ── Lectura y validación ───────────────────────────────────────────────────

def leer_filas(crudo: bytes) -> tuple[list[str], list[list[str]]]:
    texto = crudo.decode("utf-8-sig")  # strict: falla si no es UTF-8 válido
    lector = csv.reader(io.StringIO(texto, newline=""))
    encabezado = next(lector, [])
    return encabezado, list(lector)


def validar(codigo: str, cfg: dict, crudo: bytes, filas_previas: int | None,
            max_caida: float) -> tuple[list[str], list[list[str]]]:
    if not crudo.startswith(BOM):
        raise ErrorValidacion("el archivo no empieza con BOM UTF-8 (¿página de error?)")
    encabezado, filas = leer_filas(crudo)
    if encabezado != cfg["encabezado"]:
        raise ErrorValidacion(f"encabezado inesperado: {encabezado}")
    prefijo_url = f"https://postali.app/{codigo}/"
    for n, fila in enumerate(filas, start=2):
        if len(fila) != len(encabezado):
            raise ErrorValidacion(f"línea {n}: {len(fila)} columnas en vez de {len(encabezado)}")
        if not cfg["cp"].match(fila[0]):
            raise ErrorValidacion(f"línea {n}: CP inválido {fila[0]!r}")
        if not fila[1] or not fila[3] or not fila[4]:
            raise ErrorValidacion(f"línea {n}: faltan nombre, municipio o nivel 1")
        if not fila[7].startswith(prefijo_url):
            raise ErrorValidacion(f"línea {n}: URL inesperada {fila[7]!r}")
    if len(filas) < cfg["minimo"]:
        raise ErrorValidacion(f"sólo {len(filas)} filas (mínimo {cfg['minimo']})")
    if filas_previas and len(filas) < filas_previas * (1 - max_caida):
        raise ErrorValidacion(
            f"las filas caen de {filas_previas} a {len(filas)} "
            f"(más de {max_caida:.0%}); usa --forzar si es legítimo")
    return encabezado, filas


# ── Escritura de derivados ─────────────────────────────────────────────────

def escribir_si_cambia(ruta: Path, contenido: bytes) -> None:
    if ruta.exists() and ruta.read_bytes() == contenido:
        return
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_bytes(contenido)
    tmp.replace(ruta)


def a_csv(encabezado: list[str], filas: list[list[str]]) -> bytes:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(encabezado)
    w.writerows(filas)
    return BOM + buf.getvalue().encode("utf-8")


def a_gzip(crudo: bytes) -> bytes:
    # mtime=0 y sin nombre de archivo: misma entrada → mismos bytes.
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0, compresslevel=9) as gz:
        gz.write(crudo)
    return buf.getvalue()


def a_json_por_cp(encabezado: list[str], filas: list[list[str]]) -> bytes:
    """{"01000": [{asentamiento, tipo, ...}, ...], ...} — una línea por CP."""
    campos = encabezado[1:]
    por_cp: dict[str, list[dict]] = collections.defaultdict(list)
    for fila in filas:
        por_cp[fila[0]].append(dict(zip(campos, fila[1:])))
    lineas = [
        json.dumps(cp, ensure_ascii=False) + ":" +
        json.dumps(regs, ensure_ascii=False, separators=(",", ":"))
        for cp, regs in sorted(por_cp.items())
    ]
    return ("{\n" + ",\n".join(lineas) + "\n}\n").encode("utf-8")


def dividir(codigo: str, encabezado: list[str], filas: list[list[str]], columna: str) -> dict[str, bytes]:
    """Un CSV por entidad; el nombre del archivo es el slug que usa Postali en la URL."""
    idx = encabezado.index(columna)
    grupos: dict[str, list[list[str]]] = collections.defaultdict(list)
    slug_de: dict[str, str] = {}
    for fila in filas:
        slug = fila[7].split("/")[4]  # https://postali.app/mx/{slug}/...
        previo = slug_de.setdefault(fila[idx], slug)
        if previo != slug:
            raise ErrorValidacion(f"{codigo}: {fila[idx]!r} tiene dos slugs ({previo}, {slug})")
        grupos[slug].append(fila)
    return {slug: a_csv(encabezado, g) for slug, g in grupos.items()}


# ── Resumen, CHANGELOG y conteos en la documentación ───────────────────────

def estadisticas(filas: list[list[str]]) -> dict:
    return {
        "filas": len(filas),
        "codigos_postales": len({f[0] for f in filas}),
        "municipios": len({(f[4], f[3]) for f in filas}),
        "nivel1": len({f[4] for f in filas}),
    }


def miles(n: int) -> str:
    return f"{n:,}"


def delta(n: int) -> str:
    return f"+{n:,}" if n > 0 else (f"{n:,}" if n < 0 else "0")


def entrada_changelog(fecha: str, cambios: list[dict]) -> str:
    lineas = [f"## {fecha}", "",
              "| País | Filas | Δ filas | CPs | Δ CPs | Altas | Bajas |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for c in cambios:
        if c["previo"] is None:
            lineas.append(f"| {c['nombre']} | {miles(c['nuevo']['filas'])} | carga inicial | "
                          f"{miles(c['nuevo']['codigos_postales'])} | — | — | — |")
        else:
            lineas.append(
                f"| {c['nombre']} | {miles(c['nuevo']['filas'])} | "
                f"{delta(c['nuevo']['filas'] - c['previo']['filas'])} | "
                f"{miles(c['nuevo']['codigos_postales'])} | "
                f"{delta(c['nuevo']['codigos_postales'] - c['previo']['codigos_postales'])} | "
                f"{miles(c['altas'])} | {miles(c['bajas'])} |")
    lineas += ["", "Altas y bajas cuentan filas completas añadidas o retiradas "
               "(una fila editada cuenta como una baja y una alta).", "", ""]
    return "\n".join(lineas)


def anotar_changelog(entrada: str) -> None:
    cabecera = ("# Cambios en los datos\n\n"
                "Entradas generadas automáticamente por `scripts/actualizar.py` "
                "cuando alguno de los catálogos cambia.\n\n")
    previo = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else cabecera
    if not previo.startswith(cabecera):
        previo = cabecera + previo
    CHANGELOG.write_text(cabecera + entrada + previo[len(cabecera):], encoding="utf-8")


def tabla_conteos(resumen: dict) -> str:
    lineas = ["| País | Archivo | Filas | Códigos postales | Municipios | Última actualización |",
              "|---|---|---:|---:|---:|---|"]
    for codigo, cfg in PAISES.items():
        r = resumen["paises"][codigo]
        lineas.append(f"| {cfg['nombre']} | `data/{codigo}/codigos-postales.csv` | "
                      f"{miles(r['filas'])} | {miles(r['codigos_postales'])} | "
                      f"{miles(r['municipios'])} | {r['actualizado']} |")
    return "\n".join(lineas)


def actualizar_conteos_docs(resumen: dict) -> None:
    patron = re.compile(r"(<!-- conteos:inicio -->\n).*?(<!-- conteos:fin -->)", re.S)
    tabla = tabla_conteos(resumen)
    for ruta in DOCS_CON_CONTEOS:
        if not ruta.exists():
            continue
        texto = ruta.read_text(encoding="utf-8")
        nuevo = patron.sub(lambda m: m.group(1) + tabla + "\n" + m.group(2), texto)
        if nuevo != texto:
            ruta.write_text(nuevo, encoding="utf-8")


# ── Principal ───────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forzar", action="store_true", help="ignora el límite de caída de filas")
    ap.add_argument("--max-caida", type=float, default=0.10,
                    help="caída máxima de filas aceptada frente a la versión anterior (0.10 = 10%%)")
    args = ap.parse_args()
    max_caida = 1.0 if args.forzar else args.max_caida

    resumen_previo = json.loads(RESUMEN.read_text(encoding="utf-8")) if RESUMEN.exists() else {"paises": {}}
    hoy = dt.datetime.now(dt.timezone.utc).date().isoformat()

    # 1–2. Descargar y validar todo antes de escribir.
    lotes = {}
    for codigo, cfg in PAISES.items():
        previo = resumen_previo["paises"].get(codigo)
        try:
            crudo = descargar(cfg["url"])
            encabezado, filas = validar(codigo, cfg, crudo, previo and previo["filas"], max_caida)
        except (ErrorValidacion, UnicodeDecodeError, csv.Error) as e:
            print(f"✗ {codigo}: {e}", file=sys.stderr)
            return 1
        lotes[codigo] = (crudo, encabezado, filas)
        print(f"✓ {codigo}: {len(filas):,} filas, {len(crudo) / 1e6:.1f} MB")

    # 3. Escribir CSV + derivados.
    resumen = {"fuente": "https://postali.app", "paises": {}}
    cambios = []
    for codigo, (crudo, encabezado, filas) in lotes.items():
        cfg = PAISES[codigo]
        carpeta = DATOS / codigo
        ruta_csv = carpeta / "codigos-postales.csv"
        sha = hashlib.sha256(crudo).hexdigest()
        previo = resumen_previo["paises"].get(codigo)
        cambio = previo is None or previo.get("sha256") != sha or not ruta_csv.exists()

        if cambio and ruta_csv.exists() and previo is not None:
            _, filas_viejas = leer_filas(ruta_csv.read_bytes())
            a, b = collections.Counter(map(tuple, filas)), collections.Counter(map(tuple, filas_viejas))
            altas, bajas = sum((a - b).values()), sum((b - a).values())
        else:
            altas = bajas = 0

        escribir_si_cambia(ruta_csv, crudo)
        escribir_si_cambia(carpeta / "codigos-postales.csv.gz", a_gzip(crudo))
        escribir_si_cambia(carpeta / "codigos-postales.json", a_json_por_cp(encabezado, filas))

        if cfg["dividir_por"]:
            sub = carpeta / f"por-{cfg['dividir_por']}"
            partes = dividir(codigo, encabezado, filas, cfg["dividir_por"])
            for viejo in sub.glob("*.csv") if sub.exists() else []:
                if viejo.stem not in partes:
                    viejo.unlink()
            for slug, contenido in partes.items():
                escribir_si_cambia(sub / f"{slug}.csv", contenido)

        est = estadisticas(filas)
        resumen["paises"][codigo] = {
            **est,
            "sha256": sha,
            "bytes": len(crudo),
            "actualizado": hoy if cambio else previo["actualizado"],
            "origen": cfg["url"],
        }
        if cambio:
            cambios.append({"nombre": cfg["nombre"], "nuevo": est, "altas": altas, "bajas": bajas,
                            "previo": previo if previo and previo.get("sha256") else None})
            print(f"  ↻ {codigo} cambió")

    escribir_si_cambia(RESUMEN, (json.dumps(resumen, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    # 4. CHANGELOG y conteos, sólo si hubo cambios reales.
    if cambios:
        anotar_changelog(entrada_changelog(hoy, cambios))
    actualizar_conteos_docs(resumen)
    print("Sin cambios en los datos." if not cambios else f"{len(cambios)} catálogo(s) actualizados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
