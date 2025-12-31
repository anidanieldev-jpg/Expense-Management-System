from flask import Blueprint, request
from db import service
from utils import response, generate_id, today

bp = Blueprint('expenses', __name__, url_prefix='/v1/expenses')

@bp.route('', methods=['GET'])
def get_expenses():
    try:
        expenses = service.get_all('Expenses')
        return response(0, "success", {"expenses": expenses})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['GET'])
def get_expense_by_id(id):
    try:
        expense = service.get_by_id('Expenses', id)
        if not expense:
            return response(404, "Expense not found")
        return response(0, "success", {"expense": expense})
    except Exception as e:
        return response(500, str(e))

@bp.route('', methods=['POST'])
def create_expense():
    try:
        data = request.json
        total = float(data['total'])
        new_expense = {
            "id": generate_id('AEX'),
            "vendorId": data['vendorId'],
            "date": data.get('date', today()),
            "total": total,
            "balance": total,
            "status": "Unpaid",
            "category": data.get('category', 'Other'),
            "description": data.get('description', '')
        }
        service.create('Expenses', new_expense)
        return response(0, "Expense recorded", {"expense": new_expense})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['PATCH'])
def update_expense(id):
    try:
        data = request.json
        updated = service.update('Expenses', id, data)
        if not updated:
            return response(404, "Expense not found")
        return response(0, "Expense updated", {"expense": updated})
    except Exception as e:
        return response(500, str(e))

@bp.route('/<id>', methods=['DELETE'])
def delete_expense(id):
    try:
        success = service.delete('Expenses', id)
        if not success:
            return response(404, "Expense not found")
        return response(0, "Expense deleted")
    except Exception as e:
        return response(500, str(e))
