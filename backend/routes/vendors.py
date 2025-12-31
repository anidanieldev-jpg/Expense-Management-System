from flask import Blueprint, request
from db import service
from utils import response, generate_id

bp = Blueprint('vendors', __name__, url_prefix='/v1/vendors')

@bp.route('', methods=['GET'])
def get_vendors():
    try:
        vendors = service.get_all('Vendors')
        return response(0, "success", {"vendors": vendors})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['GET'])
def get_vendor_by_id(id):
    try:
        vendor = service.get_by_id('Vendors', id)
        if not vendor:
            return response(404, "Vendor not found")
        return response(0, "success", {"vendor": vendor})
    except Exception as e:
        return response(500, str(e))

@bp.route('', methods=['POST'])
def create_vendor():
    try:
        data = request.json
        if not data.get('name'):
            return response(1001, "Vendor name is required")
        
        new_vendor = {
            "id": generate_id('VND'),
            "name": data['name'],
            "address": data.get('address', ''),
            "phone": data.get('phone', '')
        }
        service.create('Vendors', new_vendor)
        return response(0, "Vendor created", {"vendor": new_vendor})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['PATCH'])
def update_vendor(id):
    try:
        data = request.json
        updated = service.update('Vendors', id, data)
        if not updated:
            return response(404, "Vendor not found")
        return response(0, "Vendor updated", {"vendor": updated})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['DELETE'])
def delete_vendor(id):
    try:
        success = service.delete('Vendors', id)
        if not success:
            return response(404, "Vendor not found")
        return response(0, "Vendor deleted")
    except Exception as e:
        return response(500, str(e))
