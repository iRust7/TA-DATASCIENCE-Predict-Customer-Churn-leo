import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Path dataset
dataset_path = r"C:\Users\ASUS\Downloads\WA_Fn-UseC_-Telco-Customer-Churn.csv"
model_dir = os.path.join("app", "static", "models")

# Buat folder models jika belum ada
os.makedirs(model_dir, exist_ok=True)

print(f"Membaca dataset dari {dataset_path}...")
df = pd.read_csv(dataset_path)

# 1. Data Cleaning
df = df.copy()
df = df.drop('customerID', axis=1, errors='ignore')

# Konversi TotalCharges ke numerik dan hapus missing values (baris kosong)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
initial_rows = len(df)
df.dropna(inplace=True)
print(f"Dihapus {initial_rows - len(df)} baris dengan nilai kosong di TotalCharges. Sisa data: {len(df)}")

# 2. Pisahkan Fitur (X) dan Target (y)
X = df.drop('Churn', axis=1)
y = df['Churn']

# Encode target Churn ('No' -> 0, 'Yes' -> 1)
le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)
target_mapping = dict(zip(le_target.classes_, le_target.transform(le_target.classes_)))
print(f"Target Churn mapping: {target_mapping}")

# 3. Identifikasi dan Preprocessing Fitur Kategorikal
categorical_cols = [col for col in X.columns if X[col].dtype == 'object']
binary_cols = [col for col in categorical_cols if X[col].nunique() == 2]
multicat_cols = [col for col in categorical_cols if X[col].nunique() > 2]

print(f"Fitur biner: {binary_cols}")
print(f"Fitur multi-kategori: {multicat_cols}")

# Lakukan Label Encoding untuk kolom biner dan simpan mapping-nya
binary_mappings = {}
X_processed = X.copy()
for col in binary_cols:
    le = LabelEncoder()
    X_processed[col] = le.fit_transform(X_processed[col])
    binary_mappings[col] = dict(zip(le.classes_, [int(v) for v in le.transform(le.classes_)]))

# Lakukan One-Hot Encoding (get_dummies) untuk kolom multi-kategori
X_processed = pd.get_dummies(X_processed, columns=multicat_cols, drop_first=True)

# Simpan urutan kolom fitur final yang digunakan model
feature_columns = X_processed.columns.tolist()
print(f"Jumlah kolom fitur final: {len(feature_columns)}")

# 4. Latih Model Random Forest (sesuai spesifikasi notebook)
print("Melatih model RandomForestClassifier...")
model_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model_rf.fit(X_processed, y_encoded)
print("Model berhasil dilatih.")

# 5. Simpan Model dan Metadata ke folder static/models/
model_path = os.path.join(model_dir, "churn_rf_model.pkl")
metadata_path = os.path.join(model_dir, "churn_metadata.pkl")

joblib.dump(model_rf, model_path)
print(f"Model berhasil disimpan ke: {model_path}")

metadata = {
    "feature_columns": feature_columns,
    "binary_cols": binary_cols,
    "multicat_cols": multicat_cols,
    "binary_mappings": binary_mappings,
    "target_mapping": target_mapping,
    # Opsi pilihan unik untuk form dropdown di UI
    "unique_options": {col: df[col].unique().tolist() for col in categorical_cols}
}
joblib.dump(metadata, metadata_path)
print(f"Metadata berhasil disimpan ke: {metadata_path}")
