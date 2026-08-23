### Restaurant Analytics — Semana 2

Laboratorio aplicado de la asignatura Data Analytics (Código: 43390860), enfocado en el perfil del analista, el modelo relacional y el trabajo reproducible.

## Objetivo 

- Actuar como Business Data Analyst de una cadena de restaurantes que guarda su información en cuatro archivos independientes (productos, clientes y ventas de dos semanas). El objetivo es consolidar esas fuentes, validar las uniones entre tablas y construir indicadores que apoyen decisiones sobre el menú y la fidelización de clientes, dejando el proceso documentado y reproducible.


## Alcance: 
- los datos incluyen precios de venta pero no costos, cantidades ni descuentos. Por eso el análisis cubre ingresos, frecuencia de compra y recurrencia, no rentabilidad, utilidad ni margen.

- `data/`: archivos CSV del laboratorio (no se incluye el archivo de clientes ni nombres en repositorios públicos, por privacidad).
- `lab_Sem2_DA.ipynb`: notebook con el análisis completo, ejecutado de principio a fin.
- `README.md`: este archivo.

## Datos utilizados


Archivo
Contenido
Filas
`Restaurant-Foods.csv`
Catálogo de productos y precios
10
`Restaurant-Customers.csv`
Información de clientes (ID, nombre, género, empresa, ocupación)
1000
`Restaurant-Week1-Sales.csv`
Registros de venta — semana 1
250
`Restaurant-Week2-Sales.csv`
Registros de venta — semana 2
250

## Principales hallazgos

Ingresos totales: $3,886.56, repartidos en $1,962.68 (semana 1) y $1,923.88 (semana 2), con 250 registros de venta en cada semana.
Desempeño del menú: el Burrito es el producto con mayor frecuencia de compra (57 registros), mientras que el Steak genera los mayores ingresos ($1,249.50). Ambos indicadores no coinciden en el mismo producto, lo que sugiere que un precio promedio más alto compensa una menor frecuencia de compra.
Recurrencia de clientes: de los 221 clientes únicos de la semana 1, 46 volvieron a comprar en la semana 2 (tasa de recurrencia del 20.8%).
Perfil agregado: las ocupaciones con mayores ingresos acumulados incluyen Compensation Analyst, Sales Representative y Marketing Manager.
Los resultados obtenidos con Pandas y con SQL son consistentes entre sí.
