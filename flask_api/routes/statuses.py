from flask import Blueprint, jsonify, request
from flask_api.extensions import db
from flask_api.models import TicketStatus
from flask_api.utils import get_paginated_response

statuses_bp = Blueprint('statuses', __name__)

@statuses_bp.route('/statuses', methods=['GET'])
def get_statuses():
    """
    Get a paginated, sorted, and filtered list of ticket statuses.
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
        description: The number of statuses to retrieve per page.
      - name: sort_by
        in: query
        type: string
        default: name
        description: The field to sort by (e.g., 'name', 'state').
      - name: sort_order
        in: query
        type: string
        default: asc
        enum: ['asc', 'desc']
        description: The sort order ('asc' or 'desc').
      - name: name
        in: query
        type: string
        description: Filter by status name.
      - name: state
        in: query
        type: string
        description: Filter by status state.
    responses:
      200:
        description: A paginated list of ticket statuses.
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
                $ref: '#/definitions/TicketStatus'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    query = TicketStatus.query

    # Filtering
    if 'name' in request.args:
        query = query.filter(TicketStatus.name.ilike(f"%{request.args.get('name')}%"))
    if 'state' in request.args:
        query = query.filter_by(state=request.args.get('state'))

    # Sorting
    if hasattr(TicketStatus, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(TicketStatus, sort_by).desc())
        else:
            query = query.order_by(getattr(TicketStatus, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(get_paginated_response(pagination, 'statuses.get_statuses', **request.args))