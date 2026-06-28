# Dataset Stats — riskalert-mining (pivot, 34 classes)

_Generated 2026-06-28. Source: Roboflow emilianos-workspace-6gmup/riskalert-mining-r07if v1._

## Splits

| split | images | boxes |
|-------|-------:|------:|
| train | 498 | 1644 |
| valid | 142 | 494 |
| test | 72 | 207 |
| **total** | **712** | **2345** |

## Per-class instance counts (all splits)

| id | class | instances | share |
|---:|-------|----------:|------:|
| 9 | PERSONA_CON_CASCO | 488 | 20.8% |
| 13 | PERSONA_ROPA_CINTA_REFLECTIVA | 347 | 14.8% |
| 1 | CAMIONETA | 187 | 8.0% |
| 5 | EXCAVADORA | 185 | 7.9% |
| 4 | CONOS_DELIMITADORES | 151 | 6.4% |
| 33 | VOLQUETE | 146 | 6.2% |
| 19 | PERSONA_SIN_ROPA_CINTA_REFLECTIVA | 101 | 4.3% |
| 7 | MOTONIVELADORA | 91 | 3.9% |
| 17 | PERSONA_SIN_LENTES | 84 | 3.6% |
| 14 | PERSONA_SIN_CASCO | 77 | 3.3% |
| 8 | PERSONA | 67 | 2.9% |
| 2 | CARGADOR_FRONTAL | 66 | 2.8% |
| 22 | RODILLO | 62 | 2.6% |
| 21 | RETRO_EXCAVADORA | 51 | 2.2% |
| 10 | PERSONA_CON_GUANTES | 41 | 1.7% |
| 16 | PERSONA_SIN_GUANTES | 33 | 1.4% |
| 23 | SENALIZACION | 30 | 1.3% |
| 26 | VIA_CON_MURO_SEGURIDAD | 27 | 1.2% |
| 11 | PERSONA_CON_LENTES | 26 | 1.1% |
| 25 | VIA_BUEN_ESTADO | 14 | 0.6% |
| 29 | VIA_OBSTACULIZADA | 14 | 0.6% |
| 3 | CISTERNA_AGUA | 9 | 0.4% |
| 18 | PERSONA_SIN_RESPIRADOR | 8 | 0.3% |
| 6 | MINIBUS | 7 | 0.3% |
| 27 | VIA_EN_MAL_ESTADO | 7 | 0.3% |
| 0 | ANIMAL | 5 | 0.2% |
| 15 | PERSONA_SIN_CHALECO | 5 | 0.2% |
| 24 | TRACTOR | 5 | 0.2% |
| 32 | VIA_SIN_MURO_SEGURIDAD | 4 | 0.2% |
| 12 | PERSONA_CON_RESPIRADOR | 3 | 0.1% |
| 20 | POLVO | 1 | 0.0% |
| 28 | VIA_NO_REGADA | 1 | 0.0% |
| 30 | VIA_SATURADA | 1 | 0.0% |
| 31 | VIA_SENALIZADA | 1 | 0.0% |

## Notes

- **Sparse classes (<20 instances):** ANIMAL, CISTERNA_AGUA, MINIBUS, PERSONA_CON_RESPIRADOR, PERSONA_SIN_CHALECO, PERSONA_SIN_RESPIRADOR, POLVO, TRACTOR, VIA_BUEN_ESTADO, VIA_EN_MAL_ESTADO, VIA_NO_REGADA, VIA_OBSTACULIZADA, VIA_SATURADA, VIA_SENALIZADA, VIA_SIN_MURO_SEGURIDAD — expect weak AP50 here; candidates for more data later.
- Heavy imbalance: `PERSONA_CON_CASCO` and `PERSONA_ROPA_CINTA_REFLECTIVA` dominate; many `VIA_*` road-state classes are rare.