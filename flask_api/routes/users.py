from flask import Blueprint, jsonify, request
from flask_api.extensions import db
from flask_api.models import User, UserEmail
from flask_api.utils import get_paginated_response

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get a paginated, sorted, and filtered list of users.
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
        description: The number of users to retrieve per page.
      - name: sort_by
        in: query
        type: string
        default: name
        description: The field to sort by (e.g., 'name', 'created').
      - name: sort_order
        in: query
        type: string
        default: asc
        enum: ['asc', 'desc']
        description: The sort order ('asc' or 'desc').
      - name: name
        in: query
        type: string
        description: Filter by user name.
      - name: email
        in: query
        type: string
        description: Filter by user email address.
      - name: org_id
        in: query
        type: integer
        description: Filter by organization ID.
    responses:
      200:
        description: A paginated list of users.
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
                $ref: '#/definitions/User'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    query = User.query

    # Filtering
    if 'name' in request.args:
        query = query.filter(User.name.ilike(f"%{request.args.get('name')}%"))
    if 'email' in request.args:
        query = query.join(UserEmail).filter(UserEmail.address.ilike(f"%{request.args.get('email')}%"))
    if 'org_id' in request.args:
        query = query.filter_by(org_id=request.args.get('org_id', type=int))

    # Sorting
    if hasattr(User, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(User, sort_by).desc())
        else:
            query = query.order_by(getattr(User, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(get_paginated_response(pagination, 'users.get_users', **request.args))

@users_bp.route('/users/<int:user_id>', methods=['GET'])
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