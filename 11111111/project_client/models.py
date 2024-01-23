from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from create_app import app
from datetime import datetime

engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    purchases = relationship('UserPurchase', back_populates='user')
    subscription = relationship('Subscription', back_populates='user')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return session.query(User).get(user_id)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class UserMessage(Base):
    __tablename__ = 'user_messages'

    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, message):
        self.message = message


class UserPurchase(Base):
    __tablename__ = 'user_purchases'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship('User', back_populates='purchases')

    def __init__(self, user_id):
        self.user_id = user_id


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship('User', back_populates='subscription')

    def __init__(self, user_id, status):
        self.user_id = user_id
        self.status = status


Base.metadata.create_all(engine)
