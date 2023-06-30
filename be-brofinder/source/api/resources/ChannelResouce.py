from source.api.BaseResource import BaseResource
from source.api.models.User import User
from playhouse.shortcuts import model_to_dict
import json
from flask import Flask, render_template, jsonify
from flask_restful import reqparse
from peewee import *




class UserResource(BaseResource):
    
    @property
    def urls(self):
        return ("/test/<int:channel_id>")
    
    def post(self):
        
        pass
    
    def get():
        pass
    
    def put():
        pass
    
    def delete():
        pass