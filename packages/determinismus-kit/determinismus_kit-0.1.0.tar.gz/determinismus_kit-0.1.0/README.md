# Determinismus-Kit für Python

Ein kleines Toolkit, das Python-Läufe reproduzierbarer macht:
- Seeds setzen (`random`, optional `numpy`, optional `torch`)
- Threads bändigen (OMP/BLAS/MKL)
- Umgebungs-Snapshot (Versionen/ENV)
- CLI: `python -m determinismus_kit run ...` oder `determinismus-kit`

## Installation (lokal)
```bash
pip install .
```
oder für Entwicklung:
```bash
pip install -e .
```

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

Optionen:
- `--seed` Seed für RNGs (Default: 123)
- `--threads` Anzahl Threads für BLAS/OMP (Default: 1)
- `--snapshot PATH` Umgebungssnapshot schreiben
- `--no-cuda-determinism` CUDA-Deterministik nicht erzwingen

Argumente für das Zielskript kommen **nach `--`**:
```bash
determinismus-kit run --seed 123 your_script.py -- --foo bar
```

## Hinweise
- NumPy/PyTorch werden automatisch unterstützt, wenn installiert.
- Kleine Abweichungen auf verschiedener Hardware/OS sind möglich (Floating-Point).
- Das Toolkit ist „best effort“ – für viele Praxisfälle ausreichend.
