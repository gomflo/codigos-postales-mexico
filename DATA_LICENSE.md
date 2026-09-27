# Licencia y términos de los datos

La licencia MIT de [LICENSE](LICENSE) cubre **sólo** los scripts y la
documentación de este repositorio. Los datos de `data/` conservan los términos
de su fuente original, que son distintos por país. Este repositorio no concede
ningún derecho adicional sobre ellos.

## México — `data/mx/`

**Fuente:** Catálogo Nacional de Códigos Postales, elaborado por el Servicio
Postal Mexicano (Correos de México, antes Sepomex), descargado de
<https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx>
y limpiado por [Postali](https://postali.app/mx).

**Términos:** son los que fija el Servicio Postal Mexicano. Su página de
descarga indica textualmente (consultado el 26 de septiembre de 2026):

> «El Catálogo Nacional de Códigos Postales, es elaborado por el Servicio
> Postal Mexicano y se proporciona en forma gratuita, no estando permitida su
> comercialización, total o parcial.»

Sepomex no publica el catálogo bajo una licencia abierta estándar (CC, ODbL,
etc.) y este repositorio no le asigna una. En la práctica:

- Puedes descargarlo, consultarlo y usarlo sin costo.
- **No** está permitido vender el catálogo, total o parcialmente.
- Si tu uso es comercial o dudas si lo es, revisa los términos vigentes en el
  sitio de Correos de México o consúltalo con ellos.
- Cita al Servicio Postal Mexicano como fuente.

## Colombia — `data/co/` y España — `data/es/`

**Fuente:** [GeoNames](https://www.geonames.org) (volcados de códigos postales
`CO.zip` y `ES.zip` de <https://download.geonames.org/export/zip/>), limpiados
por [Postali](https://postali.app).

**Licencia:** [Creative Commons Attribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.es).
Puedes copiar, redistribuir, transformar y usar los datos, también con fines
comerciales, **siempre que des atribución**: menciona a GeoNames, enlaza la
licencia e indica si hiciste cambios. Por ejemplo:

> Datos de códigos postales: GeoNames (https://www.geonames.org), CC BY 4.0.
> Normalizados por Postali (https://postali.app).

Cambios que hizo Postali sobre el volcado de GeoNames: adaptación al esquema
común de columnas (sin coordenadas), normalización de los nombres de
departamento/provincia (tildes, mayúsculas), clasificación de la columna
`tipo` y asignación de URLs. GeoNames
ofrece los datos «tal cual», sin garantía; su cobertura en Colombia es parcial
(ver <https://postali.app/co/datos>).

## Columna `url` y cita de Postali

La columna `url` y la limpieza de los datos son trabajo de
[Postali](https://postali.app). Si te resultan útiles, agradecemos que cites o
enlaces <https://postali.app> junto a la fuente original.

## Sin garantía

Los datos se ofrecen «tal cual». Los códigos postales cambian; para un uso
crítico, verifica contra la fuente oficial.
