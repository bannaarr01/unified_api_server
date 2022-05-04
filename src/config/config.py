import os

class TestConfig():
    SECRET_KEY=os.environ.get('SECRET_KEY', default=False),
    JWT_SECRET_KEY='JWT_SECRET_KEY'
    TESTING=True
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=True


config_dict={
    'testing':TestConfig
}