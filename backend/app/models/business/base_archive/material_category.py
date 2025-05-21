from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class MaterialCategory(db.Model):
    __tablename__ = 'material_categories'
    __table_args__ = {'schema': None}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    attr = db.Column(db.String(100))
    unit = db.Column(db.String(20))
    aux_unit = db.Column(db.String(20))
    sale_unit = db.Column(db.String(20))
    density = db.Column(db.Numeric)
    inspect_type = db.Column(db.String(50))
    last_price = db.Column(db.Numeric)
    sale_price = db.Column(db.Numeric)
    quote_price = db.Column(db.Numeric)
    weight = db.Column(db.Numeric)
    shelf_life = db.Column(db.Integer)
    warn_days = db.Column(db.Integer)
    subject = db.Column(db.String(100))
    remark = db.Column(db.Text)
    batch = db.Column(db.Boolean)
    barcode = db.Column(db.Boolean)
    custom_spec = db.Column(db.Boolean)
    is_ink = db.Column(db.Boolean)
    is_part = db.Column(db.Boolean)
    is_resin = db.Column(db.Boolean)
    is_roll = db.Column(db.Boolean)
    is_waste = db.Column(db.Boolean)
    is_glue = db.Column(db.Boolean)
    is_zip = db.Column(db.Boolean)
    is_foil = db.Column(db.Boolean)
    is_box = db.Column(db.Boolean)
    is_core = db.Column(db.Boolean)
    is_solvent = db.Column(db.Boolean)
    is_self_made = db.Column(db.Boolean)
    no_dock = db.Column(db.Boolean)
    cost_required = db.Column(db.Boolean)
    cost_share = db.Column(db.Boolean)
    creator = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updater = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'attr': self.attr,
            'unit': self.unit,
            'aux_unit': self.aux_unit,
            'sale_unit': self.sale_unit,
            'density': self.density,
            'inspect_type': self.inspect_type,
            'last_price': self.last_price,
            'sale_price': self.sale_price,
            'quote_price': self.quote_price,
            'weight': self.weight,
            'shelf_life': self.shelf_life,
            'warn_days': self.warn_days,
            'subject': self.subject,
            'remark': self.remark,
            'batch': self.batch,
            'barcode': self.barcode,
            'custom_spec': self.custom_spec,
            'is_ink': self.is_ink,
            'is_part': self.is_part,
            'is_resin': self.is_resin,
            'is_roll': self.is_roll,
            'is_waste': self.is_waste,
            'is_glue': self.is_glue,
            'is_zip': self.is_zip,
            'is_foil': self.is_foil,
            'is_box': self.is_box,
            'is_core': self.is_core,
            'is_solvent': self.is_solvent,
            'is_self_made': self.is_self_made,
            'no_dock': self.no_dock,
            'cost_required': self.cost_required,
            'cost_share': self.cost_share,
            'creator': self.creator,
            'created_at': self.created_at,
            'updater': self.updater,
            'updated_at': self.updated_at
        } 