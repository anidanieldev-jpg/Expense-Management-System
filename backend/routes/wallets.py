from flask import Blueprint, request
from db import service
from utils import response, generate_id

bp = Blueprint('wallets', __name__, url_prefix='/v1/wallets')

@bp.route('', methods=['GET'])
def get_wallets():
    try:
        wallets = service.get_all('Wallets')
        return response(0, "success", {"wallets": wallets})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['GET'])
def get_wallet_by_id(id):
    try:
        wallet = service.get_by_id('Wallets', id)
        if not wallet:
            return response(404, "Wallet not found")
        return response(0, "success", {"wallet": wallet})
    except Exception as e:
        return response(500, str(e))

@bp.route('', methods=['POST'])
def create_wallet():
    try:
        data = request.json
        new_wallet = {
            "id": generate_id('WLT'),
            "name": data['name'],
            "balance": data.get('balance', 0),
            "currency": data.get('currency', 'NGN')
        }
        service.create('Wallets', new_wallet)
        return response(0, "Wallet created", {"wallet": new_wallet})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['PATCH'])
def update_wallet(id):
    try:
        data = request.json
        updated = service.update('Wallets', id, data)
        if not updated:
            return response(404, "Wallet not found")
        return response(0, "Wallet updated", {"wallet": updated})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['DELETE'])
def delete_wallet(id):
    try:
        success = service.delete('Wallets', id)
        if not success:
            return response(404, "Wallet not found")
        return response(0, "Wallet deleted")
    except Exception as e:
        return response(500, str(e))
