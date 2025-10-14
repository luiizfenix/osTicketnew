from flask import Blueprint, jsonify, request
from flask_api.extensions import db
from flask_api.models import Department
from flask_api.utils import get_paginated_response

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/departments', methods=['GET'])
def get_departments():
    """
    Get a paginated, sorted, and filtered list of departments.
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
        description: The number of departments to retrieve per page.
      - name: sort_by
        in: query
        type: string
        default: name
        description: The field to sort by (e.g., 'name', 'ispublic').
      - name: sort_order
        in: query
        type: string
        default: asc
        enum: ['asc', 'desc']
        description: The sort order ('asc' or 'desc').
      - name: name
        in: query
        type: string
        description: Filter by department name.
      - name: ispublic
        in: query
        type: boolean
        description: Filter by whether the department is public or not.
    responses:
      200:
        description: A paginated list of departments.
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
                $ref: '#/definitions/Department'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    query = Department.query

    # Filtering
    if 'name' in request.args:
        query = query.filter(Department.name.ilike(f"%{request.args.get('name')}%"))
    if 'ispublic' in request.args:
        is_public = request.args.get('ispublic').lower() in ['true', '1']
        query = query.filter_by(ispublic=is_public)

    # Sorting
    if hasattr(Department, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Department, sort_by).desc())
        else:
            query = query.order_by(getattr(Department, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(get_paginated_response(pagination, 'departments.get_departments', **request.args))