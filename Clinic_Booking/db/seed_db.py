from app import app
from models import db, User, Doctor, Patient
with app.app_context():
    db.drop_all()
    db.create_all()
    # admin
    admin = User(email="admin@clinic.local", role="admin", name="Admin")
    admin.set_password("adminpass")
    db.session.add(admin)
    # doctor 1
    duser = User(email="dr1@clinic.local", role="doctor", name="Dr. John")
    duser.set_password("password")
    db.session.add(duser)
    db.session.commit()
    doc = Doctor(user_id=duser.id, telephone="078000001", specialization="General", availability="Mon 09-12; Tue 14-17")
    db.session.add(doc)
    # patient 1
    puser = User(email="patient1@clinic.local", role="patient", name="Alice")
    puser.set_password("password")
    db.session.add(puser)
    db.session.commit()
    pat = Patient(user_id=puser.id, telephone="078000002")
    db.session.add(pat)
    db.session.commit()
    print("Seeded DB with admin, one doctor, one patient")
