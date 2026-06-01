import sys
from pathlib import Path as Pth

import joblib as jl
import pandas as pd
from sentence_transformers import SentenceTransformer as St
from sklearn.linear_model import LogisticRegression as Lr
from sklearn.model_selection import train_test_split as tts


def vec(enc, txt):
    return enc.encode(
        txt.tolist(),
        batch_size=16,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


def run():
    if len(sys.argv) != 3:
        print("Использование: python scripts/train_classifier.py data.csv model.joblib")
        return 1

    src = Pth(sys.argv[1])
    dst = Pth(sys.argv[2])
    df = pd.read_csv(src)
    tr, te = tts(
        df,
        test_size=0.1,
        random_state=42,
        shuffle=True,
        stratify=df["category"],
    )

    enc = St("cointegrated/rubert-tiny2")
    xtr = vec(enc, tr["text"])
    ytr = tr["category"].to_numpy()
    clf = Lr(max_iter=1000)
    clf.fit(xtr, ytr)

    dst.parent.mkdir(parents=True, exist_ok=True)
    bun = {
        "knn": clf,
        "class_mapping": {},
        "model_name": "RuBERT Tiny2 LogisticRegression",
        "encoder_path": "dummy_path_none",
        "source_encoder_name": "cointegrated/rubert-tiny2",
    }
    jl.dump(bun, dst, compress=3)
    print(f"Обучено строк: {len(tr)}")
    print(f"Проверка строк: {len(te)}")
    print(f"Модель сохранена: {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
