from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class CustomerCategory(db.Model):
    __tablename__ = 'customer_categories'
    __table_args__ = {'schema': None}  # schema由请求动态切换

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    creator = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updater = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'creator': self.creator,
            'created_at': self.created_at,
            'updater': self.updater,
            'updated_at': self.updated_at
        } 