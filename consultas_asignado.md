# Proyecto asignado: tres consultas del warehouse de agua (CDMX)

Base: PostgreSQL 16 en Docker (`data_warehouse_cdmx`, puerto 5433, base `data_warehouse`).
Esquema en estrella: hechos `fact_consumo_agua` (70,886 filas) y `fact_clima`;
dimensiones `dim_tiempo` (181 días de 2019, enero a junio), `dim_ubicacion`, `dim_indice_des`
y `dim_ubicacion_adyacencia`.

Notación: σ selección, π proyección, ⨝ reunión, γ agrupación.
Los árboles se leen de abajo hacia arriba: las tablas son las hojas y la expresión termina en la raíz.

---

## Q1. Selección y proyección

**Pregunta:** ¿qué días hubo una temperatura máxima de 28 °C o más, y de cuánto fue?

**Álgebra relacional**

```
π id_tiempo, temp_maxima ( σ temp_maxima >= 28 ( fact_clima ) )
```

**Árbol de operadores**

```
π id_tiempo, temp_maxima        <- raíz
        |
σ temp_maxima >= 28             <- operador principal
        |
   fact_clima                   <- hoja
```

**Operador principal:** la selección (σ), que descarta las filas que no cumplen el umbral.

**SQL equivalente**

```sql
SELECT id_tiempo, temp_maxima
FROM fact_clima
WHERE temp_maxima >= 28;
```

**Resultado:** 47 filas. Las 8 más altas:

| id_tiempo | temp_maxima |
|---|---|
| 156 | 31.7 |
| 79 | 31.6 |
| 102 | 30.8 |
| 145 | 30.5 |
| 137 | 30.4 |
| 52 | 30.4 |
| 159 | 30.0 |
| 136 | 29.9 |

**Verificación:** `SELECT COUNT(*) FROM fact_clima WHERE temp_maxima >= 28;` devuelve 47,
igual a los días de calor por bimestre de Q3 (3 + 25 + 19).

---

## Q2. Reunión de tres tablas

**Pregunta:** ¿cuánta agua se facturó por alcaldía en el bimestre 2?

**Álgebra relacional**

```
γ alcaldia; SUM(consumo_total) → total_agua (
  π alcaldia, consumo_total (
    σ bimestre = 2 (
      ( fact_consumo_agua ⨝ dim_ubicacion ) ⨝ dim_tiempo ) ) )
```

Las reuniones son naturales por `id_ubicacion` e `id_tiempo`.

**Árbol de operadores**

```
γ alcaldia; SUM(consumo_total)
        |
π alcaldia, consumo_total
        |
σ bimestre = 2
        |
⨝ (id_tiempo)                    <- operador principal
   /            \
⨝ (id_ubicacion)  dim_tiempo
   /        \
fact_consumo_agua  dim_ubicacion
```

**Operador principal:** la reunión (⨝) de las tres tablas. La agrupación solo resume al final.

**SQL equivalente**

```sql
SELECT u.alcaldia, SUM(f.consumo_total) AS total_agua
FROM fact_consumo_agua f
JOIN dim_ubicacion u ON f.id_ubicacion = u.id_ubicacion
JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
WHERE t.bimestre = 2
GROUP BY u.alcaldia
ORDER BY total_agua DESC;
```

**Resultado:** 16 filas, una por alcaldía.

| alcaldia | total_agua |
|---|---|
| CUAUHTEMOC | 6,339,135.50 |
| MIGUEL HIDALGO | 5,008,196.54 |
| GUSTAVO A. MADERO | 4,682,351.10 |
| BENITO JUAREZ | 4,645,272.84 |
| ALVARO OBREGON | 3,382,510.95 |
| AZCAPOTZALCO | 3,145,963.98 |
| IZTAPALAPA | 2,839,631.76 |
| COYOACAN | 2,679,713.92 |
| VENUSTIANO CARRANZA | 2,434,000.08 |
| IZTACALCO | 2,126,746.66 |
| TLALPAN | 1,719,464.92 |
| CUAJIMALPA DE MORELOS | 1,040,060.00 |
| XOCHIMILCO | 706,822.13 |
| LA MAGDALENA CONTRERAS | 437,824.13 |
| TLAHUAC | 282,601.84 |
| MILPA ALTA | 49,284.61 |

**Verificación:** la suma de las 16 alcaldías es 41,519,580.96, igual al `total_agua`
del bimestre 2 en Q3.

---

## Q3. Consulta del proyecto: consumo de agua frente a clima por bimestre

Archivo original: `warehouse/scripts/consulta.sql`.

**Pregunta:** ¿cómo se comparan el consumo de agua y la temperatura en cada bimestre?

**Álgebra relacional** (modela el núcleo: `total_agua` y `temp_promedio`)

```
A = γ anio, bimestre; SUM(consumo_total) → total_agua ( fact_consumo_agua ⨝ dim_tiempo )
C = γ anio, bimestre; AVG(temp_promedio) → temp_promedio ( fact_clima ⨝ dim_tiempo )

π anio, bimestre, total_agua, temp_promedio ( A ⨝ C )
```

**Árbol de operadores**

```
π anio, bimestre, total_agua, temp_promedio
                 |
     ⨝ (anio, bimestre)                    <- operador principal
        /                  \
γ anio,bimestre; SUM     γ anio,bimestre; AVG
        |                          |
   ⨝ (id_tiempo)             ⨝ (id_tiempo)
    /        \                /        \
fact_consumo_agua dim_tiempo  fact_clima dim_tiempo
```

**Operador principal:** la reunión (⨝) de las dos agrupaciones por año y bimestre.

**SQL equivalente:** el del archivo `consulta.sql`, que además calcula
`dias_ola_calor` (máxima ≥ 28), `dias_frio` (mínima ≤ 10) y `total_lluvia`.

```sql
WITH ClimaBimestral AS (
    SELECT t.anio, t.bimestre,
        ROUND(AVG(fc.temp_promedio), 2) AS temp_promedio,
        COUNT(CASE WHEN fc.temp_maxima >= 28 THEN 1 END) AS dias_ola_calor,
        COUNT(CASE WHEN fc.temp_minima <= 10 THEN 1 END) AS dias_frio,
        SUM(fc.lluvia_total) AS total_lluvia
    FROM fact_clima fc
    JOIN dim_tiempo t ON fc.id_tiempo = t.id_tiempo
    GROUP BY t.anio, t.bimestre
),
AguaBimestral AS (
    SELECT t.anio, t.bimestre, SUM(fca.consumo_total) AS total_agua
    FROM fact_consumo_agua fca
    JOIN dim_tiempo t ON fca.id_tiempo = t.id_tiempo
    GROUP BY t.anio, t.bimestre
)
SELECT a.anio, a.bimestre, a.total_agua,
       c.temp_promedio, c.dias_ola_calor, c.dias_frio, c.total_lluvia
FROM AguaBimestral a
JOIN ClimaBimestral c ON a.anio = c.anio AND a.bimestre = c.bimestre
ORDER BY a.anio, a.bimestre;
```

**Resultado**

| anio | bimestre | total_agua | temp_promedio | dias_ola_calor | dias_frio | total_lluvia |
|---|---|---|---|---|---|---|
| 2019 | 1 | 37,663,466.692 | 15.50 | 3 | 45 | 13.50 |
| 2019 | 2 | 41,519,580.96 | 18.88 | 25 | 16 | 45.00 |
| 2019 | 3 | 41,174,097.68 | 19.46 | 19 | 2 | 186.60 |

---

## Cobertura pedida

- Selección: Q1 (σ).
- Proyección: Q1 y Q2 (π).
- Reunión: Q2 y Q3 (⨝).
- Agrupación: Q2 y Q3 (γ).
