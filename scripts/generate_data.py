#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from becas_rd.data_generation import GenerationConfig, save_synthetic_dataset


if __name__ == "__main__":
    output = Path("data/synthetic_becas_rd.csv")
    cfg = GenerationConfig(n_samples=3000, random_state=42)
    df = save_synthetic_dataset(output, cfg)
    print(f"Saved {len(df)} records to {output}")
