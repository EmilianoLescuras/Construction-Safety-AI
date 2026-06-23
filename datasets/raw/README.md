# Datasets — Raw

Datasets sin procesar. **No se commitean** (excluidos por `.gitignore`).

## Fuente v1

- **Nombre**: Construction Safety v1
- **Origen**: Roboflow — `svrd/construction-safety-gdvov` (versión 1)
- **Formato**: YOLOv8 (`images/` + `labels/` por split)
- **Splits**: 521 train / 114 valid / 82 test
- **Clases (19)**: `Excavator, Gloves, Hardhat, Ladder, Mask, NO-Hardhat, NO-Mask, NO-Safety Vest, Person, Safety Cone, Safety Vest, dump truck, machinery, sedan, trailer, truck, van, vehicle, wheel loader`

## Ubicación local

El dataset se encuentra en:

```
/Users/nanolescuras/Downloads/Construction safety.v1i.yolov8/
```

En la **Fase 2** se preparará un script `scripts/prepare_dataset.py` que copia/enlaza los splits a `datasets/{train,valid,test}/` y genera `config/data.yaml` con rutas absolutas del proyecto.

## Reglas

- Nunca commitear imágenes ni labels.
- Documentar cualquier nuevo dataset agregado en este README.
- Si se incorporan datos de `boots / goggles / harness / ear_protection`, agregarlos en `datasets/raw/<nombre>/` con su propio README.
