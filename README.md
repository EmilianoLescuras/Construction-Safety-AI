# Construction Safety AI — YOLOv8

Sistema de Computer Vision para detectar incumplimientos de normas de seguridad (EPP) en obras de construcción, basado en YOLOv8.

> Proyecto independiente. Sin relación con otros repositorios privados del autor.

---

## Capacidades objetivo

- Detectar **personas** y elementos de protección personal (EPP).
- Identificar EPP **presente y faltante** por trabajador.
- **Tracking** persistente de trabajadores (ByteTrack).
- **Reglas configurables** de cumplimiento (`config/rules.json`).
- **Alertas** (Telegram / Email / Dashboard).
- **Almacenamiento** de evidencia (imágenes + metadata).
- **Estadísticas** (diarias / semanales / mensuales).
- Inferencia en **tiempo real** sobre webcam, video, RTSP.

---

## Dataset v1

Roboflow — `svrd/construction-safety-gdvov` (v1).

- **19 clases**: `Excavator, Gloves, Hardhat, Ladder, Mask, NO-Hardhat, NO-Mask, NO-Safety Vest, Person, Safety Cone, Safety Vest, dump truck, machinery, sedan, trailer, truck, van, vehicle, wheel loader`
- **Splits**: 521 train / 114 valid / 82 test.
- Las clases `NO-*` indican violación directa: el modelo detecta la ausencia, sin necesidad de inferirlo por overlap.

Clases del plan extendido (`boots`, `goggles`, `ear_protection`, `harness`) → diferidas a v2 cuando se incorporen datos adicionales.

---

## Estructura del proyecto

```
construction_safety_ai/
├── agents/         # Lógica de agentes especializados (rule engine, alert, etc.)
├── backend/        # FastAPI service (Fase 8)
├── config/         # rules.json, model configs
├── database/       # Migraciones, esquemas SQL
├── datasets/       # raw/ processed/ train/ valid/ test/ (gitignored)
├── deployment/     # k8s / cloud manifests
├── docker/         # Dockerfiles
├── docs/           # Documentación técnica
├── frontend/       # Next.js dashboard (Fase 9)
├── inference/      # detect_image|video|webcam|rtsp.py
├── logs/           # Runtime logs (gitignored)
├── models/         # Pesos entrenados (gitignored)
├── monitoring/     # MLflow / Prometheus
├── notebooks/      # EDA, training, evaluación
├── outputs/        # Predicciones generadas (gitignored)
├── scripts/        # Utilities (download, prepare, export)
├── src/            # Código fuente compartido
├── tests/          # pytest
└── .github/workflows/  # CI/CD
```

---

## Roadmap

| Fase | Entregable | Estado |
|------|-----------|--------|
| 1 | Infraestructura + repo privado en GitHub | ✅ |
| 2 | Dataset preparado (`data.yaml` apuntando a splits locales) | ⏳ |
| 3 | Entrenamiento baseline YOLOv8n | ⏳ |
| 4 | YOLOv8s (mejora de precisión) | ⏳ |
| 5 | Inferencia (image / video / webcam) | ⏳ |
| 6 | Tracking con ByteTrack | ⏳ |
| 7 | Rule Engine + `config/rules.json` | ⏳ |
| 8 | Backend FastAPI + PostgreSQL | ⏳ |
| 9 | Dashboard Next.js | ⏳ |
| 10 | Alertas (Telegram / Email) | ⏳ |
| 11 | Docker Compose + CI/CD (GitHub Actions) | ⏳ |
| 12 | Deploy producción + MLOps (MLflow) | ⏳ |

---

## Setup local

```bash
# 1. Clonar y entrar
git clone git@github.com:EmilianoLescuras/construction_safety_ai.git
cd construction_safety_ai

# 2. Entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con valores reales

# 5. Dataset
# Ver datasets/raw/README.md
```

---

## Reglas críticas del proyecto

- **Nunca commitear** pesos de modelos (`*.pt`), datasets crudos, archivos `runs/`, ni `.env`.
- Antes de cada push: escanear secretos y confirmar que el repo sigue privado.
- Repo **privado** hasta que el proyecto esté en estado de demo público.

---

## Licencia

Privado. Sin licencia pública asignada.
