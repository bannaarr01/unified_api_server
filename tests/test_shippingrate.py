import unittest
from src import create_app
from src.config.config import config_dict
from src.database import db
from werkzeug.security import generate_password_hash
from faker import Faker
from flask_jwt_extended import JWTManager, create_access_token
from flask import url_for, request


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config=config_dict['testing'])
        self.appctx=self.app.app_context()
        self.appctx.push()
        self.client=self.app.test_client()
        self.shipping_rate_url = '/api/v1/shippingrate'
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


    def test_unathorize_user_cannot_get_shippingrate(self):
        with self.client:
            data={
                "destination_postcode": "63000", 
                "height": "5", 
                "length": "9", 
                "origin_postcode": 
                "71800", "weight": "45", 
                "width": "7" }
            token=create_access_token('testuser')
            response=self.client.post(self.shipping_rate_url, json=data, follow_redirects=True)
            self.assertEqual(response.status_code, 401) 
            #should pass,unauth

    def test_wrong_data_cannot_get_shippingrate(self):
        with self.client:
            token=create_access_token('testuser')
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
            data={
                "destination_postcode": "600", 
                "height": "5", 
                "length": "", 
                "origin_postcode":"70",
                "weight": "45", 
                "width": "7" }
            response=self.client.post(self.shipping_rate_url, headers=headers, json=data, follow_redirects=True)
            self.assertEqual(response.status_code, 422) 
            #should pass


    def test_can_get_shippingrate(self):
        with self.client:
            token=create_access_token('testuser')
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
            data={
                "destination_postcode": "63000", 
                "height": "5", 
                "length": "9", 
                "origin_postcode":"71800",
                "weight": "45", 
                "width": "7" }
            response=self.client.post(self.shipping_rate_url, headers=headers, json=data, follow_redirects=True)
            # import pdb; pdb.set_trace() #use response.data for debug
            self.assertEqual(response.status_code, 200) 
            #should pass by fectching all shipping rates successfully✅


