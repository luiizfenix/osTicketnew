from flask import Blueprint, jsonify, request
from flask_api.extensions import db
from flask_api.models import Organization
from flask_api.utils import get_paginated_response

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/organizations', methods=['GET'])
def get_organizations():
    """
    Get a paginated, sorted, and filtered list of organizations.
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
        description: The number of organizations to retrieve per page.
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
        description: Filter by organization name.
    responses:
      200:
        description: A paginated list of organizations.
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
                $ref: '#/definitions/Organization'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    query = Organization.query

    # Filtering
    if 'name' in request.args:
        query = query.filter(Organization.name.ilike(f"%{request.args.get('name')}%"))

    # Sorting
    if hasattr(Organization, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Organization, sort_by).desc())
        else:
            query = query.order_by(getattr(Organization, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(get_paginated_response(pagination, 'organizations.get_organizations', **request.args))

@organizations_bp.route('/organizations/<int:org_id>', methods=['GET'])
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