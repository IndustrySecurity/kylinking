from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    __table_args__ = {'schema': None}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100))
    is_blow = db.Column(db.Boolean, default=False)
    creator = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updater = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'subject': self.subject,
            'is_blow': self.is_blow,
            'creator': self.creator,
            'created_at': self.created_at,
            'updater': self.updater,
            'updated_at': self.updated_at
        } 