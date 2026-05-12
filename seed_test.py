import requests
from datetime import datetime

API_URL = "http://localhost:8000/api"

def seed_data():
    # 1. Create a patient
    patient_res = requests.post(f"{API_URL}/patients", json={
        "dni": "20111222",
        "first_name": "Maria",
        "last_name": "Rodriguez",
        "birth_date": "1985-05-15",
        "gender": "F",
        "address": "Barrio Libertad",
        "commune_id": 2, # Pozuelos
        "phone": "0414-1234567",
        "marital_status": "Soltera"
    })
    
    if patient_res.status_code == 200:
        patient = patient_res.json()
        patient_id = patient['id']
        print(f"Created patient {patient_id}")
        
        # 2. Create 3 clinical records for the same pathology to trigger an outbreak
        for i in range(3):
            record_res = requests.post(f"{API_URL}/clinical_records", json={
                "patient_id": patient_id,
                "primary_pathology": "Dengue",
                "secondary_pathologies": "",
                "cie10_code": "A90",
                "risk_level": "Medio",
                "evolutionary_state": "Agudo",
                "priority": "Urgente",
                "medications": "Acetaminofén",
                "observations": f"Paciente con síntomas febriles - Caso {i+1}",
                "assigned_doctor_id": 1
            })
            if record_res.status_code == 200:
                print(f"Created record {i+1}")
            else:
                print(f"Error creating record {i+1}: {record_res.text}")
    else:
        print(f"Error creating patient: {patient_res.text}")

if __name__ == "__main__":
    import time
    time.sleep(2) # Wait for server
    seed_data()
