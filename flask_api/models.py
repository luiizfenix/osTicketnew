from .extensions import db
from sqlalchemy.orm import aliased

TABLE_PREFIX = 'ost_'

class User(db.Model):
    __tablename__ = f'{TABLE_PREFIX}user'
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}organization.id'))
    default_email_id = db.Column(db.Integer)
    name = db.Column(db.String(128))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    email = db.relationship('UserEmail', primaryjoin='User.default_email_id==UserEmail.id', foreign_keys='User.default_email_id', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'name': self.name,
            'email': self.email.address if self.email else None,
            'phone': self.get_phone(),
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
        }

    def get_phone(self):
        """Retrieves the user's phone number from the dynamic form data."""
        form_entry_alias = aliased(FormEntry)
        form_entry_value_alias = aliased(FormEntryValue)
        form_field_alias = aliased(FormField)

        phone_value = db.session.query(form_entry_value_alias.value).join(
            form_entry_alias, form_entry_alias.id == form_entry_value_alias.entry_id
        ).join(
            form_field_alias, form_field_alias.id == form_entry_value_alias.field_id
        ).filter(
            form_entry_alias.object_id == self.id,
            form_entry_alias.object_type == 'U',
            form_field_alias.name == 'phone'
        ).scalar()

        return phone_value

class UserEmail(db.Model):
    __tablename__ = f'{TABLE_PREFIX}user_email'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}user.id'))
    address = db.Column(db.String(128))

class Department(db.Model):
    __tablename__ = f'{TABLE_PREFIX}department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    ispublic = db.Column(db.Boolean)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ispublic': self.ispublic,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
        }

class HelpTopic(db.Model):
    __tablename__ = f'{TABLE_PREFIX}help_topic'
    topic_id = db.Column(db.Integer, primary_key=True)
    ispublic = db.Column(db.Boolean)
    topic = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'topic_id': self.topic_id,
            'ispublic': self.ispublic,
            'topic': self.topic,
            'notes': self.notes,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
        }

class Organization(db.Model):
    __tablename__ = f'{TABLE_PREFIX}organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
        }

class Ticket(db.Model):
    __tablename__ = f'{TABLE_PREFIX}ticket'
    ticket_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}user.id'))
    status_id = db.Column(db.Integer)
    dept_id = db.Column(db.Integer)
    topic_id = db.Column(db.Integer)
    staff_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    closed = db.Column(db.DateTime)

    user = db.relationship('User', backref='tickets')
    status = db.relationship('TicketStatus', primaryjoin='Ticket.status_id==TicketStatus.id', foreign_keys='Ticket.status_id', uselist=False)

    def to_dict(self):
        return {
            'ticket_id': self.ticket_id,
            'number': self.number,
            'user_id': self.user_id,
            'status_id': self.status_id,
            'dept_id': self.dept_id,
            'topic_id': self.topic_id,
            'staff_id': self.staff_id,
            'team_id': self.team_id,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
            'closed': self.closed.isoformat() if self.closed else None,
            'user': self.user.to_dict() if self.user else None
        }

class Thread(db.Model):
    __tablename__ = f'{TABLE_PREFIX}thread'
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}ticket.ticket_id'))
    object_type = db.Column(db.String(1), default='T')
    created = db.Column(db.DateTime)

    entries = db.relationship('ThreadEntry', backref='thread', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'object_id': self.object_id,
            'object_type': self.object_type,
            'created': self.created.isoformat() if self.created else None,
            'entries': [entry.to_dict() for entry in self.entries]
        }

class ThreadEntry(db.Model):
    __tablename__ = f'{TABLE_PREFIX}thread_entry'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}thread.id'))
    staff_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    type = db.Column(db.String(1))
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    attachments = db.relationship('Attachment', backref='entry', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'staff_id': self.staff_id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
            'attachments': [attachment.to_dict() for attachment in self.attachments]
        }

class Attachment(db.Model):
    __tablename__ = f'{TABLE_PREFIX}attachment'
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    type = db.Column(db.String(1))
    file_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}file.id'))
    entry_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}thread_entry.id'))

    file = db.relationship('File', backref='attachment', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'object_id': self.object_id,
            'type': self.type,
            'file': self.file.to_dict() if self.file else None
        }

class File(db.Model):
    __tablename__ = f'{TABLE_PREFIX}file'
    id = db.Column(db.Integer, primary_key=True)
    ft = db.Column(db.String(1))
    bk = db.Column(db.String(1))
    type = db.Column(db.String(255))
    size = db.Column(db.Integer)
    name = db.Column(db.String(255))
    key = db.Column(db.String(255))
    signature = db.Column(db.String(255))
    created = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'size': self.size,
            'name': self.name,
            'created': self.created.isoformat() if self.created else None,
        }

class Form(db.Model):
    __tablename__ = f'{TABLE_PREFIX}form'
    id = db.Column(db.Integer, primary_key=True)
    form_type = db.Column('type', db.String(1))
    title = db.Column(db.String(255))

    fields = db.relationship('FormField', backref='form', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'form_type': self.form_type,
            'title': self.title,
            'fields': [field.to_dict() for field in self.fields]
        }

class FormField(db.Model):
    __tablename__ = f'{TABLE_PREFIX}form_field'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}form.id'))
    type = db.Column(db.String(32))
    label = db.Column(db.String(255))
    name = db.Column(db.String(64))

    def to_dict(self):
        return {
            'id': self.id,
            'form_id': self.form_id,
            'type': self.type,
            'label': self.label,
            'name': self.name,
        }

class FormEntry(db.Model):
    __tablename__ = f'{TABLE_PREFIX}form_entry'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}form.id'))
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(1))

    values = db.relationship('FormEntryValue', backref='entry', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'form_id': self.form_id,
            'object_id': self.object_id,
            'object_type': self.object_type,
            'values': [value.to_dict() for value in self.values]
        }

class FormEntryValue(db.Model):
    __tablename__ = f'{TABLE_PREFIX}form_entry_values'
    entry_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}form_entry.id'), primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey(f'{TABLE_PREFIX}form_field.id'), primary_key=True)
    value = db.Column(db.Text)

    field = db.relationship('FormField')

    def to_dict(self):
        return {
            'field_id': self.field_id,
            'value': self.value,
            'field': self.field.to_dict() if self.field else None
        }

class FAQ(db.Model):
    __tablename__ = f'{TABLE_PREFIX}faq'
    id = db.Column(db.Integer, primary_key=True)
    ispublished = db.Column(db.Boolean)
    question = db.Column(db.String(255))
    answer = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'ispublished': self.ispublished,
            'question': self.question,
            'answer': self.answer,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
        }

class Queue(db.Model):
    __tablename__ = f'{TABLE_PREFIX}queue'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer)
    staff_id = db.Column(db.Integer)
    title = db.Column(db.String(60))
    sort = db.Column(db.Integer)
    config = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'staff_id': self.staff_id,
            'title': self.title,
            'sort': self.sort,
            'config': self.config,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
        }

class TicketStatus(db.Model):
    __tablename__ = f'{TABLE_PREFIX}ticket_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    state = db.Column(db.String(16))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
        }