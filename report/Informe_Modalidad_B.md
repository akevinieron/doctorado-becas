# Modalidad B - Sistema de Becas RD con IA/ML

## Abstract

Este trabajo presenta un MVP reproducible en Python/Colab para apoyo a decisiones en becas (nacional e internacional) en Republica Dominicana. El sistema combina un modelo de clasificacion para estimar probabilidad de adjudicacion con un asistente conversacional basado en recuperacion documental y reglas. Se analiza desempeno predictivo, equidad regional y limites del uso de IA.

## Introduccion

- Problema: la evaluacion de postulaciones puede ser costosa, heterogenea y poco transparente.
- Motivacion: construir una herramienta de apoyo (no de reemplazo) para orientar postulantes y apoyar analisis tecnico.
- Objetivo: integrar prediccion, explicabilidad y orientacion conversacional en un flujo reproducible.

## Desarrollo

### Datos y metodologia

- Dataset sintetico de postulantes (3000 registros).
- Variable objetivo: adjudicacion (0/1).
- Modelos: baseline logistico y modelo principal de arboles.
- Auditoria de equidad: paridad regional minima mediante ajuste de umbrales.

### Arquitectura del sistema

- Modulo de datos sinteticos.
- Modulo de entrenamiento y prediccion.
- Asistente RAG simple + reglas para orientacion.

### Resultados

Incluir tablas de `report/assets/metrics_summary.csv` y analisis de `report/assets/results_summary.md`.

### Evaluacion critica del uso de IA

- Que fue util: velocidad de prototipado, generacion de variantes, apoyo para refactor.
- Limites: riesgo de alucinacion documental, sobreconfianza en metricas, sensibilidad a supuestos sinteticos.
- Decisiones humanas: definicion de criterios de equidad, interpretacion de trade-offs, limites de uso.
- Idea rechazada/modificada: automatizar adjudicacion final sin revision humana (rechazada por riesgo etico).

## Conclusiones

El MVP demuestra viabilidad tecnica para apoyo a procesos de becas, pero exige gobernanza humana, auditoria y validacion con datos reales antes de uso institucional.

## Trabajo futuro

- Integrar datos reales anonimizados.
- Evaluar fairness multi-grupo (region + genero + ingreso).
- Crear dashboard interactivo para comite evaluador.

## Transparencia de asistencia IA

- Partes asistidas por IA: ideacion inicial, bocetos de codigo y redaccion preliminar.
- Partes no delegadas: criterios finales, validacion tecnica, evaluacion critica y conclusiones.

## Recursos externos

- Enlace al video pechakucha: `PENDIENTE`
- Enlace a recursos multimedia en nube: `PENDIENTE`
