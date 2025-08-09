from marshmallow import Schema, fields

class ItemSchema(Schema):
    id       = fields.Str(dump_only=True) # Esto quiere decir que no es neceario y solamente sera una dato que se devuelve en el response de la API
    name     = fields.Str(required=True)
    price    = fields.Float(required=True)
    store_id = fields.Str(required=True)

class UpdateItemSchema(Schema):
    name  = fields.Str(required=True)
    price = fields.Float(required=True)