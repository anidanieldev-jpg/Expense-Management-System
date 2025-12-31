from flask import Blueprint
from db import service
from utils import response

bp = Blueprint('deposits', __name__, url_prefix='/v1/deposits')

@bp.route('', methods=['GET'])
def get_deposits():
    try:
        deposits = service.get_all('Deposits')
        return response(0, "success", {"deposits": deposits})
    except Exception as e:
        return response(500, str(e))
