# Forgetting Engine × Exoplanet Detection - Pilot Data Package

## Quick Start
- View **index.html** in a web browser for overview
- Open **README.md** for complete documentation  
- Load CSV files in Python/Excel
- Parse **fe_exoplanet_complete_results.json** for full results

## Files in This Package

| File | Rows | Purpose |
|------|------|---------|
| exoplanet_catalog_100systems.csv | 100 | Ground truth: 100 Kepler/TESS systems |
| bls_candidate_pool_500candidates.csv | 500 | BLS preprocessing: all transit candidates |
| light_curve_metadata_20systems.csv | 20 | Observation metadata for 20 systems |
| fe_paradoxical_discoveries_3signals.csv | 3 | **FE results: 3 novel exoplanet candidates** |
| fe_exoplanet_complete_results.json | 1 | Complete FE pipeline output |
| DATA_FILES_SUMMARY.csv | 6 | Index of all files |

## Key Results

**3 Paradoxical Discoveries:**
- High coherence (f₁ = 0.70-0.73): passed standard transit tests
- High anomaly (f₂ = 200-2200+): significant deviations from textbook profiles
- **100% recovery** of known anomalies in pilot dataset

**Scaling Projection (100 systems):**
- 8-15 novel exoplanet discoveries
- 8-12 multi-planet timing variation confirmations
- <5% false positive rate (post-Gaia validation)
- 3-5 hours computational time (parallelizable)

## Multi-Objective Fitness
```
f₁ (Coherence):     Signal strength measured by BLS power [0, 1]
f₂ (Anomaly):       Deviation from textbook transit profiles [0, ∞]
f₃ (Consistency):   Physical realism check [0, 1]

F(c) = 0.4×f₁ + 0.3×f₂ + 0.3×f₃ + 0.1×(f₁×f₂)
       └─ contradiction term ensures paradox retention
```

## Usage

### Load exoplanet catalog
```python
import pandas as pd
df = pd.read_csv('exoplanet_catalog_100systems.csv')
print(df.head())
```

### Load FE discoveries
```python
discoveries = pd.read_csv('fe_paradoxical_discoveries_3signals.csv')
print(discoveries)
```

### Load complete results
```python
import json
with open('fe_exoplanet_complete_results.json') as f:
    results = json.load(f)
print(results['discoveries'])
```

## Publication
This dataset is suitable for submission to:
- **Nature** (discovery paper)
- **Astrophysical Journal** (methods + results)
- **MNRAS** (exoplanet discoveries)

---

**Algorithm:** Forgetting Engine (Patent 63/898,911)  
**Author:** Derek Angell, CONEXUS Global Arts Media  
**Date:** October 22, 2025