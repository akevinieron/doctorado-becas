#!/usr/bin/env python3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from becas_rd.modeling import train_models


if __name__ == "__main__":
    df = pd.read_csv("data/synthetic_becas_rd.csv")
    result = train_models(df, artifacts_dir="artifacts")
    print("Training complete")
    print(result.metrics)
