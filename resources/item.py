import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores, items
from schemas.item import ItemSchema, UpdateItemSchema


blp = Blueprint('Items', __name__, description='Operation on items')

@blp.route('/item/<string:item_id>')
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message='Item not found.')

    def delete(self, item_id):
        try:
            del items[item_id]
            return {'message': 'Item deleted successfully.'}, 200
        except KeyError:
            abort(404, message='Item not found.')

    @blp.arguments(UpdateItemSchema)
    @blp.response(200, UpdateItemSchema)
    def put(self, item_data, item_id): # si vamos a tener mas de dos arguemnto primero debe ir el de schema luego como tal el del metodo
        try:
            item = items[item_id]
            item |= item_data
            return item
        except KeyError:
            abort(404, message='Item not found.')


@blp.route('/item')
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True)) # esto hara que el response lo convierta todo en una lista
    def get(self):
        return items.values()
    
    @blp.arguments(ItemSchema) # Con esto le agregamos el esquema crado en schemas/item.py
    @blp.response(201, ItemSchema)
    def post(self, item_data):    # ahora item_data dentro del arguemento tendra el json/diccionario que nostros enviamos en el body
        for item in items.values():
            if (
                item_data['name'] == item['name'] and
                item_data['store_id'] == item['store_id']
            ):
                abort(
                    400,
                    message='Item already exists in this store.'
                )
    
        if item_data['store_id'] not in stores:
            abort(404, message='Store not found.')
    
        item_id = uuid.uuid4().hex
        item = { **item_data, 'id': item_id }
        items[item_id] = item
    
        return item