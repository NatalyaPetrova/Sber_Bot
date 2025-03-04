from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    skill_level = db.Column(db.String(20), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String(50), nullable=False)  # Например, "Может работать 40 часов в неделю"

    def __repr__(self):
        return f'<Employee {self.name}>'