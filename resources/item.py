import uuid

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import ItemModel
from schemas import ItemSchema, UpdateItemSchema


blp = Blueprint('Items', __name__, description='Operation on items')

@blp.route('/item/<string:item_id>')
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted.'}

    @blp.arguments(UpdateItemSchema)
    @blp.response(200, UpdateItemSchema)
    def put(self, item_data, item_id): # si vamos a tener mas de dos arguemnto primero debe ir el de schema luego como tal el del metodo
        item = ItemModel.query.get(item_id)

        if item:
            item.price = item_data['price']
            item.name  = item_data['name']
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route('/item')
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True)) # esto hara que el response lo convierta todo en una lista
    def get(self):
        return ItemModel.query.all()  # Esto devuelve todos los items de la base de datos
    
    @blp.arguments(ItemSchema) # Con esto le agregamos el esquema crado en schemas/item.py
    @blp.response(201, ItemSchema)
    def post(self, item_data):    # ahora item_data dentro del arguemento tendra el json/diccionario que nostros enviamos en el body
        # Aca se elimino la comprobacion si existe el obj dentro de la bbdd ya que el name esta en UNQ
    
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(
                400, 
                message='An item with that name already exists.')
        except SQLAlchemyError:
            abort(
                500, 
                message=f'An error ocurred while inserting the item.')

        return item