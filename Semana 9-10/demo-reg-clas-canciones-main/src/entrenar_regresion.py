"""Primer avance, regresión: compara modelos, elige con validación interna y guarda models/modelo.pkl.

    python -m src.entrenar_regresion

La prueba (2020-2025) se usa una sola vez, con el modelo ya elegido.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from src.artefacto import guardar
from src.variables import (
    COLUMNAS_ENTRADA, cargar_canciones, derivadas, particion_temporal, preprocesamiento, resumen_periodo,
)

CORTE_PROMOCION = 65
ANIO_VALIDACION = 2015  # dentro del entrenamiento: 1995-2014 ajusta, 2015-2019 valida
VARIABLES_EXCLUIDAS = {
    "reproducciones_sem1": "ocurre después del lanzamiento: no existe en el momento de decidir",
    "es_hit": "se calcula a partir del objetivo (popularidad >= 70)",
}

CANDIDATOS = {
    "lineal": lambda: LinearRegression(),
    "ridge": lambda: Ridge(alpha=10),
    "random_forest": lambda: RandomForestRegressor(200, max_depth=8, min_samples_leaf=5, random_state=0, n_jobs=-1),
    "gradient_boosting": lambda: GradientBoostingRegressor(random_state=0),
}


def pipeline_de(estimador):
    return make_pipeline(FunctionTransformer(derivadas), preprocesamiento(), estimador)


def metricas(y, pred):
    return {
        "mae": round(float(mean_absolute_error(y, pred)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(y, pred))), 2),
        "r2": round(float(r2_score(y, pred)), 3),
        "sesgo": round(float((y - pred).mean()), 2),
    }


def entrenar() -> dict:
    datos = cargar_canciones()
    entrenamiento, prueba = particion_temporal(datos)
    X, y = datos[COLUMNAS_ENTRADA], datos["popularidad"]

    # 1) Registro comparativo con validación interna (nunca con la prueba)
    interno = entrenamiento & (datos["anio"] < ANIO_VALIDACION)
    validacion = entrenamiento & (datos["anio"] >= ANIO_VALIDACION)
    media_genero = y[interno].groupby(datos.loc[interno, "genero"]).mean()
    registro = [{"modelo": "linea_base_genero", **metricas(y[validacion], datos.loc[validacion, "genero"].map(media_genero))}]
    for nombre, fabrica in CANDIDATOS.items():
        p = pipeline_de(fabrica()).fit(X[interno], y[interno])
        registro.append({"modelo": nombre, **metricas(y[validacion], p.predict(X[validacion]))})
    registro = pd.DataFrame(registro)
    registro.to_csv("registro_semana9.csv", index=False)
    print(registro.to_string(index=False))

    ganador = registro[registro["modelo"] != "linea_base_genero"].sort_values("mae").iloc[0]["modelo"]
    print("Elegido:", ganador)

    # 2) Reentrenar con todo 1995-2019 y evaluar UNA vez en 2020-2025
    pipeline = pipeline_de(CANDIDATOS[ganador]()).fit(X[entrenamiento], y[entrenamiento])
    pred = pipeline.predict(X[prueba])
    residuo = y[prueba] - pred
    media_tr = y[entrenamiento].groupby(datos.loc[entrenamiento, "genero"]).mean()
    base = datos.loc[prueba, "genero"].map(media_tr)
    por_genero = (
        pd.DataFrame({"genero": datos.loc[prueba, "genero"], "abs": residuo.abs(), "res": residuo})
        .groupby("genero").agg(mae=("abs", "mean"), sesgo=("res", "mean")).round(2)
    )

    ficha = {
        "nombre": f"{ganador} + duración² + baile×energía",
        "tarea": "regresion",
        "objetivo": "popularidad (0-100) que alcanzará la canción",
        "momento_prediccion": "antes del lanzamiento: la disquera decide cuánto invertir en promoción",
        "variables_entrada": list(COLUMNAS_ENTRADA),
        "variables_excluidas": VARIABLES_EXCLUIDAS,
        "entrenamiento": resumen_periodo(datos, entrenamiento),
        "prueba": {**resumen_periodo(datos, prueba), "tipo": "temporal"},
        "linea_base": {"descripcion": "media por género (entrenamiento)", "mae": round(float(mean_absolute_error(y[prueba], base)), 2)},
        "desempeno": metricas(y[prueba], pred),
        "por_genero": por_genero.to_dict(orient="index"),
        "decision": {
            "corte_promocion": CORTE_PROMOCION,
            "regla": "promocionar si la popularidad esperada supera el corte",
            "nota": "el corte lo fija quien responde por el presupuesto, no el modelo",
        },
        "limites": "describe asociaciones en datos sintéticos; no es evidencia causal",
    }
    return guardar(pipeline, ficha)


if __name__ == "__main__":
    entrenar()
