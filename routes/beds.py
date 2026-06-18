from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from services.bed_service import BedService

beds_bp = Blueprint('beds', __name__, url_prefix='/beds')

@beds_bp.route('', methods=['GET'])
@token_required
def get_beds():
    """Obtiene todas las camas"""
    area = request.args.get('area')
    status = request.args.get('status')  # LIBRE, OCUPADA, MANTENIMIENTO
    
    beds = BedService.get_all_beds(area, status)
    return jsonify(beds), 200

@beds_bp.route('', methods=['POST'])
@token_required
@role_required('admin')
def create_bed():
    """Crea una nueva cama"""
    data = request.get_json()
    
    required_fields = ['numero', 'area']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    result, error = BedService.create_bed(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 201

@beds_bp.route('/<int:id_cama>', methods=['PUT'])
@token_required
@role_required('admin')
def update_bed(id_cama):
    """Actualiza una cama"""
    data = request.get_json()
    
    result = BedService.update_bed(id_cama, data)
    
    if not result:
        return jsonify({'error': 'Cama no encontrada'}), 404
    
    return jsonify(result), 200

@beds_bp.route('/<int:id_cama>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_bed(id_cama):
    """Elimina una cama"""
    result, error = BedService.delete_bed(id_cama)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Cama eliminada correctamente'}), 200

@beds_bp.route('/occupancy', methods=['GET'])
@token_required
def get_occupancy():
    """Obtiene ocupación de camas por área"""
    occupancy = BedService.get_occupancy_report()
    return jsonify(occupancy), 200