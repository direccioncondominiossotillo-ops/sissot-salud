from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salud_sotillo.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)
    role = Column(String)  # admin, doctor
    is_active = Column(Boolean, default=True)

class Commune(Base):
    __tablename__ = "communes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    coordinates = Column(String) # For the map: "lat,lng"

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(DateTime)
    gender = Column(String)
    address = Column(String)
    commune_id = Column(Integer, ForeignKey("communes.id"))
    phone = Column(String)
    marital_status = Column(String)
    
    commune = relationship("Commune")
    records = relationship("ClinicalRecord", back_populates="patient")

class ClinicalRecord(Base):
    __tablename__ = "clinical_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    primary_pathology = Column(String)
    secondary_pathologies = Column(Text)
    cie10_code = Column(String)
    risk_level = Column(String) # Bajo, Medio, Alto, Critico
    evolutionary_state = Column(String)
    priority = Column(String) # Normal, Urgente
    medications = Column(Text)
    observations = Column(Text)
    last_visit = Column(DateTime, default=datetime.utcnow)
    assigned_doctor_id = Column(Integer, ForeignKey("users.id"))
    
    patient = relationship("Patient", back_populates="records")
    doctor = relationship("User")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String) # Brote, Caso Critico, Medicamento Urgente
    level = Column(String) # Bajo, Medio, Alto, Critico
    description = Column(Text)
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=True)
    status = Column(String, default="active") # active, resolved
    created_at = Column(DateTime, default=datetime.utcnow)

class CIE10(Base):
    __tablename__ = "cie10"
    code = Column(String, primary_key=True, index=True)
    description = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Communes
    if db.query(Commune).count() == 0:
        communes = [
            "Puerto La Cruz", "Pozuelos", "El Maguey", "Chuparín", "Guanire",
            "Sotillo Central", "Sierra Maestra", "Valle Verde", "Los Yaques", "Molorca",
            "Aldea de Pescadores", "Oropeza Castillo", "Dany de Puerto", "Monte Cristo", "Tierra Adentro",
            "Las Delicias", "El Frío", "San Diego", "El Rincón", "Putucual", "Curataquiche"
        ]
        for name in communes:
            db.add(Commune(name=name))
        db.commit()

    # CIE-10 Basic Sample
    if db.query(CIE10).count() == 0:
        cie_codes = [
            ("A00", "Cólera"), ("A01", "Fiebre tifoidea"), ("A90", "Dengue"),
            ("E10", "Diabetes mellitus"), ("I10", "Hipertensión esencial"),
            ("J00", "Rinofaringitis aguda"), ("J10", "Influenza")
        ]
        for code, desc in cie_codes:
            db.add(CIE10(code=code, description=desc))
        db.commit()

    # Default Admin
    if db.query(User).count() == 0:
        admin_user = User(
            username="admin",
            full_name="Administrador Sotillo",
            password_hash=pwd_context.hash("admin123"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        
    db.close()
