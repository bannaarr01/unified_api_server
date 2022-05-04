import unittest
from src import create_app
from src.config.config import config_dict
from src.database import db
from src.database import User
from werkzeug.security import generate_password_hash
from faker import Faker
import json
from flask_jwt_extended import JWTManager, create_access_token

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config=config_dict['testing'])
        self.appctx=self.app.app_context()
        self.appctx.push()
        self.client=self.app.test_client()
        self.register_url = '/api/v1/auth/signup'
        self.login_url = '/api/v1/auth/login'
        self.fake=Faker()
        JWTManager(self.app)
        self.user_data = {
            'email': self.fake.email(),
            'password': self.fake.email().split('@')[0]
        }
        db.create_all()
        

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app=None
        self.client=None


    def test_user_cannot_signup_with_no_data(self):
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400) #should pass
        

    def test_user_can_signup_correctly(self):
        res = self.client.post(self.register_url, json=self.user_data)
        result = json.loads(res.data)
        self.assertEqual(result["user"]["email"], self.user_data["email"])
        self.assertEqual(res.status_code, 201) #should pass
        #res.data


    def test_user_cannot_login_with_incorrect_data(self):
        res = self.client.post(self.login_url, json=self.user_data)
        self.assertEqual(res.status_code, 400) #should pass
        

    def test_user_can_login_correctly(self):
        user_data={
            "email":"testinguser1@gmail.com",
            "password":"AwesomeFlask"
        }
        self.client.post(self.register_url, json=user_data)
        res=self.client.post(self.login_url, json=user_data)
        user=User.query.filter_by(email=user_data['email']).first()
        create_access_token(identity=user.id)
        self.assertEqual(res.status_code, 200) #should pass


   