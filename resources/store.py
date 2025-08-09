import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores
from schemas.store import StoreSchema, UpdateStoreSchema

blp = Blueprint('Stores', __name__, description='Operations on stores')

@blp.route('/store/<string:store_id>') # http://localhost:5001:/store/<store_id>
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message='Store not found.')

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {'message': 'Store deleted successfully.'}, 200
        except KeyError:
            abort(400, message='Store not found')

    @blp.arguments(UpdateStoreSchema)
    @blp.response(200, UpdateStoreSchema)
    def put(self, store_data, store_id):
        try:
            store = stores[store_id]
            store |= store_data
            return store
        except KeyError:
            abort(404, message='Item not found.')


@blp.route('/store')
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return {'stores': list(stores.values())}
    
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        for store in stores.values():
            if store_data['name'] == store['name']:
                abort(400, message='Store with this name already exists.')

        store_id = uuid.uuid4().hex
        store = { **store_data, 'id': store_id, }
        stores[store_id] = store
        return store, 201