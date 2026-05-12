from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database as db_config
from datetime import datetime, timedelta
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SISSOT - Sistema de Salud Sotillo")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
db_config.init_db()

# Dependency
def get_db():
    db = db_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_patients = db.query(db_config.Patient).count()
    total_records = db.query(db_config.ClinicalRecord).count()
    total_alerts = db.query(db_config.Alert).filter(db_config.Alert.status == "active").count()
    
    # Pathologies count for chart
    pathologies = db.query(db_config.ClinicalRecord.primary_pathology).all()
    pathology_stats = {}
    for p in pathologies:
        name = p[0]
        pathology_stats[name] = pathology_stats.get(name, 0) + 1
        
    return {
        "total_patients": total_patients,
        "total_records": total_records,
        "active_alerts": total_alerts,
        "pathology_distribution": pathology_stats
    }

@app.get("/api/communes")
async def get_communes(db: Session = Depends(get_db)):
    return db.query(db_config.Commune).all()

@app.get("/api/patients")
async def get_patients(db: Session = Depends(get_db)):
    return db.query(db_config.Patient).all()

@app.post("/api/patients")
async def create_patient(patient_data: dict, db: Session = Depends(get_db)):
    # Basic logic for now, should use Pydantic models
    new_patient = db_config.Patient(
        dni=patient_data.get("dni"),
        first_name=patient_data.get("first_name"),
        last_name=patient_data.get("last_name"),
        birth_date=datetime.fromisoformat(patient_data.get("birth_date")),
        gender=patient_data.get("gender"),
        address=patient_data.get("address"),
        commune_id=patient_data.get("commune_id"),
        phone=patient_data.get("phone"),
        marital_status=patient_data.get("marital_status")
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(db_config.Patient).filter(db_config.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

@app.get("/api/patients/{patient_id}/pdf")
async def generate_patient_pdf(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(db_config.Patient).filter(db_config.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Ensure reports dir exists
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/ficha_{patient.dni}.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "FICHA TÉCNICA DEL PACIENTE - SISSOT")
    c.setFont("Helvetica", 12)
    c.line(100, 740, 500, 740)
    
    y = 710
    c.drawString(100, y, f"Nombre: {patient.first_name} {patient.last_name}")
    y -= 20
    c.drawString(100, y, f"Cédula: {patient.dni}")
    y -= 20
    c.drawString(100, y, f"Dirección: {patient.address}")
    y -= 20
    c.drawString(100, y, f"Comuna: {patient.commune.name if patient.commune else 'N/A'}")
    
    # Clinical history snippet
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "HISTORIAL CLÍNICO RECIENTE")
    y -= 20
    c.line(100, y+10, 500, y+10)
    
    c.setFont("Helvetica", 10)
    for record in patient.records[-3:]: # Last 3 records
        c.drawString(100, y, f"Fecha: {record.last_visit.strftime('%Y-%m-%d')} - Patología: {record.primary_pathology}")
        y -= 15
        c.drawString(120, y, f"Riesgo: {record.risk_level} - CIE-10: {record.cie10_code}")
        y -= 20
        
    c.save()
    return FileResponse(filename, media_type="application/pdf", filename=f"ficha_{patient.dni}.pdf")

@app.post("/api/clinical_records")
async def create_record(record_data: dict, db: Session = Depends(get_db)):
    new_record = db_config.ClinicalRecord(
        patient_id=record_data.get("patient_id"),
        primary_pathology=record_data.get("primary_pathology"),
        secondary_pathologies=record_data.get("secondary_pathologies"),
        cie10_code=record_data.get("cie10_code"),
        risk_level=record_data.get("risk_level"),
        evolutionary_state=record_data.get("evolutionary_state"),
        priority=record_data.get("priority"),
        medications=record_data.get("medications"),
        observations=record_data.get("observations"),
        assigned_doctor_id=record_data.get("assigned_doctor_id")
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    # SURVEILLANCE LOGIC: Check for outbreaks
    check_for_outbreaks(new_record, db)
    
    return new_record

def check_for_outbreaks(record, db):
    # Threshold: more than 3 cases of same pathology in same commune in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    commune_id = db.query(db_config.Patient.commune_id).filter(db_config.Patient.id == record.patient_id).scalar()
    
    case_count = db.query(db_config.ClinicalRecord).join(db_config.Patient).filter(
        db_config.Patient.commune_id == commune_id,
        db_config.ClinicalRecord.primary_pathology == record.primary_pathology,
        db_config.ClinicalRecord.last_visit >= seven_days_ago
    ).count()
    
    if case_count >= 3:
        commune_name = db.query(db_config.Commune.name).filter(db_config.Commune.id == commune_id).scalar()
        alert = db_config.Alert(
            type="Brote Epidemiológico",
            level="Alto",
            description=f"Se han detectado {case_count} casos de {record.primary_pathology} en la comuna {commune_name} en los últimos 7 días.",
            commune_id=commune_id
        )
        db.add(alert)
        db.commit()

@app.get("/api/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    return db.query(db_config.Alert).order_by(db_config.Alert.created_at.desc()).all()

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
