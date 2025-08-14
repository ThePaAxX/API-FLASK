from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import ItemModel
from schemas import ItemSchema, UpdateItemSchema


blp = Blueprint('Items', __name__, description='Operation on items')

@blp.route('/item/<int:item_id>')
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get('is_admin'):
            abort(403, message="Admin privilege required to delete an item.")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted.'}

    @jwt_required()
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
    @jwt_required()  # Esto asegura que el usuario debe estar autenticado para ver los items
    @blp.response(200, ItemSchema(many=True)) # esto hara que el response lo convierta todo en una lista
    def get(self):
        return ItemModel.query.all()  # Esto devuelve todos los items de la base de datos
    
    @jwt_required()  # Esto asegura que el usuario debe estar autenticado para crear un item
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