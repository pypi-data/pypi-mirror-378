# Determinismus-Kit für Python

[![PyPI](https://img.shields.io/pypi/v/determinismus-kit.svg)](https://pypi.org/project/determinismus-kit/)
[![TestPyPI](https://img.shields.io/badge/TestPyPI-Link-blue)](https://test.pypi.org/project/determinismus-kit/)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-black)](https://github.com/DrMabuseistda/determinismus-kit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Ein kleines Toolkit, das Python-Läufe reproduzierbarer macht:

- Seeds setzen (`random`, optional `numpy`, optional `torch`)
- Threads bändigen (OMP/BLAS/MKL)
- Umgebungs-Snapshot (Versionen/ENV)
- CLI: `python -m determinismus_kit run ...` oder `determinismus-kit`

---

## Installation

### Für Entwicklung
```bash
pip install -e .
```

### Von TestPyPI
Das Paket ist aktuell auf TestPyPI verfügbar:
```bash
pip install -i https://test.pypi.org/simple/ determinismus-kit
```

---

## Nutzung

### Als Bibliothek
```python
from determinismus_kit import deterministic

with deterministic(seed=123, threads=1):
    import random
    print([random.random() for _ in range(3)])
```

### Als CLI
```bash
python -m determinismus_kit run --seed 123 --threads 1 your_script.py
# oder
determinismus-kit run --seed 123 --threads 1 your_script.py
```

Argumente für das Zielskript kommen **nach `--`**:
```bash
determinismus-kit run --seed 123 your_script.py -- --foo bar
```

---

## Optionen

- `--seed` Seed für RNGs (Default: 123)  
- `--threads` Anzahl Threads für BLAS/OMP (Default: 1)  
- `--snapshot PATH` Umgebungssnapshot schreiben  
- `--no-cuda-determinism` CUDA-Deterministik nicht erzwingen  
- `-c/--code` Direkt Python-Code ausführen  

---

## Beispiele

### 1. Python-Skript deterministisch ausführen
```bash
determinismus-kit run --seed 123 --threads 1 examples/simple_random.py
```

### 2. Direkt Python-Code per `-c/--code` ausführen
```bash
determinismus-kit run --seed 42 --threads 1 -c "import random; print([random.random() for _ in range(3)])"
```

Mit gleichem Seed zweimal identisch:
```
[0.6394267984578837, 0.025010755222666936, 0.27502931836911926]
[0.6394267984578837, 0.025010755222666936, 0.27502931836911926]
```

Mit anderem Seed:
```
[0.32383276483316237, 0.15084917392450192, 0.6509344730398537]
```

---

## Hinweise

- NumPy/PyTorch werden automatisch unterstützt, wenn installiert.  
- Kleine Abweichungen auf verschiedener Hardware/OS sind möglich (Floating-Point).  
- Das Toolkit ist „best effort“ – für viele Praxisfälle ausreichend.  

---

## Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE).
