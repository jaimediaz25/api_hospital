from flask import Blueprint, request, jsonify, send_file, g
from middleware.auth_middleware import token_required, role_required
from utils.backups import realizar_backup, restaurar_backup, list_backups, limpiar_backups, check_db_health
import os

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

@backup_bp.route('', methods=['GET'])
@token_required
@role_required('admin')
def get_backups():
    """Lista backups disponibles"""
    backups = list_backups()
    return jsonify(backups), 200

@backup_bp.route('/create', methods=['POST'])
@token_required
@role_required('admin')
def create_backup():
    """Crea un nuevo backup"""
    data = request.get_json() or {}
    tipo = data.get('tipo', 'completa')
    
    backup_file = realizar_backup(tipo=tipo, comprimir=True)
    
    return jsonify({
        'message': 'Backup creado exitosamente',
        'file': os.path.basename(backup_file)
    }), 201

@backup_bp.route('/restore', methods=['POST'])
@token_required
@role_required('admin')
def restore_backup():
    """Restaura un backup"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Nombre de archivo requerido'}), 400
    
    try:
        restaurar_backup(filename)
        return jsonify({'message': 'Backup restaurado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/download/<filename>', methods=['GET'])
@token_required
@role_required('admin')
def download_backup(filename):
    """Descarga un backup"""
    backup_path = os.path.join('backups', filename)
    
    if not os.path.exists(backup_path):
        return jsonify({'error': 'Archivo no encontrado'}), 404
    
    return send_file(
        backup_path,
        as_attachment=True,
        download_name=filename
    )

@backup_bp.route('/health', methods=['GET'])
@token_required
def health_check():
    """Verifica salud de la BD"""
    health = check_db_health()
    return jsonify(health), 200

@backup_bp.route('/clean', methods=['POST'])
@token_required
@role_required('admin')
def clean_backups():
    """Limpia backups antiguos"""
    keep = request.json.get('keep', 5)
    limpiar_backups(keep)
    return jsonify({'message': f'Backups antiguos eliminados, se mantienen {keep}'}), 200