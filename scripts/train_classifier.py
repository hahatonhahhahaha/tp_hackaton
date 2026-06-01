from google.colab import drive
drive.mount("/content/drive")

import pandas as pd
df = pd.read_csv("/content/drive/MyDrive/real_dataset (2).csv")
df
from pathlib import Path
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report,ConfusionMatrixDisplay


import json
import joblib
import numpy as np
import torch
import sklearn
import sentence_transformers


train_df, test_df = train_test_split(df,test_size=0.05,random_state=42,shuffle=True,stratify=df["category"])
print("обуч:", train_df.shape)
print("тест:", test_df.shape)


model = "cointegrated/rubert-tiny2"
enc = SentenceTransformer(model)
def encode_texts(texts):
    return enc.encode(texts.tolist(),batch_size=16, show_progress_bar=True,convert_to_numpy=True,normalize_embeddings=True)
X_train = encode_texts(train_df["text"])
X_test = encode_texts(test_df["text"])
y_train = train_df["category"].to_numpy()
y_test = test_df["category"].to_numpy()

print("трейн", X_train.shape)
print("тест", X_test.shape)


vibork = [1, 2,3,4, 5, 6,7, 11, 13, 15]
results = []
for k in vibork:
    knn = KNeighborsClassifier(n_neighbors=k,weights="distance",metric="cosine",algorithm="brute")
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    results.append({"k": k, "accuracy": accuracy_score(y_test, y_pred), "macro_f1": f1_score(y_test, y_pred,average="macro")})

df_res = pd.DataFrame(results).sort_values(by=["macro_f1", "accuracy"],ascending=False)
df_res


knn = KNeighborsClassifier(n_neighbors=7,weights="distance",metric="cosine",algorithm="brute",n_jobs=-1)
knn.fit(X_train, y_train)

test_predictions = knn.predict(X_test)

print(classification_report(y_test,test_predictions))
ConfusionMatrixDisplay.from_predictions(y_test,test_predictions)


encode_dora = "/content/drive/MyDrive/mail_class/encoder"
knnbase= "/content/drive/MyDrive/mail_class/knnbase.joblib"
metaput = "/content/drive/MyDrive/mail_class/metadata.json"
enc.save_pretrained(encode_dora)
bundle = {"knn": knn,"encoder_path": str(encode_dora), "source_encoder_name": "cointegrated/rubert-tiny2"}
joblib.dump(bundle,knnbase,compress=3)
