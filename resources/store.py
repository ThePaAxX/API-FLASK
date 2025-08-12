import uuid

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema, UpdateStoreSchema

blp = Blueprint('Stores', __name__, description='Operations on stores')

@blp.route('/store/<string:store_id>') # http://localhost:5001:/store/<store_id>
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {'message': 'Store deleted.'}

    @blp.arguments(UpdateStoreSchema)
    @blp.response(200, UpdateStoreSchema)
    def put(self, store_data, store_id):
        store = StoreModel.query.get(store_id)

        if store:
            name_store = store_data['name']

            if StoreModel.query.filter_by(name=name_store).one_or_none() is None:
                store.name = name_store

                db.session.add(store)
                db.session.commit()
                return store
            else:
                abort(
                    400, 
                    message='A store with that name already exists.')
        else:
            abort(
                404, 
                message='Store not found.')
        # if store:
        #     store.name = store_data['name']
        # else:
        #     abort(404, message="Store not found.")


@blp.route('/store')
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):

        store = StoreModel(**store_data)
        print(store)

        try:
            db.session.add(store)
            db.session.commit()
        
        except IntegrityError:
            abort(
                400, 
                message='A store with that name already exists.')
        except SQLAlchemyError:
            abort(
                500, 
                message=f'An error occurred while inserting the store.')

        return store