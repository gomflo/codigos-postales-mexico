#!/usr/bin/env bash
# Prepara carpetas listas para subir a Kaggle y Hugging Face en dist/.
# No sube nada: sólo copia. Correr después de scripts/actualizar.py.
#
#   dist/kaggle/  dataset-metadata.json + los tres CSV con nombre plano
#   dist/hf/      README.md (tarjeta HF) + DATA_LICENSE.md + data/
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf dist
mkdir -p dist/kaggle dist/hf

cp kaggle/dataset-metadata.json dist/kaggle/
for pais in mx co es; do
  cp "data/$pais/codigos-postales.csv" "dist/kaggle/$pais-codigos-postales.csv"
done

cp hf/README.md dist/hf/README.md
cp DATA_LICENSE.md dist/hf/
cp -R data dist/hf/data

du -sh dist/kaggle dist/hf
