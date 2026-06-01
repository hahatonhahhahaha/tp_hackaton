from functools import lru_cache as lru
from pathlib import Path as Pth

import joblib as jl


PTH = Pth(__file__).resolve().parent.parent / "models" / "logregression.joblib"
MAP = {
    "incidents": "incidents",
    "servicerequests": "service_requests",
    "spam": "spam",
    "hr": "прочее",
    "unclassifed": "прочее",
    "unclassified": "прочее",
}


@lru(maxsize=1)
def bdl():
    return jl.load(PTH)


@lru(maxsize=1)
def enc():
    from sentence_transformers import SentenceTransformer as St

    b = bdl()
    p = Pth(str(b.get("encoder_path", "")))

    if p.exists():
        return St(str(p))

    return St(str(b["source_encoder_name"]))


def cat(x):
    s = str(x).strip()
    return MAP.get(s.lower(), "прочее")


def prd(txt):
    e = enc()
    b = bdl()
    x = e.encode(
        [txt],
        batch_size=16,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    y = b["knn"].predict(x)[0]
    m = b.get("class_mapping", {})

    try:
        y = m.get(int(y), y)
    except (TypeError, ValueError):
        y = m.get(y, y)

    return cat(y)


def inf(sub, txt):
    t = f"{sub or ''} {txt or ''}".strip()

    if not t:
        return {
            "ml_category": "прочее",
            "ml_status": "empty",
        }

    try:
        return {
            "ml_category": prd(t),
            "ml_status": "ok",
        }
    except Exception as err:
        return {
            "ml_category": "",
            "ml_status": type(err).__name__,
        }
