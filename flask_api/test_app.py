import unittest
import os

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
from app import app, db
from models import User, UserEmail, Form, FormField, FormEntry, FormEntryValue, Ticket

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

    def test_get_tickets_pagination(self):
        """Test that the tickets are paginated correctly."""
        with self.app.app_context():
            # Create 15 dummy tickets
            for i in range(15):
                ticket = Ticket(ticket_id=i+1, number=str(i+1))
                db.session.add(ticket)
            db.session.commit()

            # Make a request to the get_tickets endpoint with pagination
            response = self.client.get('/tickets?page=2&per_page=5')
            data = response.get_json()

            # Assert that the pagination is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 5)
            self.assertEqual(data['total'], 15)
            self.assertEqual(data['pages'], 3)
            self.assertEqual(data['next_page'], 3)
            self.assertEqual(data['prev_page'], 1)

    def test_get_tickets_sorting(self):
        """Test that the tickets are sorted correctly."""
        with self.app.app_context():
            # Create dummy tickets with different creation dates
            ticket1 = Ticket(ticket_id=1, number='1', created=db.func.now())
            ticket2 = Ticket(ticket_id=2, number='2', created=db.func.now())
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with sorting
            response = self.client.get('/tickets?sort_by=created&sort_order=asc')
            data = response.get_json()

            # Assert that the sorting is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['number'], '1')
            self.assertEqual(data['results'][1]['number'], '2')

    def test_get_tickets_filtering(self):
        """Test that the tickets are filtered correctly."""
        with self.app.app_context():
            # Create dummy tickets with different statuses
            ticket1 = Ticket(ticket_id=1, number='1', status_id=1)
            ticket2 = Ticket(ticket_id=2, number='2', status_id=2)
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with filtering
            response = self.client.get('/tickets?status_id=1')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '1')

if __name__ == '__main__':
    unittest.main()