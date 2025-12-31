from flask import Blueprint, request
import threading
from db import service
from utils import response

bp = Blueprint('sync', __name__, url_prefix='/v1/sync')

@bp.route('/status', methods=['GET'])
def get_sync_status():
    try:
        return response(0, "success", {
            "pending_count": len(service.pending_sync),
            "last_sync": service.last_sync_info,
            "settings": service.settings
        })
    except Exception as e:
        return response(500, str(e))

@bp.route('/diff', methods=['GET'])
def get_sync_diff():
    try:
        diff, error = service.get_diff()
        if diff is not None:
            return response(0, "success", diff)
        return response(500, f"Sync Connection Failed: {error}")
    except Exception as e:
        return response(500, str(e))

@bp.route('/settings', methods=['POST'])
def update_settings():
    try:
        data = request.json
        service.update_settings(data)
        return response(0, "Settings updated")
    except Exception as e:
        return response(500, str(e))

@bp.route('/force', methods=['POST'])
def force_sync():
    try:
        print("[API] Manual Sync Triggered. Dispatching background worker...")
        thread = threading.Thread(target=service.full_sync)
        thread.start()
        return response(0, "Full sync (Push + Pull) initiated in background")
    except Exception as e:
        print(f"[API] Error triggering sync: {str(e)}")
        return response(500, str(e))

@bp.route('/pull', methods=['POST'])
def force_pull():
    try:
        print("[API] Manual Pull Triggered. Dispatching background worker...")
        thread = threading.Thread(target=service.pull_from_remote)
        thread.start()
        return response(0, "Full pull initiated in background")
    except Exception as e:
        print(f"[API] Error triggering pull: {str(e)}")
        return response(500, str(e))
