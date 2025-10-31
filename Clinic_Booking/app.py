from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, User, Doctor, Patient, Appointment, Notification
from forms import RegisterForm, LoginForm, DoctorProfileForm, BookForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists", "danger")
            return redirect(url_for("register"))
        u = User(email=form.email.data, role=form.role.data, name=form.name.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        # create profile record
        if u.role == "doctor":
            doc = Doctor(user_id=u.id)
            db.session.add(doc)
        else:
            pat = Patient(user_id=u.id)
            db.session.add(pat)
        db.session.commit()
        flash("Registered. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "doctor":
        doctor = current_user.doctor_profile
        # upcoming appointments
        appts = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date_time).all()
        notes = Notification.query.filter_by(doctor_id=doctor.id).order_by(Notification.created_at.desc()).limit(10).all()
        return render_template("dashboard.html", user=current_user, appointments=appts, notifications=notes)
    elif current_user.role == "patient":
        patient = current_user.patient_profile
        appts = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date_time).all()
        notes = Notification.query.filter_by(patient_id=patient.id).order_by(Notification.created_at.desc()).limit(10).all()
        return render_template("dashboard.html", user=current_user, appointments=appts, notifications=notes)
    else:
        # admin
        total_appts = Appointment.query.count()
        doctors = Doctor.query.count()
        patients = Patient.query.count()
        return render_template("admin_dashboard.html", total_appts=total_appts, doctors=doctors, patients=patients)

@app.route("/doctor/profile", methods=["GET","POST"])
@login_required
def doctor_profile():
    if current_user.role != "doctor":
        flash("Only doctors can access that page", "warning")
        return redirect(url_for("dashboard"))
    form = DoctorProfileForm()
    doc = current_user.doctor_profile
    if form.validate_on_submit():
        doc.telephone = form.telephone.data
        doc.specialization = form.specialization.data
        doc.availability = form.availability.data
        db.session.commit()
        flash("Profile saved", "success")
        return redirect(url_for("dashboard"))
    # populate
    form.telephone.data = doc.telephone
    form.specialization.data = doc.specialization
    form.availability.data = doc.availability
    return render_template("doctor_profile.html", form=form)

@app.route("/book", methods=["GET","POST"])
@login_required
def book():
    if current_user.role != "patient":
        flash("Only patients can book", "warning")
        return redirect(url_for("dashboard"))
    form = BookForm()
    doctors = Doctor.query.join(User).all()
    form.doctor_id.choices = [(d.id, f"{d.user.name} - {d.specialization or 'General'}") for d in doctors]
    if form.validate_on_submit():
        appt = Appointment(
            date_time=form.date_time.data,
            doctor_id=form.doctor_id.data,
            patient_id=current_user.patient_profile.id,
            notes=form.notes.data,
            status="pending"
        )
        db.session.add(appt)
        db.session.commit()
        # create notification for doctor
        note = Notification(
            message=f"New booking by {current_user.name} for {form.date_time.data.strftime('%Y-%m-%d %H:%M')}",
            doctor_id=form.doctor_id.data,
            patient_id=current_user.patient_profile.id,
            appointment_id=appt.id
        )
        db.session.add(note)
        db.session.commit()
        flash("Appointment requested. Wait for approval.", "success")
        return redirect(url_for("dashboard"))
    return render_template("book.html", form=form)

@app.route("/appointments")
@login_required
def appointments():
    if current_user.role == "doctor":
        appts = Appointment.query.filter_by(doctor_id=current_user.doctor_profile.id).order_by(Appointment.date_time).all()
    elif current_user.role == "patient":
        appts = Appointment.query.filter_by(patient_id=current_user.patient_profile.id).order_by(Appointment.date_time).all()
    else:
        appts = Appointment.query.order_by(Appointment.date_time).all()
    return render_template("appointments.html", appointments=appts)

@app.route("/appointment/<int:appt_id>/action", methods=["POST"])
@login_required
def appointment_action(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if current_user.role not in ("doctor","admin"):
        flash("Not allowed", "danger")
        return redirect(url_for("dashboard"))
    # doctor can approve/reject for their appointments
    action = request.form.get("action")
    if current_user.role == "doctor" and appt.doctor.user_id != current_user.id:
        flash("Not allowed", "danger")
        return redirect(url_for("dashboard"))
    if action == "approve":
        appt.status = "approved"
        db.session.commit()
        note = Notification(message=f"Your appointment on {appt.date_time.strftime('%Y-%m-%d %H:%M')} was approved", patient_id=appt.patient_id, appointment_id=appt.id)
        db.session.add(note)
        db.session.commit()
        flash("Appointment approved", "success")
    elif action == "reject":
        appt.status = "rejected"
        db.session.commit()
        note = Notification(message=f"Your appointment on {appt.date_time.strftime('%Y-%m-%d %H:%M')} was rejected", patient_id=appt.patient_id, appointment_id=appt.id)
        db.session.add(note)
        db.session.commit()
        flash("Appointment rejected", "info")
    return redirect(url_for("appointments"))

# Simple notifications view
@app.route("/notifications")
@login_required
def notifications():
    if current_user.role == "doctor":
        notes = Notification.query.filter_by(doctor_id=current_user.doctor_profile.id).order_by(Notification.created_at.desc()).all()
    elif current_user.role == "patient":
        notes = Notification.query.filter_by(patient_id=current_user.patient_profile.id).order_by(Notification.created_at.desc()).all()
    else:
        notes = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", notifications=notes)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
