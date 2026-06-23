# Models

Pesos entrenados (`.pt`, `.onnx`, `.engine`). **No se commitean** (excluidos por `.gitignore`).

## Convención de nombres

```
yolov8{n|s|m}_construction_safety_{tag}.pt
```

Ejemplos:
- `yolov8n_construction_safety_baseline.pt` — primer entrenamiento (Fase 3)
- `yolov8s_construction_safety_v1.pt` — mejora de precisión (Fase 4)
- `yolov8m_construction_safety_prod.pt` — versión productiva

## Tracking

Métricas y artefactos van a `runs/` (también gitignored). MLflow se incorpora en Fase 12.
