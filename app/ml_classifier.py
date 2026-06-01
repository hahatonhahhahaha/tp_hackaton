from functools import lru_cache
from pathlib import Path
import joblib
from sentence_transformers import SentenceTransformer
base = Path(__file__).resolve().parent.parent
BUNDLE_PATH = base / "models" / "knnbase.joblib"
@lru_cache(maxsize=1)
def load_bundle():
    return joblib.load(BUNDLE_PATH)

@lru_cache(maxsize=1)
def load_encoder():
    bundle = load_bundle()

    encoder_path = Path(bundle["encoder_path"])

    if encoder_path.exists():
        return SentenceTransformer(str(encoder_path))

    return SentenceTransformer(bundle["source_encoder_name"])\

def predict_category(text):
    bundle = load_bundle()
    encoder = load_encoder()
    embedding = encoder.encode(
        [text],
        batch_size=16,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    prediction = bundle["knn"].predict(embedding)

    return int(prediction[0])
