from marshmallow import Schema, fields

class PlainItemSchema(Schema):
    id       = fields.Int(dump_only=True) # Esto quiere decir que no es neceario y solamente sera una dato que se devuelve en el response de la API
    name     = fields.Str(required=True)
    price    = fields.Float(required=True)

class PlainStoreSchema(Schema):
    id   = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class PlainTagSchema(Schema):
    id   = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class UpdateItemSchema(Schema):
    id       = fields.Str(dump_only=True)
    name     = fields.Str()
    price    = fields.Float()
    store    = fields.Nested(PlainStoreSchema(), dump_only=True) # Aca estamos hacinedo un valor anidado 
    store_id = fields.Int(required=False, load_only=True)

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    
    store    = fields.Nested(PlainStoreSchema(), dump_only=True) # Aca estamos hacinedo un valor anidado 

class UpdateStoreSchema(Schema):
    id   = fields.Str(dump_only=True)
    name = fields.Str()

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags  = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class TagSchema(PlainTagSchema):
    store_id = fields.Int(dump_only=True)

    store    = fields.Nested(PlainStoreSchema(), dump_only=True)  # Aca estamos hacinedo un valor anidado