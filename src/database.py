from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import unique
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

   
    #Returns a string as a representation of the object. 
    def __repr__(self) -> str:
        return 'User>>> {self.email}'