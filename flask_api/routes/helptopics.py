from flask import Blueprint, jsonify, request
from flask_api.extensions import db
from flask_api.models import HelpTopic
from flask_api.utils import get_paginated_response

helptopics_bp = Blueprint('helptopics', __name__)

@helptopics_bp.route('/helptopics', methods=['GET'])
def get_helptopics():
    """
    Get a paginated, sorted, and filtered list of help topics.
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
        description: The number of help topics to retrieve per page.
      - name: sort_by
        in: query
        type: string
        default: topic
        description: The field to sort by (e.g., 'topic', 'ispublic').
      - name: sort_order
        in: query
        type: string
        default: asc
        enum: ['asc', 'desc']
        description: The sort order ('asc' or 'desc').
      - name: topic
        in: query
        type: string
        description: Filter by help topic name.
      - name: ispublic
        in: query
        type: boolean
        description: Filter by whether the help topic is public or not.
    responses:
      200:
        description: A paginated list of help topics.
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
                $ref: '#/definitions/HelpTopic'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'topic')
    sort_order = request.args.get('sort_order', 'asc')

    query = HelpTopic.query

    # Filtering
    if 'topic' in request.args:
        query = query.filter(HelpTopic.topic.ilike(f"%{request.args.get('topic')}%"))
    if 'ispublic' in request.args:
        is_public = request.args.get('ispublic').lower() in ['true', '1']
        query = query.filter_by(ispublic=is_public)

    # Sorting
    if hasattr(HelpTopic, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(HelpTopic, sort_by).desc())
        else:
            query = query.order_by(getattr(HelpTopic, sort_by).asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(get_paginated_response(pagination, 'helptopics.get_helptopics', **request.args))