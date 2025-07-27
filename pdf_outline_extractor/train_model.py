
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("train_all.csv")
df["label"] = df["label"].apply(lambda x: x if x in ["H1", "H2", "H3"] else "None")

font_encoder = LabelEncoder()
df["font_name_encoded"] = font_encoder.fit_transform(df["font_name"])
joblib.dump(font_encoder, "font_encoder.joblib")

punct_encoder = LabelEncoder()
df["punctuation_encoded"] = punct_encoder.fit_transform(df["punctuation_type"])
joblib.dump(punct_encoder, "punctuation_encoder.joblib")

features = [
    "font_size", "font_name_encoded", "is_bold", "is_italic",
    "x0", "x1", "y0", "y1",
    "char_count", "capital_ratio", "line_y_ratio",
    "punctuation_encoded", "has_numbering"
]

X = df[features]
y = df["label"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
joblib.dump(label_encoder, "label_encoder.joblib")

clf = XGBClassifier(
    n_estimators=500,
    max_depth=10,
    learning_rate=0.3,
    min_child_weight=1,
    objective="multi:softprob",
    eval_metric="mlogloss"
)
clf.fit(X, y_encoded)

y_pred = clf.predict(X)

joblib.dump(clf, "heading_classifier.joblib")
