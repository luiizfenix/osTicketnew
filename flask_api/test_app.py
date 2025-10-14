import unittest
import os

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
from app import app, db

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

if __name__ == '__main__':
    unittest.main()