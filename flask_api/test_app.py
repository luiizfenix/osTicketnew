import unittest
import os

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
from app import app, db
from models import User, UserEmail, Form, FormField, FormEntry, FormEntryValue

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_app_creation(self):
        """Test that the Flask app is created successfully."""
        self.assertIsNotNone(self.app)

    def test_db_connection(self):
        """Test that the database connection is established."""
        with self.app.app_context():
            self.assertIsNotNone(db.engine)

    def test_get_user_with_email(self):
        """Test that the user's email is retrieved correctly."""
        with self.app.app_context():
            # Create a dummy user and email
            email = UserEmail(id=1, address='test@example.com')
            user = User(id=1, name='Test User', default_email_id=1, email=email)
            db.session.add(user)
            db.session.add(email)
            db.session.commit()

            # Make a request to the get_user endpoint
            response = self.client.get('/users/1')
            data = response.get_json()

            # Assert that the email is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['email'], 'test@example.com')

    def test_get_user_with_phone(self):
        """Test that the user's phone number is retrieved correctly."""
        with self.app.app_context():
            # Create a dummy user and form data
            user = User(id=1, name='Test User')
            form = Form(id=1, form_type='U')
            phone_field = FormField(id=1, form_id=1, name='phone')
            form_entry = FormEntry(id=1, form_id=1, object_id=1, object_type='U')
            phone_value = FormEntryValue(entry_id=1, field_id=1, value='123-456-7890')
            db.session.add(user)
            db.session.add(form)
            db.session.add(phone_field)
            db.session.add(form_entry)
            db.session.add(phone_value)
            db.session.commit()

            # Make a request to the get_user endpoint
            response = self.client.get('/users/1')
            data = response.get_json()

            # Assert that the phone number is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['phone'], '123-456-7890')

if __name__ == '__main__':
    unittest.main()