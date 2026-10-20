"""Segundo avance, clasificación: compara clasificadores por costo, elige con validación interna y guarda models/modelo.pkl.

    python -m src.entrenar_clasificacion

Cada candidato recibe su umbral de menor costo con probabilidades fuera de muestra dentro de 1995-2019
(ventana temporal creciente). Se elige el candidato de menor costo en esa validación y la prueba
(2020-2025) se usa una sola vez, con el modelo y el umbral ya elegidos.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from src.artefacto import guardar
from src.variables import (
    COLUMNAS_ENTRADA, RAIZ, cargar_canciones, derivadas, particion_temporal, preprocesamiento, resumen_periodo,
)

COSTO_FALSO_NEGATIVO = 3  # dejar sin promoción una canción que sí fue hit
COSTO_FALSO_POSITIVO = 1  # promocionar una canción que no fue hit
PLIEGUES_VALIDACION = 4
RUTA_REGISTRO = RAIZ / "registro_semana10.csv"
VARIABLES_EXCLUIDAS = {
    "reproducciones_sem1": "ocurre después del lanzamiento: no existe en el momento de decidir",
    "popularidad": "define es_hit: usarla como entrada equivale a conocer la respuesta",
}

CANDIDATOS = {
    "logistica": lambda: LogisticRegression(max_iter=1000),
    "logistica_regularizada": lambda: LogisticRegression(C=0.1, max_iter=1000),
    "random_forest": lambda: RandomForestClassifier(300, max_depth=6, min_samples_leaf=5, random_state=0, n_jobs=-1),
    "gradient_boosting": lambda: GradientBoostingClassifier(random_state=0),
}


def pipeline_de(estimador):
    return make_pipeline(FunctionTransformer(derivadas), preprocesamiento(), estimador)


def costo(real, pred) -> int:
    falsos_negativos = int(((real == 1) & ~pred).sum())
    falsos_positivos = int(((real == 0) & pred).sum())
    return COSTO_FALSO_NEGATIVO * falsos_negativos + COSTO_FALSO_POSITIVO * falsos_positivos


def probabilidades_fuera_de_muestra(fabrica, X, y):
    """Probabilidades de cada bloque temporal con un modelo ajustado solo con los años anteriores."""
    X, y = X.reset_index(drop=True), y.reset_index(drop=True)
    reales, probs = [], []
    for ajuste, validacion in TimeSeriesSplit(n_splits=PLIEGUES_VALIDACION).split(X):
        modelo = pipeline_de(fabrica()).fit(X.iloc[ajuste], y.iloc[ajuste])
        probs.append(modelo.predict_proba(X.iloc[validacion])[:, 1])
        reales.append(y.iloc[validacion].to_numpy())
    return np.concatenate(reales), np.concatenate(probs)


def mejor_umbral(real, prob) -> float:
    umbrales = np.round(np.arange(0.05, 0.96, 0.01), 2)
    costos = [costo(real, prob >= u) for u in umbrales]
    return float(umbrales[int(np.argmin(costos))])


def metricas(real, prob, umbral) -> dict:
    pred = prob >= umbral
    return {
        "costo": costo(real, pred),
        "precision": round(float(precision_score(real, pred, zero_division=0)), 3),
        "recall": round(float(recall_score(real, pred)), 3),
        "auc": round(float(roc_auc_score(real, prob)), 3),
    }


def entrenar() -> dict:
    datos = cargar_canciones()
    entrenamiento, prueba = particion_temporal(datos)
    X, y = datos[COLUMNAS_ENTRADA], datos["es_hit"]

    # 1) Registro comparativo con validación interna (nunca con la prueba)
    registro, umbrales = [], {}
    for nombre, fabrica in CANDIDATOS.items():
        real, prob = probabilidades_fuera_de_muestra(fabrica, X[entrenamiento], y[entrenamiento])
        umbrales[nombre] = mejor_umbral(real, prob)
        registro.append({"modelo": nombre, "umbral": umbrales[nombre], **metricas(real, prob, umbrales[nombre])})
    base = {"modelo": "linea_base_nunca_hit", "umbral": None, "costo": costo(real, np.zeros_like(real, dtype=bool)),
            "precision": None, "recall": 0.0, "auc": None}
    registro = pd.DataFrame([base, *registro])
    registro.to_csv(RUTA_REGISTRO, index=False)
    print(registro.to_string(index=False))

    ganador = registro[registro["modelo"] != base["modelo"]].sort_values("costo", kind="stable").iloc[0]["modelo"]
    umbral = umbrales[ganador]
    print("Elegido:", ganador, "con umbral", umbral)

    # 2) Reentrenar con todo 1995-2019 y evaluar UNA vez en 2020-2025
    pipeline = pipeline_de(CANDIDATOS[ganador]()).fit(X[entrenamiento], y[entrenamiento])
    prob = pipeline.predict_proba(X[prueba])[:, 1]
    pred = prob >= umbral
    real = y[prueba].to_numpy()
    tn, fp, fn, tp = confusion_matrix(real, pred).ravel()

    por_genero = (
        pd.DataFrame({"genero": datos.loc[prueba, "genero"], "hit": real, "promover": pred})
        .assign(detectado=lambda d: d["hit"] & d["promover"], falso_positivo=lambda d: ~d["hit"].astype(bool) & d["promover"])
        .groupby("genero")
        .agg(canciones=("hit", "size"), hits=("hit", "sum"), detectados=("detectado", "sum"), falsos_positivos=("falso_positivo", "sum"))
        .astype(int)
    )

    ficha = {
        "nombre": f"{ganador} + umbral por costos",
        "tarea": "clasificacion",
        "objetivo": "es_hit: 1 si la canción alcanza 70 puntos de popularidad",
        "momento_prediccion": "antes del lanzamiento: la disquera decide cuánto invertir en promoción",
        "variables_entrada": list(COLUMNAS_ENTRADA),
        "variables_excluidas": VARIABLES_EXCLUIDAS,
        "entrenamiento": resumen_periodo(datos, entrenamiento),
        "prueba": {**resumen_periodo(datos, prueba), "tipo": "temporal"},
        "seleccion": {
            "candidatos": list(CANDIDATOS),
            "criterio": f"menor costo con probabilidades fuera de muestra en 1995-2019 ({PLIEGUES_VALIDACION} bloques temporales)",
            "costo_validacion": int(registro.loc[registro["modelo"] == ganador, "costo"].iloc[0]),
        },
        "linea_base": {
            "descripcion": "predecir siempre 'no hit'",
            "costo": costo(real, np.zeros_like(pred)),
        },
        "desempeno": {
            "precision": round(float(precision_score(real, pred)), 3),
            "recall": round(float(recall_score(real, pred)), 3),
            "auc": round(float(roc_auc_score(real, prob)), 3),
            "matriz_confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            "costo": costo(real, pred),
        },
        "por_genero": por_genero.to_dict(orient="index"),
        "decision": {
            "umbral": umbral,
            "costos": {"falso_negativo": COSTO_FALSO_NEGATIVO, "falso_positivo": COSTO_FALSO_POSITIVO},
            "regla": "promocionar si la probabilidad de hit supera el umbral",
            "nota": "los costos los fija quien responde por el presupuesto, no el modelo",
        },
        "limites": "probabilidades sin calibrar; describe asociaciones en datos sintéticos",
    }
    return guardar(pipeline, ficha)


if __name__ == "__main__":
    entrenar()
