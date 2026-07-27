from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company = db.Column(db.String(150))

    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))

    segment = db.Column(db.String(50))

    status = db.Column(db.String(50))

    last_contact = db.Column(db.String(50))

    notes = db.Column(db.Text)


class Outreach(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )

    customer = db.relationship("Customer", backref="outreach")

    channel = db.Column(db.String(20))
    message = db.Column(db.Text)
    status = db.Column(db.String(30))
    follow_up = db.Column(db.String(30))
    response = db.Column(db.String(100))