import os
import joblib
import pandas as pd
from flask import current_app

# Singleton loader untuk model dan metadata
_model = None
_metadata = None

def _get_model_dir() -> str:
    return os.path.join(current_app.root_path, "static", "models")

def load_model():
    global _model, _metadata
    model_dir = _get_model_dir()
    model_path = os.path.join(model_dir, "churn_rf_model.pkl")
    metadata_path = os.path.join(model_dir, "churn_metadata.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file tidak ditemukan: {model_path}\n"
            "Pastikan Anda telah menjalankan train_churn_model.py terlebih dahulu."
        )
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file tidak ditemukan: {metadata_path}")

    _model = joblib.load(model_path)
    _metadata = joblib.load(metadata_path)
    current_app.logger.info("✅ Churn prediction model and metadata loaded successfully.")

def get_metadata() -> dict:
    if _metadata is None:
        load_model()
    return _metadata

def get_model():
    if _model is None:
        load_model()
    return _model

class PredictionInputError(ValueError):
    pass

def validate_input(form_data: dict) -> dict:
    errors = []
    cleaned = {}

    options = get_field_options()

    # 1. Validasi Kolom Kategorikal Biner dan Multi-kategori
    categorical_cols = [
        "gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService", 
        "PaperlessBilling", "MultipleLines", "InternetService", "OnlineSecurity", 
        "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", 
        "StreamingMovies", "Contract", "PaymentMethod"
    ]

    for col in categorical_cols:
        val = form_data.get(col, "").strip()
        if not val:
            errors.append(f"Kolom '{col}' tidak boleh kosong.")
        elif val not in options[col]:
            errors.append(f"Nilai '{val}' untuk kolom '{col}' tidak valid.")
        else:
            cleaned[col] = val

    # 2. Validasi Kolom Numerik
    # tenure
    tenure_raw = form_data.get("tenure", "").strip()
    if not tenure_raw:
        errors.append("Kolom 'tenure' tidak boleh kosong.")
    else:
        try:
            tenure = int(tenure_raw)
            if tenure < 0 or tenure > 72:
                errors.append("Lama Berlangganan (tenure) harus antara 0 dan 72 bulan.")
            else:
                cleaned["tenure"] = tenure
        except ValueError:
            errors.append("Lama Berlangganan (tenure) harus berupa angka bulat.")

    # MonthlyCharges
    monthly_raw = form_data.get("MonthlyCharges", "").strip()
    if not monthly_raw:
        errors.append("Kolom 'MonthlyCharges' tidak boleh kosong.")
    else:
        try:
            monthly = float(monthly_raw)
            if monthly < 0 or monthly > 200:
                errors.append("Biaya Bulanan (MonthlyCharges) harus antara 0 dan 200.")
            else:
                cleaned["MonthlyCharges"] = monthly
        except ValueError:
            errors.append("Biaya Bulanan (MonthlyCharges) harus berupa angka desimal.")

    # TotalCharges
    total_raw = form_data.get("TotalCharges", "").strip()
    if not total_raw:
        errors.append("Kolom 'TotalCharges' tidak boleh kosong.")
    else:
        try:
            total = float(total_raw)
            if total < 0 or total > 10000:
                errors.append("Total Biaya (TotalCharges) harus antara 0 dan 10000.")
            else:
                cleaned["TotalCharges"] = total
        except ValueError:
            errors.append("Total Biaya (TotalCharges) harus berupa angka desimal.")

    if errors:
        raise PredictionInputError("<br>".join(errors))

    return cleaned

def predict_churn(form_data: dict) -> dict:
    result = {
        "success": False,
        "prediction": None,
        "churn_risk": "",
        "churn_probability": 0.0,
        "probability_formatted": "",
        "input_summary": {},
        "error": None
    }

    try:
        cleaned = validate_input(form_data)
        meta = get_metadata()
        model = get_model()

        # Pemetaan data untuk input_row
        input_row = {}

        # 1. Kolom numerik dasar
        input_row["SeniorCitizen"] = 1 if cleaned["SeniorCitizen"] == "Yes" else 0
        input_row["tenure"] = cleaned["tenure"]
        input_row["MonthlyCharges"] = cleaned["MonthlyCharges"]
        input_row["TotalCharges"] = cleaned["TotalCharges"]

        # 2. Label Encoding untuk biner
        binary_mappings = meta.get("binary_mappings", {})
        for col in meta.get("binary_cols", []):
            if col != "SeniorCitizen": # SeniorCitizen di-handle manual di atas agar nilainya integer 0/1
                val = cleaned[col]
                input_row[col] = binary_mappings[col][val]

        # 3. One-hot encoding untuk kolom multi-kategori (get_dummies drop_first=True)
        # multicat_cols: ['MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 'PaymentMethod']
        for col in meta.get("multicat_cols", []):
            selected_val = cleaned[col]
            # Ambil semua opsi unik untuk kolom ini
            all_options = meta.get("unique_options", {}).get(col, [])
            # Urutkan secara alfabetis untuk menentukan kategori pertama yang di-drop
            sorted_options = sorted(all_options)
            dropped_first = sorted_options[0]
            
            for val in sorted_options[1:]:
                dummy_col_name = f"{col}_{val}"
                input_row[dummy_col_name] = 1 if selected_val == val else 0

        # Konstruksi DataFrame dengan urutan kolom fitur yang persis sama dengan waktu training
        feature_cols = meta["feature_columns"]
        input_df = pd.DataFrame([{col: input_row.get(col, 0) for col in feature_cols}])

        # Lakukan prediksi
        prediction_val = int(model.predict(input_df)[0]) # 0 = No, 1 = Yes
        proba_val = float(model.predict_proba(input_df)[0][1]) # Probabilitas kelas 1 (Yes Churn)

        # Churn risk ditentukan oleh nilai prediksi:
        # 1 -> Churn: Tinggi
        # 0 -> Churn: Rendah
        churn_risk = "Tinggi" if prediction_val == 1 else "Rendah"
        prob_percent = int(round(proba_val * 100))

        result.update({
            "success": True,
            "prediction": prediction_val,
            "churn_risk": churn_risk,
            "churn_probability": proba_val,
            "probability_formatted": f"{prob_percent}%",
            "input_summary": cleaned
        })

    except PredictionInputError as e:
        result["error"] = str(e)
    except FileNotFoundError as e:
        current_app.logger.error(f"Model file error: {e}")
        result["error"] = "Model Churn belum tersedia. Harap hubungi administrator untuk melatih model terlebih dahulu."
    except Exception as e:
        current_app.logger.exception(f"Prediction error: {e}")
        result["error"] = f"Terjadi kesalahan saat memproses prediksi: {str(e)}"

    return result

def get_field_options() -> dict:
    """
    Opsi dropdown statis yang rapi dan sesuai dengan dataset Telco Customer Churn.
    """
    return {
        "gender": ["Female", "Male"],
        "SeniorCitizen": ["No", "Yes"],
        "Partner": ["No", "Yes"],
        "Dependents": ["No", "Yes"],
        "PhoneService": ["No", "Yes"],
        "MultipleLines": ["No", "Yes", "No phone service"],
        "InternetService": ["DSL", "Fiber optic", "No"],
        "OnlineSecurity": ["No", "Yes", "No internet service"],
        "OnlineBackup": ["No", "Yes", "No internet service"],
        "DeviceProtection": ["No", "Yes", "No internet service"],
        "TechSupport": ["No", "Yes", "No internet service"],
        "StreamingTV": ["No", "Yes", "No internet service"],
        "StreamingMovies": ["No", "Yes", "No internet service"],
        "Contract": ["Month-to-month", "One year", "Two year"],
        "PaperlessBilling": ["No", "Yes"],
        "PaymentMethod": [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ]
    }
