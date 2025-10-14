import unittest
import os
from datetime import datetime, timedelta

os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
from flask_api.app import app, db
from flask_api.models import User, UserEmail, Form, FormField, FormEntry, FormEntryValue, Ticket, TicketStatus, Queue, Department, HelpTopic, Organization

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
            self.assertEqual(data['next_page'], '/tickets?page=3&per_page=5')
            self.assertEqual(data['prev_page'], '/tickets?page=1&per_page=5')

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

    def test_get_tickets_filtering_by_number(self):
        """Test that the tickets are filtered correctly by number."""
        with self.app.app_context():
            # Create dummy tickets with different numbers
            ticket1 = Ticket(ticket_id=1, number='12345')
            ticket2 = Ticket(ticket_id=2, number='67890')
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with filtering by number
            response = self.client.get('/tickets?number=12345')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '12345')

    def test_get_tickets_filtering_by_topic_and_team(self):
        """Test that the tickets are filtered correctly by topic and team."""
        with self.app.app_context():
            # Create dummy tickets with different topics and teams
            ticket1 = Ticket(ticket_id=1, number='1', topic_id=1, team_id=1)
            ticket2 = Ticket(ticket_id=2, number='2', topic_id=2, team_id=2)
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with filtering by topic and team
            response = self.client.get('/tickets?topic_id=1&team_id=1')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '1')

    def test_get_tickets_filtering_by_date_range(self):
        """Test that the tickets are filtered correctly by date range."""
        with self.app.app_context():
            # Create dummy tickets with different creation dates
            ticket1 = Ticket(ticket_id=1, number='1', created=datetime.now() - timedelta(days=2))
            ticket2 = Ticket(ticket_id=2, number='2', created=datetime.now())
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with date range filtering
            response = self.client.get(f'/tickets?created_after={(datetime.now() - timedelta(days=1)).isoformat()}')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '2')

    def test_get_tickets_filtering_by_is_closed(self):
        """Test that the tickets are filtered correctly by is_closed."""
        with self.app.app_context():
            # Create dummy tickets with different closed statuses
            ticket1 = Ticket(ticket_id=1, number='1', closed=datetime.now())
            ticket2 = Ticket(ticket_id=2, number='2', closed=None)
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with is_closed filtering
            response = self.client.get('/tickets?is_closed=true')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '1')

    def test_get_statuses(self):
        """Test the /statuses endpoint."""
        with self.app.app_context():
            # Create dummy statuses
            status1 = TicketStatus(id=1, name='Open', state='open')
            status2 = TicketStatus(id=2, name='Closed', state='closed')
            db.session.add(status1)
            db.session.add(status2)
            db.session.commit()

            # Test pagination
            response = self.client.get('/statuses?page=1&per_page=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)

            # Test sorting
            response = self.client.get('/statuses?sort_by=name&sort_order=desc')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['name'], 'Open')
            self.assertEqual(data['results'][1]['name'], 'Closed')

            # Test filtering
            response = self.client.get('/statuses?name=Closed')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'Closed')

    def test_get_queues(self):
        """Test the /queues endpoint."""
        with self.app.app_context():
            # Create dummy queues
            queue1 = Queue(id=1, title='Queue 1', staff_id=1)
            queue2 = Queue(id=2, title='Queue 2', staff_id=2)
            db.session.add(queue1)
            db.session.add(queue2)
            db.session.commit()

            # Test pagination
            response = self.client.get('/queues?page=1&per_page=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)

            # Test sorting
            response = self.client.get('/queues?sort_by=title&sort_order=desc')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['title'], 'Queue 2')

            # Test filtering
            response = self.client.get('/queues?staff_id=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['title'], 'Queue 1')

    def test_get_tickets_filtering_by_status_name(self):
        """Test that the tickets are filtered correctly by status name."""
        with self.app.app_context():
            # Create dummy tickets and statuses
            status1 = TicketStatus(id=1, name='Open', state='open')
            status2 = TicketStatus(id=2, name='Closed', state='closed')
            ticket1 = Ticket(ticket_id=1, number='1', status_id=1)
            ticket2 = Ticket(ticket_id=2, number='2', status_id=2)
            db.session.add(status1)
            db.session.add(status2)
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with filtering by status name
            response = self.client.get('/tickets?status_name=Open')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '1')

    def test_get_tickets_filtering_by_organization_name(self):
        """Test that the tickets are filtered correctly by organization name."""
        with self.app.app_context():
            # Create dummy tickets, users, and organizations
            org1 = Organization(id=1, name='Org 1')
            org2 = Organization(id=2, name='Org 2')
            user1 = User(id=1, name='User 1', org_id=1)
            user2 = User(id=2, name='User 2', org_id=2)
            ticket1 = Ticket(ticket_id=1, number='1', user_id=1)
            ticket2 = Ticket(ticket_id=2, number='2', user_id=2)
            db.session.add(org1)
            db.session.add(org2)
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()

            # Make a request to the get_tickets endpoint with filtering by organization name
            response = self.client.get('/tickets?organization_name=Org 1')
            data = response.get_json()

            # Assert that the filtering is correct
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['number'], '1')

    def test_get_departments_enhanced(self):
        """Test the enhanced /departments endpoint."""
        with self.app.app_context():
            # Create dummy departments
            dept1 = Department(id=1, name='Dept 1', ispublic=True)
            dept2 = Department(id=2, name='Dept 2', ispublic=False)
            db.session.add(dept1)
            db.session.add(dept2)
            db.session.commit()

            # Test pagination
            response = self.client.get('/departments?page=1&per_page=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)

            # Test sorting
            response = self.client.get('/departments?sort_by=name&sort_order=desc')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['name'], 'Dept 2')

            # Test filtering
            response = self.client.get('/departments?ispublic=true')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'Dept 1')

    def test_get_helptopics_enhanced(self):
        """Test the enhanced /helptopics endpoint."""
        with self.app.app_context():
            # Create dummy help topics
            topic1 = HelpTopic(topic_id=1, topic='Topic 1', ispublic=True)
            topic2 = HelpTopic(topic_id=2, topic='Topic 2', ispublic=False)
            db.session.add(topic1)
            db.session.add(topic2)
            db.session.commit()

            # Test pagination
            response = self.client.get('/helptopics?page=1&per_page=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)

            # Test sorting
            response = self.client.get('/helptopics?sort_by=topic&sort_order=desc')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['topic'], 'Topic 2')

            # Test filtering
            response = self.client.get('/helptopics?ispublic=true')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['topic'], 'Topic 1')

    def test_get_users_enhanced(self):
        """Test the enhanced /users endpoint."""
        with self.app.app_context():
            # Create dummy users
            user1 = User(id=1, name='Alice')
            user2 = User(id=2, name='Bob')
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            # Test pagination
            response = self.client.get('/users?page=1&per_page=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)

            # Test sorting
            response = self.client.get('/users?sort_by=name&sort_order=desc')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['name'], 'Bob')

            # Test filtering
            response = self.client.get('/users?name=Alice')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'Alice')

    def test_get_organizations_enhanced(self):
        """Test the enhanced /organizations endpoint."""
        with self.app.app_context():
            # Create dummy organizations
            org1 = Organization(id=1, name='Org A')
            org2 = Organization(id=2, name='Org B')
            db.session.add(org1)
            db.session.add(org2)
            db.session.commit()

            # Test pagination
            response = self.client.get('/organizations?page=1&per_page=1')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)

            # Test sorting
            response = self.client.get('/organizations?sort_by=name&sort_order=desc')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['results'][0]['name'], 'Org B')

            # Test filtering
            response = self.client.get('/organizations?name=Org A')
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'Org A')

if __name__ == '__main__':
    unittest.main()