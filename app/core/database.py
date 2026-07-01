from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

DATABASE_URL = "sqlite:///data/medical.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Patient(Base):
    """患者基本信息表"""
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)       # 男/女
    age = Column(Integer, nullable=False)
    phone = Column(String)
    blood_type = Column(String)                    # A/B/AB/O

    diagnoses = relationship("Diagnosis", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    lab_results = relationship("LabResult", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


class Diagnosis(Base):
    """诊断记录表"""
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    disease = Column(String, nullable=False)       # 疾病名称
    icd_code = Column(String)                      # ICD编码
    severity = Column(String, nullable=False)      # 轻度/中度/重度
    doctor = Column(String, nullable=False)
    diagnosed_at = Column(DateTime, nullable=False,
                          default=datetime.datetime.utcnow)
    notes = Column(Text)

    patient = relationship("Patient", back_populates="diagnoses")


class Prescription(Base):
    """处方记录表"""
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    drug_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)        # 如 10mg
    frequency = Column(String, nullable=False)     # 如 每日两次
    duration_days = Column(Integer, nullable=False)
    doctor = Column(String, nullable=False)
    prescribed_at = Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="prescriptions")


class LabResult(Base):
    """检验结果表"""
    __tablename__ = "lab_results"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    test_name = Column(String, nullable=False)     # 检验项目
    value = Column(Float, nullable=False)          # 检验值
    unit = Column(String, nullable=False)          # 单位
    reference_range = Column(String, nullable=False)  # 参考范围
    is_abnormal = Column(Integer, nullable=False, default=0)  # 0正常/1异常
    tested_at = Column(DateTime, nullable=False,
                       default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="lab_results")


class Appointment(Base):
    """就诊预约表"""
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor = Column(String, nullable=False)
    department = Column(String, nullable=False)    # 科室
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False,
                    default="pending")  # pending/completed/cancelled

    patient = relationship("Patient", back_populates="appointments")


def init_db():
    Base.metadata.create_all(bind=engine)
    print("数据库表结构已创建(5张表:patients/diagnoses/prescriptions/lab_results/appointments)")


if __name__ == "__main__":
    init_db()