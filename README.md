Restaurant Analytics — Semana 2

Laboratorio aplicado de la asignatura Data Analytics (Código: 43390860), enfocado en el perfil del analista, el modelo relacional y el trabajo reproducible.

Objetivo

Actuar como Business Data Analyst de una cadena de restaurantes que guarda su información en cuatro archivos independientes (productos, clientes y ventas de dos semanas). El objetivo es consolidar esas fuentes, validar las uniones entre tablas y construir indicadores que apoyen decisiones sobre el menú y la fidelización de clientes, dejando el proceso documentado y reproducible.


Alcance: los datos incluyen precios de venta pero no costos, cantidades ni descuentos. Por eso el análisis cubre ingresos, frecuencia de compra y recurrencia, no rentabilidad, utilidad ni margen.


Estructura del repositorio

text
lab-restaurant/
│
├── data/
├── lab_Sem2_DA.ipynb
└── README.md


data/: archivos CSV del laboratorio (no se incluye el archivo de clientes ni nombres en repositorios públicos, por privacidad).
lab_Sem2_DA.ipynb: notebook con el análisis completo, ejecutado de principio a fin.
README.md: este archivo.

Datos utilizados


Archivo
Contenido
Filas
Restaurant-Foods.csv
Catálogo de productos y precios
10
Restaurant-Customers.csv
Información de clientes (ID, nombre, género, empresa, ocupación)
1000
Restaurant-Week1-Sales.csv
Registros de venta — semana 1
250
Restaurant-Week2-Sales.csv
Registros de venta — semana 2
250


Modelo relacional: cada registro de venta referencia un único Food ID (tabla foods) y un único Customer ID (tabla customers), en relación N:1. Un producto o un cliente pueden aparecer en varios registros de venta.

Cómo ejecutar el notebook

Clonar el repositorio y ubicar los cuatro CSV dentro de data/ (o cargarlos manualmente si se trabaja en Google Colab).
Abrir lab_Sem2_DA.ipynb y ejecutar las celdas en orden, de la primera a la última, sin modificaciones manuales adicionales.
Dependencias: pandas, matplotlib, sqlite3 (incluida en la librería estándar de Python).

bash
pip install pandas matplotlib


Proceso realizado

Carga y unificación: lectura de los cuatro CSV; se etiqueta cada venta con su semana (Semana = 1 o 2) y se concatenan en all_sales.
Validación de claves y referencias: se comprueba que Food ID en foods y ID en customers sean únicos, y que todas las ventas referencien productos y clientes existentes.
Consolidación (merge): unión de all_sales con foods y customers (validate='many_to_one') para construir full_report, verificando que el número de registros no cambie y que no queden datos esenciales vacíos.
Construcción de indicadores (KPIs):
Ingresos y registros de venta por semana.
Frecuencia de compra e ingresos totales por producto.
Tasa de recurrencia de clientes entre semana 1 y semana 2.
Ingresos agregados por ocupación del cliente.

Verificación cruzada con SQL: el mismo resumen semanal se replica con una consulta SQL sobre una base SQLite en memoria, para confirmar consistencia con los resultados de Pandas.
Visualizaciones:
Frecuencia de compra vs. ingresos por producto (gráfico de barras horizontales, lado a lado).
Comparación de ingresos entre semana 1 y semana 2 (gráfico de barras).
Una tercera visualización de elección libre, orientada a apoyar una recomendación del informe ejecutivo (recurrencia, ingresos por ocupación u otro indicador).


Principales hallazgos

Ingresos totales: $3,886.56, repartidos en $1,962.68 (semana 1) y $1,923.88 (semana 2), con 250 registros de venta en cada semana.
Desempeño del menú: el Burrito es el producto con mayor frecuencia de compra (57 registros), mientras que el Steak genera los mayores ingresos ($1,249.50). Ambos indicadores no coinciden en el mismo producto, lo que sugiere que un precio promedio más alto compensa una menor frecuencia de compra.
Recurrencia de clientes: de los 221 clientes únicos de la semana 1, 46 volvieron a comprar en la semana 2 (tasa de recurrencia del 20.8%).
Perfil agregado: las ocupaciones con mayores ingresos acumulados incluyen Compensation Analyst, Sales Representative y Marketing Manager.
Los resultados obtenidos con Pandas y con SQL son consistentes entre sí.

Limitaciones

No es posible calcular rentabilidad, utilidad o margen (no hay datos de costos).
La comparación entre solo dos semanas no permite atribuir causalidad a las diferencias observadas.
No se realizan ni publican afirmaciones sobre clientes individuales a partir de variables como ocupación o género; el archivo de clientes no se incluye en el repositorio público.
