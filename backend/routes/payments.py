from flask import Blueprint, request
from db import service
from utils import response, generate_id, today

bp = Blueprint('payments', __name__, url_prefix='/v1/payments')

@bp.route('', methods=['GET'])
def get_payments():
    try:
        payments = service.get_all('Payments')
        return response(0, "success", {"payments": payments})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['GET'])
def get_payment_by_id(id):
    try:
        payment = service.get_by_id('Payments', id)
        if not payment:
            return response(404, "Payment not found")
        return response(0, "success", {"payment": payment})
    except Exception as e:
        return response(500, str(e))

@bp.route('', methods=['POST'])
def create_payment():
    try:
        data = request.json
        txn_type = data.get('type', 'payment')
        
        if txn_type == 'deposit':
             deposit_payload = {
                "id": generate_id('DEP'),
                "date": today(),
                "amount": data['amount'],
                "walletId": data['walletId'],
                "vendorId": data.get('vendorId'),
                "notes": "Transfer from Vendor"
            }
             service.process_deposit(deposit_payload)
             return response(0, "Deposit processed successfully", {"deposit": deposit_payload})
        else:
            payment_payload = {
                "id": generate_id('PAY'),
                "date": today(),
                "amount": data['amount'],
                "walletId": data['walletId'],
                "vendorId": data['vendorId'],
                "allocations": data['allocations']
            }
            service.process_payment(payment_payload)
            return response(0, "Payment processed successfully", {"payment": payment_payload})
    except Exception as e:
        return response(2001, str(e))
@bp.route('/<id>', methods=['DELETE'])
def delete_payment(id):
    try:
        success = service.delete('Payments', id)
        if not success:
            return response(404, "Payment not found")
        return response(0, "Payment deleted successfully")
    except Exception as e:
        return response(500, str(e))
