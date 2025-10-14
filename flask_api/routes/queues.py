from flask import Blueprint, jsonify, request
from flask_api.extensions import db
from flask_api.models import Queue
from flask_api.utils import get_paginated_response

queues_bp = Blueprint('queues', __name__)

@queues_bp.route('/queues', methods=['GET'])
def get_queues():
    """
    Get a paginated, sorted, and filtered list of queues.
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
        description: The number of queues to retrieve per page.
      - name: sort_by
        in: query
        type: string
        default: title
        description: The field to sort by (e.g., 'title', 'sort').
      - name: sort_order
        in: query
        type: string
        default: asc
        enum: ['asc', 'desc']
        description: The sort order ('asc' or 'desc').
      - name: title
        in: query
        type: string
        description: Filter by queue title.
      - name: staff_id
        in: query
        type: integer
        description: Filter by staff ID.
    responses:
      200:
        description: A paginated list of queues.
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
                $ref: '#/definitions/Queue'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'title')
    sort_order = request.args.get('sort_order', 'asc')

    query = Queue.query

    # Filtering
    if 'title' in request.args:
        query = query.filter(Queue.title.ilike(f"%{request.args.get('title')}%"))
    if 'staff_id' in request.args:
        query = query.filter_by(staff_id=request.args.get('staff_id', type=int))

    # Sorting
    if hasattr(Queue, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Queue, sort_by).desc())
        else:
            query = query.order_by(getattr(Queue, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(get_paginated_response(pagination, 'queues.get_queues', **request.args))