from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class SupplierCategory(db.Model):
    __tablename__ = 'supplier_categories'
    __table_args__ = {'schema': None}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    plate = db.Column(db.Boolean, default=False)
    outsource = db.Column(db.Boolean, default=False)
    knife = db.Column(db.Boolean, default=False)
    creator = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updater = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'plate': self.plate,
            'outsource': self.outsource,
            'knife': self.knife,
            'creator': self.creator,
            'created_at': self.created_at,
            'updater': self.updater,
            'updated_at': self.updated_at
        } 