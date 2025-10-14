from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_api.extensions import db
from flask_api.models import Ticket, TicketStatus, User, Organization, Thread, FormEntry
from flask_api.utils import get_paginated_response

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets', methods=['GET'])
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
      - name: status_name
        in: query
        type: string
        description: Filter by status name.
      - name: organization_name
        in: query
        type: string
        description: Filter by organization name.
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
    if 'status_name' in request.args:
        query = query.join(TicketStatus, Ticket.status_id == TicketStatus.id).filter(TicketStatus.name == request.args.get('status_name'))
    if 'organization_name' in request.args:
        query = query.join(User).join(Organization).filter(Organization.name == request.args.get('organization_name'))
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

    return jsonify(get_paginated_response(pagination, 'tickets.get_tickets', **request.args))

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
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