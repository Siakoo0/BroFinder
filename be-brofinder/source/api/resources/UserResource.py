from source.api.BaseResource import BaseResource
from source.api.models.User import User
from playhouse.shortcuts import model_to_dict
import json
from flask import Flask, render_template, jsonify
from flask_restful import reqparse
from peewee import *

class UserResource(BaseResource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, help="user_id è necessario e deve essere un intero!")
    parser.add_argument('role', type=int, required=True, help="Il ruolo è necessario e deve essere un intero!")
    parser.add_argument('active', type=int, default=1, help="Specificare se questo utente è attivo, tramite un intero.")
    
    @property
    def urls(self):
        return ("/test/<int:user_id>")

    def post(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        role = args['role']
        active = args['active']
        User.create(id = user_id, role = role, is_active = active)
        return jsonify({'id': user_id, 'role': role}), 201
        
    def get(self, user_id: int):
        return {"ok" : model_to_dict(User.get(User.id == user_id))}
    
    def put(self, user_id: int):
        args = self.parser.parse_args()
        is_active = args.get('active')
        role = args.get('role')
        return jsonify({'id': user_id, 'role': role, 'active': is_active}), 201
    
    def delete(self, user_id: int):
        user = User.get_or_404(id=user_id)
        user.delete_instance()
        return '', 204 
        


    