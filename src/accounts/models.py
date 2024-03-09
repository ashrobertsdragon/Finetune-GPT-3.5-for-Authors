from datetime import datetime
from uuid import uuid4

from src.extensions import bcrypt, db
from utils import random_str


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.UUID(as_uuid=True), default=uuid4, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    credits_available = db.Column(db.Integer, nullable=False, default=0)
    credits_used = db.Column(db.Integer, nullable=False, default=0)
    user_folder = db.Column(db.String, nullable=False, unique=True, default=random_str)

    def random_folder(self):
        while True:
          folder = random_str()
          if User.query.filter_by(folder).first():
                continue
        self.user_folder = folder

    def __init__(self, email, password, is_admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.is_admin = is_admin
        self.random_folder()


    def __repr__(self):
        return f"<email {self.email}>"
