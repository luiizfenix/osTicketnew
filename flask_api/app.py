import os
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flasgger import Swagger

# Load environment variables from .env file
load_dotenv()

# --- App Initialization ---
app = Flask(__name__)

# Database connection
db_uri = os.getenv('DATABASE_URI')
if not db_uri:
    db_config = {
        'DBUSER': os.getenv('DBUSER', 'root'),
        'DBPASS': os.getenv('DBPASS', ''),
        'DBHOST': os.getenv('DBHOST', 'localhost'),
        'DBNAME': os.getenv('DBNAME', 'osticket'),
        'TABLE_PREFIX': os.getenv('TABLE_PREFIX', 'ost_')
    }
    db_uri = f"mysql+pymysql://{db_config['DBUSER']}:{db_config['DBPASS']}@{db_config['DBHOST']}/{db_config['DBNAME']}"

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Flasgger Initialization ---
app.config['SWAGGER'] = {
    'title': 'osTicket API',
    'uiversion': 3,
    'definitions': {
        "Ticket": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer"},
                "number": {"type": "string"},
                "user_id": {"type": "integer"},
                "status_id": {"type": "integer"},
                "dept_id": {"type": "integer"},
                "topic_id": {"type": "integer"},
                "staff_id": {"type": "integer"},
                "team_id": {"type": "integer"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "closed": {"type": "string", "format": "date-time"},
                "user": {"$ref": "#/definitions/User"}
            }
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "org_id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"}
            }
        },
        "Organization": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"}
            }
        },
        "Thread": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "object_id": {"type": "integer"},
                "object_type": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "entries": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/ThreadEntry"}
                }
            }
        },
        "ThreadEntry": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "thread_id": {"type": "integer"},
                "staff_id": {"type": "integer"},
                "user_id": {"type": "integer"},
                "type": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "attachments": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Attachment"}
                }
            }
        },
        "Attachment": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "object_id": {"type": "integer"},
                "type": {"type": "string"},
                "file": {"$ref": "#/definitions/File"}
            }
        },
        "File": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "type": {"type": "string"},
                "size": {"type": "integer"},
                "name": {"type": "string"},
                "created": {"type": "string", "format": "date-time"}
            }
        },
        "Form": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "string"},
                "fields": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/FormField"}
                }
            }
        },
        "FormField": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "form_id": {"type": "integer"},
                "type": {"type": "string"},
                "label": {"type": "string"},
                "name": {"type": "string"}
            }
        },
        "FormEntry": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "form_id": {"type": "integer"},
                "object_id": {"type": "integer"},
                "object_type": {"type": "string"},
                "values": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/FormEntryValue"}
                }
            }
        },
        "FormEntryValue": {
            "type": "object",
            "properties": {
                "field_id": {"type": "integer"},
                "value": {"type": "string"},
                "field": {"$ref": "#/definitions/FormField"}
            }
        },
        "FAQ": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "category_id": {"type": "integer"},
                "ispublished": {"type": "boolean"},
                "question": {"type": "string"},
                "answer": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"}
            }
        },
        "Department": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "ispublic": {"type": "boolean"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"}
            }
        },
        "HelpTopic": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "integer"},
                "ispublic": {"type": "boolean"},
                "topic": {"type": "string"},
                "notes": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"}
            }
        }
    }
}
swagger = Swagger(app)

# --- Import Routes ---
# Import routes after db initialization to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True)