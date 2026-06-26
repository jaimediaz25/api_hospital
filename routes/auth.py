from flask import Blueprint, request, jsonify, g
from services.auth_service import AuthService
from middleware.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login de usuario"""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400

    result, error = AuthService.login(username, password)

    if error:
        return jsonify({'error': error}), 401

    return jsonify(result), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Obtiene información del usuario actual"""
    from models.user import UserModel

    user = UserModel.find_by_id(g.user['user_id'])

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id': str(user['_id']),
        'username': user.get('username'),
        'role': user.get('role'),
        'nombre': user.get('nombre'),
        'papell': user.get('papell'),
        'sapell': user.get('sapell'),
        'email': user.get('email'),
        'telefono': user.get('telefono'),
        'activo': user.get('activo', True)
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Cambia la contraseña del usuario"""
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'error': 'Contraseñas requeridas'}), 400

    success, message = AuthService.change_password(
        g.user['user_id'],
        old_password,
        new_password
    )

    if not success:
        return jsonify({'error': message}), 400

    return jsonify({'message': message}), 200


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout (cliente debe eliminar el token)"""
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200


# ==========================================================
# USUARIOS DEL SISTEMA - MÓDULO CONFIGURACIÓN
# ==========================================================

def is_admin():
    """Valida si el usuario actual es admin"""
    return g.user.get('role') == 'admin'


@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """Lista usuarios del sistema"""
    from models.user import UserModel

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    users = UserModel.get_all(page=1, page_size=100)

    return jsonify(users), 200


@auth_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    """Crea un nuevo usuario del sistema"""
    from models.user import UserModel

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400

    existing = UserModel.find_by_username(data.get('username'))

    if existing:
        return jsonify({'error': 'El usuario ya existe'}), 400

    user = UserModel.create(data)

    return jsonify(user), 201


@auth_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Actualiza un usuario del sistema"""
    from bson import ObjectId
    from utils.database import get_collection

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    collection = get_collection('users')

    allowed_fields = [
        'username',
        'role',
        'nombre',
        'papell',
        'sapell',
        'email',
        'telefono',
        'activo'
    ]

    update_data = {}

    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]

    if not update_data:
        return jsonify({'error': 'No hay datos para actualizar'}), 400

    try:
        result = collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    except Exception:
        result = collection.update_one(
            {'id': user_id},
            {'$set': update_data}
        )

    if result.matched_count == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'message': 'Usuario actualizado correctamente'}), 200


@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """Elimina un usuario del sistema"""
    from bson import ObjectId
    from utils.database import get_collection

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    collection = get_collection('users')

    try:
        result = collection.delete_one({'_id': ObjectId(user_id)})
    except Exception:
        result = collection.delete_one({'id': user_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'message': 'Usuario eliminado correctamente'}), 200