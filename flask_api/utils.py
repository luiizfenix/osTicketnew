from flask import url_for
from flask_api.models import Ticket, User, Organization, Department, HelpTopic, TicketStatus, Queue

def get_paginated_response(pagination, endpoint, **kwargs):
    """
    Creates a paginated response with next and previous page URLs.
    """
    args = kwargs.copy()
    args.pop('page', None)

    next_url = url_for(
        endpoint,
        page=pagination.next_num,
        **args
    ) if pagination.has_next else None

    prev_url = url_for(
        endpoint,
        page=pagination.prev_num,
        **args
    ) if pagination.has_prev else None

    return {
        'total': pagination.total,
        'pages': pagination.pages,
        'next_page': next_url,
        'prev_page': prev_url,
        'results': [item.to_dict() for item in pagination.items]
    }