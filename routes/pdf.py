from flask import Blueprint, request, jsonify, send_file, g
from middleware.auth_middleware import token_required
from services.pdf_service import PDFService
from datetime import datetime

pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdf')

@pdf_bp.route('/initial-sheet/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_initial_sheet(id_exp, id_atencion):
    """Genera hoja inicial de paciente"""
    pdf_file = PDFService.generate_initial_sheet(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hoja_inicial_{id_atencion}.pdf'
    )

@pdf_bp.route('/front-sheet/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_front_sheet(id_exp, id_atencion):
    """Genera hoja frontal"""
    pdf_file = PDFService.generate_front_sheet(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hoja_frontal_{id_atencion}.pdf'
    )

@pdf_bp.route('/contract/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_contract(id_exp, id_atencion):
    """Genera contrato de servicios"""
    pdf_file = PDFService.generate_contract(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'contrato_{id_atencion}.pdf'
    )

@pdf_bp.route('/consent/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_consent(id_exp, id_atencion):
    """Genera consentimiento de datos personales"""
    pdf_file = PDFService.generate_consent(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'consentimiento_{id_atencion}.pdf'
    )

@pdf_bp.route('/vital-signs/<int:id_signos>', methods=['GET'])
@token_required
def get_vital_signs_pdf(id_signos):
    """Genera PDF de signos vitales"""
    pdf_file = PDFService.generate_vital_signs_pdf(id_signos)
    
    if not pdf_file:
        return jsonify({'error': 'Signos vitales no encontrados'}), 404
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'signos_vitales_{id_signos}.pdf'
    )

@pdf_bp.route('/medical-note/<int:id_nota>', methods=['GET'])
@token_required
def get_medical_note_pdf(id_nota):
    """Genera PDF de nota médica"""
    pdf_file = PDFService.generate_medical_note_pdf(id_nota)
    
    if not pdf_file:
        return jsonify({'error': 'Nota médica no encontrada'}), 404
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'nota_medica_{id_nota}.pdf'
    )

@pdf_bp.route('/diagnosis/<int:id_diagnostico>', methods=['GET'])
@token_required
def get_diagnosis_pdf(id_diagnostico):
    """Genera PDF de diagnóstico"""
    pdf_file = PDFService.generate_diagnosis_pdf(id_diagnostico)
    
    if not pdf_file:
        return jsonify({'error': 'Diagnóstico no encontrado'}), 404
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'diagnostico_{id_diagnostico}.pdf'
    )

@pdf_bp.route('/prescription/<int:id_receta>', methods=['GET'])
@token_required
def get_prescription_pdf(id_receta):
    """Genera PDF de receta médica"""
    pdf_file = PDFService.generate_prescription_pdf(id_receta)
    
    if not pdf_file:
        return jsonify({'error': 'Receta no encontrada'}), 404
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'receta_{id_receta}.pdf'
    )

@pdf_bp.route('/lab/<int:id_examen>', methods=['GET'])
@token_required
def get_lab_pdf(id_examen):
    """Genera PDF de resultados de laboratorio"""
    pdf_file = PDFService.generate_lab_pdf(id_examen)
    
    if not pdf_file:
        return jsonify({'error': 'Examen no encontrado'}), 404
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'laboratorio_{id_examen}.pdf'
    )

@pdf_bp.route('/imaging/<int:id_examen>', methods=['GET'])
@token_required
def get_imaging_pdf(id_examen):
    """Genera PDF de resultados de gabinete"""
    pdf_file = PDFService.generate_imaging_pdf(id_examen)
    
    if not pdf_file:
        return jsonify({'error': 'Examen no encontrado'}), 404
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'gabinete_{id_examen}.pdf'
    )