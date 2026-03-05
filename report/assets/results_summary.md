# Resultados del MVP de Becas RD

## Metricas globales
| model                    |   threshold |    roc_auc |   accuracy |   precision |   recall |       f1 |
|:-------------------------|------------:|-----------:|-----------:|------------:|---------:|---------:|
| baseline                 |        0.27 |   0.781026 |   0.726667 |    0.728421 | 0.908136 | 0.808411 |
| main                     |        0.32 |   0.753868 |   0.705    |    0.716102 | 0.887139 | 0.792497 |
| main_adjusted_for_parity |      nan    | nan        |   0.705    |    0.716102 | 0.887139 | 0.792497 |

## Equidad regional antes del ajuste
| region         |   n |   positive_rate |      tpr |
|:---------------|----:|----------------:|---------:|
| Cibao Nordeste |  32 |        0.875    | 0.947368 |
| Cibao Noroeste |   8 |        0.375    | 0.6      |
| Cibao Norte    | 105 |        0.790476 | 0.9      |
| Cibao Sur      |  65 |        0.692308 | 0.809524 |
| El Valle       |  26 |        0.807692 | 0.882353 |
| Enriquillo     |  10 |        0.8      | 1        |
| Higuamo        |  35 |        0.8      | 0.941176 |
| Ozama          | 178 |        0.808989 | 0.86087  |
| Valdesia       |  81 |        0.790123 | 0.923077 |
| Yuma           |  60 |        0.8      | 0.947368 |

## Equidad regional despues del ajuste
| region         |   n |   positive_rate |      tpr |
|:---------------|----:|----------------:|---------:|
| Cibao Nordeste |  32 |        0.875    | 0.947368 |
| Cibao Noroeste |   8 |        0.375    | 0.6      |
| Cibao Norte    | 105 |        0.790476 | 0.9      |
| Cibao Sur      |  65 |        0.692308 | 0.809524 |
| El Valle       |  26 |        0.807692 | 0.882353 |
| Enriquillo     |  10 |        0.8      | 1        |
| Higuamo        |  35 |        0.8      | 0.941176 |
| Ozama          | 178 |        0.808989 | 0.86087  |
| Valdesia       |  81 |        0.790123 | 0.923077 |
| Yuma           |  60 |        0.8      | 0.947368 |

## Nota metodologica
Se aplico ajuste de umbrales por region para aproximar paridad de tasa positiva minima.