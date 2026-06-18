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
        'username': user['username'],
        'role': user.get('role'),
        'nombre': user.get('nombre'),
        'papell': user.get('papell')
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