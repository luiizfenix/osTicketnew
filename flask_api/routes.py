from flask import jsonify, request
from datetime import datetime
from app import app, db
from models import User, UserEmail, Organization, Ticket, Thread, FormEntry, FormEntryValue, FAQ, Department, HelpTopic

@app.route('/tickets', methods=['GET'])
def get_tickets():
    """
    Get a paginated, sorted, and filtered list of tickets.
    ---
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: The page number to retrieve.
      - name: per_page
        in: query
        type: integer
        default: 10
        description: The number of tickets to retrieve per page.
      - name: sort_by
        in: query
        type: string
        default: created
        description: The field to sort by (e.g., 'created', 'updated', 'status_id').
      - name: sort_order
        in: query
        type: string
        default: desc
        enum: ['asc', 'desc']
        description: The sort order ('asc' or 'desc').
      - name: number
        in: query
        type: string
        description: Filter by ticket number.
      - name: status_id
        in: query
        type: integer
        description: Filter by status ID.
      - name: dept_id
        in: query
        type: integer
        description: Filter by department ID.
      - name: topic_id
        in: query
        type: integer
        description: Filter by topic ID.
      - name: team_id
        in: query
        type: integer
        description: Filter by team ID.
      - name: user_id
        in: query
        type: integer
        description: Filter by user ID.
      - name: staff_id
        in: query
        type: integer
        description: Filter by staff ID.
      - name: created_after
        in: query
        type: string
        format: date-time
        description: Filter by tickets created after a certain date (ISO 8601 format).
      - name: created_before
        in: query
        type: string
        format: date-time
        description: Filter by tickets created before a certain date (ISO 8601 format).
      - name: updated_after
        in: query
        type: string
        format: date-time
        description: Filter by tickets updated after a certain date (ISO 8601 format).
      - name: updated_before
        in: query
        type: string
        format: date-time
        description: Filter by tickets updated before a certain date (ISO 8601 format).
      - name: closed_after
        in: query
        type: string
        format: date-time
        description: Filter by tickets closed after a certain date (ISO 8601 format).
      - name: closed_before
        in: query
        type: string
        format: date-time
        description: Filter by tickets closed before a certain date (ISO 8601 format).
      - name: is_closed
        in: query
        type: boolean
        description: Filter by whether the ticket is closed or not.
    responses:
      200:
        description: A paginated list of tickets.
        schema:
          type: object
          properties:
            total:
              type: integer
            pages:
              type: integer
            next_page:
              type: string
            prev_page:
              type: string
            results:
              type: array
              items:
                $ref: '#/definitions/Ticket'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created')
    sort_order = request.args.get('sort_order', 'desc')

    query = Ticket.query

    # Filtering
    if 'number' in request.args:
        query = query.filter_by(number=request.args.get('number'))
    if 'status_id' in request.args:
        query = query.filter_by(status_id=request.args.get('status_id', type=int))
    if 'dept_id' in request.args:
        query = query.filter_by(dept_id=request.args.get('dept_id', type=int))
    if 'topic_id' in request.args:
        query = query.filter_by(topic_id=request.args.get('topic_id', type=int))
    if 'team_id' in request.args:
        query = query.filter_by(team_id=request.args.get('team_id', type=int))
    if 'user_id' in request.args:
        query = query.filter_by(user_id=request.args.get('user_id', type=int))
    if 'staff_id' in request.args:
        query = query.filter_by(staff_id=request.args.get('staff_id', type=int))
    if 'created_after' in request.args:
        query = query.filter(Ticket.created >= datetime.fromisoformat(request.args.get('created_after')))
    if 'created_before' in request.args:
        query = query.filter(Ticket.created <= datetime.fromisoformat(request.args.get('created_before')))
    if 'updated_after' in request.args:
        query = query.filter(Ticket.updated >= datetime.fromisoformat(request.args.get('updated_after')))
    if 'updated_before' in request.args:
        query = query.filter(Ticket.updated <= datetime.fromisoformat(request.args.get('updated_before')))
    if 'closed_after' in request.args:
        query = query.filter(Ticket.closed >= datetime.fromisoformat(request.args.get('closed_after')))
    if 'closed_before' in request.args:
        query = query.filter(Ticket.closed <= datetime.fromisoformat(request.args.get('closed_before')))
    if 'is_closed' in request.args:
        is_closed = request.args.get('is_closed').lower() in ['true', '1']
        if is_closed:
            query = query.filter(Ticket.closed.isnot(None))
        else:
            query = query.filter(Ticket.closed.is_(None))

    # Sorting
    if hasattr(Ticket, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Ticket, sort_by).desc())
        else:
            query = query.order_by(getattr(Ticket, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    tickets = pagination.items

    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'next_page': pagination.next_num,
        'prev_page': pagination.prev_num,
        'results': [ticket.to_dict() for ticket in tickets]
    })

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