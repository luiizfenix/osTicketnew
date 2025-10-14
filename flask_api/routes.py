from flask import jsonify, request
from app import app, db
from models import User, Organization, Ticket, Thread, FormEntry, FormEntryValue, FAQ, Department, HelpTopic

@app.route('/tickets', methods=['GET'])
def get_tickets():
    """
    Get a list of all tickets.
    ---
    responses:
      200:
        description: A list of tickets.
        schema:
          type: array
          items:
            $ref: '#/definitions/Ticket'
    """
    tickets = Ticket.query.all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """
    Get a single ticket by its ID.
    ---
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        description: The ID of the ticket to retrieve.
    responses:
      200:
        description: The ticket details.
        schema:
          $ref: '#/definitions/Ticket'
      404:
        description: Ticket not found.
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket_data = ticket.to_dict()

    # Get thread and entries
    thread = Thread.query.filter_by(object_id=ticket.ticket_id, object_type='T').first()
    if thread:
        ticket_data['thread'] = thread.to_dict()

    # Get custom form data
    form_entry = FormEntry.query.filter_by(object_id=ticket.ticket_id, object_type='T').first()
    if form_entry:
        ticket_data['custom_data'] = form_entry.to_dict()

    return jsonify(ticket_data)

@app.route('/users', methods=['GET'])
def get_users():
    """
    Get a list of all users.
    ---
    responses:
      200:
        description: A list of users.
        schema:
          type: array
          items:
            $ref: '#/definitions/User'
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a single user by their ID.
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The ID of the user to retrieve.
    responses:
      200:
        description: The user details.
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found.
    """
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/organizations', methods=['GET'])
def get_organizations():
    """
    Get a list of all organizations.
    ---
    responses:
      200:
        description: A list of organizations.
        schema:
          type: array
          items:
            $ref: '#/definitions/Organization'
    """
    organizations = Organization.query.all()
    return jsonify([organization.to_dict() for organization in organizations])

@app.route('/organizations/<int:org_id>', methods=['GET'])
def get_organization(org_id):
    """
    Get a single organization by its ID.
    ---
    parameters:
      - name: org_id
        in: path
        type: integer
        required: true
        description: The ID of the organization to retrieve.
    responses:
      200:
        description: The organization details.
        schema:
          $ref: '#/definitions/Organization'
      404:
        description: Organization not found.
    """
    organization = Organization.query.get_or_404(org_id)
    return jsonify(organization.to_dict())

@app.route('/kb/faqs', methods=['GET'])
def get_faqs():
    """
    Get a list of all FAQs.
    ---
    responses:
      200:
        description: A list of FAQs.
    """
    faqs = FAQ.query.filter_by(ispublished=True).all()
    return jsonify([faq.to_dict() for faq in faqs])

@app.route('/departments', methods=['GET'])
def get_departments():
    """
    Get a list of all departments.
    ---
    responses:
      200:
        description: A list of departments.
    """
    departments = Department.query.filter_by(ispublic=True).all()
    return jsonify([department.to_dict() for department in departments])

@app.route('/helptopics', methods=['GET'])
def get_helptopics():
    """
    Get a list of all help topics.
    ---
    responses:
      200:
        description: A list of help topics.
    """
    helptopics = HelpTopic.query.filter_by(ispublic=True).all()
    return jsonify([helptopic.to_dict() for helptopic in helptopics])