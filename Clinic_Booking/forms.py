from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    role = SelectField("I am a", choices=[("patient","Patient"),("doctor","Doctor")], validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class DoctorProfileForm(FlaskForm):
    telephone = StringField("Telephone")
    specialization = StringField("Specialization")
    availability = StringField("Availability (e.g. Mon 09-12;Tue 13-17)")
    submit = SubmitField("Save")

class BookForm(FlaskForm):
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    date_time = DateTimeField("Appointment Date & Time (YYYY-mm-dd HH:MM)", format="%Y-%m-%d %H:%M", validators=[DataRequired()])
    notes = TextAreaField("Notes")
    submit = SubmitField("Book")
