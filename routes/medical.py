# routes/medical.py
from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from utils.database import get_db, serialize_doc, get_next_sequence
from bson import ObjectId
from datetime import datetime
from services.medical_service import MedicalService

medical_bp = Blueprint('medical', __name__, url_prefix='/medical')

@medical_bp.route('/medico', methods=['GET'])
@token_required
def get_medico_dashboard():
    """Obtiene los datos del módulo médico - IGUAL QUE TU CÓDIGO ORIGINAL"""
    try:
        db = get_db()
        
        # =============================
        # CONSULTA EXTERNA (Ambulatorio)
        # =============================
        beds_consulta = list(db['atencion'].aggregate([
            {"$match": {"area": "Ambulatorio", "status": "ABIERTA"}},
            {"$lookup": {
                "from": "pacientes",
                "localField": "Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": "$paciente"},
            {"$project": {
                "id_atencion": 1,
                "num_cama": {"$concat": ["Consulta ", {"$toString": "$id_atencion"}]},
                "estatus": {"$literal": "OCUPADA"},
                "nom_pac": "$paciente.nom_pac",
                "papell": "$paciente.papell",
                "sapell": "$paciente.sapell",
                "Id_exp": "$paciente.Id_exp",
                "tiene_atencion": {"$literal": True},
                "id_atencion": {"$ifNull": ["$id_atencion", None]}
            }}
        ]))
        
        # =============================
        # URGENCIAS
        # =============================
        beds_preparacion = list(db['camas'].aggregate([
            {"$match": {"area": "Urgencias"}},
            {"$lookup": {
                "from": "atencion",
                "let": {"id_cama": "$id_cama"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$eq": ["$id_cama", "$$id_cama"]},
                        "status": "ABIERTA"
                    }}
                ],
                "as": "atencion"
            }},
            {"$unwind": {"path": "$atencion", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": {"path": "$paciente", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "id_cama": 1,
                "id_atencion": {"$ifNull": ["$atencion.id_atencion", None]},
                "num_cama": "$numero",
                "estatus": {
                    "$cond": [
                        {"$and": [
                            {"$ifNull": ["$atencion", False]},
                            {"$eq": ["$atencion.status", "ABIERTA"]}
                        ]},
                        "OCUPADA",
                        "LIBRE"
                    ]
                },
                "nom_pac": "$paciente.nom_pac",
                "papell": "$paciente.papell",
                "sapell": "$paciente.sapell",
                "Id_exp": "$paciente.Id_exp",
                "tiene_atencion": {
                    "$cond": [
                        {"$and": [
                            {"$ifNull": ["$atencion.id_atencion", False]},
                            {"$eq": ["$atencion.status", "ABIERTA"]}
                        ]},
                        True,
                        False
                    ]
                }
            }}
        ]))
        
        # =============================
        # HOSPITALIZADO
        # =============================
        beds_recuperacion = list(db['camas'].aggregate([
            {"$match": {"area": "Hospitalizado"}},
            {"$lookup": {
                "from": "atencion",
                "let": {"id_cama": "$id_cama"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$eq": ["$id_cama", "$$id_cama"]},
                        "status": "ABIERTA"
                    }}
                ],
                "as": "atencion"
            }},
            {"$unwind": {"path": "$atencion", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": {"path": "$paciente", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "id_cama": 1,
                "id_atencion": {"$ifNull": ["$atencion.id_atencion", None]},
                "num_cama": "$numero",
                "estatus": {
                    "$cond": [
                        {"$and": [
                            {"$ifNull": ["$atencion", False]},
                            {"$eq": ["$atencion.status", "ABIERTA"]}
                        ]},
                        "OCUPADA",
                        "LIBRE"
                    ]
                },
                "nom_pac": "$paciente.nom_pac",
                "papell": "$paciente.papell",
                "sapell": "$paciente.sapell",
                "Id_exp": "$paciente.Id_exp",
                "tiene_atencion": {
                    "$cond": [
                        {"$and": [
                            {"$ifNull": ["$atencion.id_atencion", False]},
                            {"$eq": ["$atencion.status", "ABIERTA"]}
                        ]},
                        True,
                        False
                    ]
                }
            }}
        ]))
        
        # Usar serialize_doc para convertir ObjectId y fechas
        return jsonify({
            'beds_consulta': serialize_doc(beds_consulta),
            'beds_preparacion': serialize_doc(beds_preparacion),
            'beds_recuperacion': serialize_doc(beds_recuperacion)
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/paciente/<int:id_atencion>/<int:Id_exp>', methods=['GET'])
@token_required
def get_paciente(id_atencion, Id_exp):
    """Obtiene los datos de un paciente para el médico"""
    try:
        db = get_db()
        
        pipeline = [
            {"$match": {"Id_exp": Id_exp}},
            {"$lookup": {
                "from": "atencion",
                "localField": "Id_exp",
                "foreignField": "Id_exp",
                "as": "atencion"
            }},
            {"$unwind": "$atencion"},
            {"$match": {"atencion.id_atencion": id_atencion}},
            {"$project": {
                "Id_exp": 1,
                "papell": 1,
                "sapell": 1,
                "nom_pac": 1,
                "fecnac": 1,
                "id_cama": "$atencion.id_cama",
                "area": "$atencion.area",
                "motivo_atn": {"$ifNull": ["$atencion.motivo", ""]},
                "alergias": {"$ifNull": ["$atencion.alergias", ""]},
                "fecha": "$atencion.fecha_ing"
            }}
        ]
        
        resultado = list(db['pacientes'].aggregate(pipeline))
        if not resultado:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        paciente = resultado[0]
        
        # Obtener familiar
        familiar = db['familiares'].find_one({"Id_exp": Id_exp})
        
        # Obtener médicos
        pipeline_med = [
            {"$match": {"id_atencion": id_atencion}},
            {"$lookup": {
                "from": "users",
                "localField": "id_medico",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
            {"$project": {"doctor": "$user.username"}}
        ]
        
        medicos = list(db['atencion_medicos'].aggregate(pipeline_med))
        
        # Obtener cama
        cama = {"num_cama": "Sin Cama", "tipo": ""}
        if paciente.get("id_cama"):
            cama_data = db['camas'].find_one({"id_cama": paciente['id_cama']})
            if cama_data:
                cama = {
                    "num_cama": cama_data.get("numero"),
                    "tipo": cama_data.get("area")
                }
        
        return jsonify({
            'paciente': serialize_doc(paciente),
            'familiar': serialize_doc(familiar),
            'medicos': serialize_doc(medicos),
            'cama': serialize_doc(cama)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@medical_bp.route('/historia-clinica/<int:id_atencion>/<int:Id_exp>', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def save_historia_clinica(id_atencion, Id_exp):
    """Guarda la historia clínica del paciente"""
    try:
        db = get_db()
        data = request.get_json()
        
        # Verificar si ya existe una historia clínica para esta atención
        existing = db['historia_clinica'].find_one({
            'id_atencion': id_atencion,
            'Id_exp': Id_exp
        })
        
        # Preparar los datos
        historia_data = {
            'id_atencion': id_atencion,
            'Id_exp': Id_exp,
            'motivo_consulta': data.get('motivo_consulta', ''),
            'sintomatologia': data.get('sintomatologia', ''),
            'sintomatologia_otros': data.get('sintomatologia_otros', ''),
            'heredo': data.get('heredo', ''),
            'heredo_otros': data.get('heredo_otros', ''),
            'nopat': data.get('nopat', ''),
            'nopat_otros': data.get('nopat_otros', ''),
            'pat_enfermedades': data.get('pat_enfermedades', ''),
            'pat_medicamentos': data.get('pat_medicamentos', ''),
            'pat_alergias': data.get('pat_alergias', ''),
            'pat_oculares': data.get('pat_oculares', ''),
            'pat_cirugias': data.get('pat_cirugias', ''),
            'fecha_registro': datetime.now(),
            'id_medico': ObjectId(g.user['user_id'])
        }
        
        if existing:
            # Actualizar existente
            db['historia_clinica'].update_one(
                {'id_atencion': id_atencion, 'Id_exp': Id_exp},
                {'$set': historia_data}
            )
        else:
            # Insertar nueva
            historia_data['id_historia'] = get_next_sequence('historia_clinica_id')
            db['historia_clinica'].insert_one(historia_data)
        
        return jsonify({'message': 'Historia clínica guardada correctamente'}), 200
        
    except Exception as e:
        print(f"Error guardando historia clínica: {e}")
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/historia-clinica/<int:id_atencion>/<int:Id_exp>', methods=['GET'])
@token_required
def get_historia_clinica(id_atencion, Id_exp):
    """Obtiene la historia clínica del paciente"""
    try:
        db = get_db()
        
        historia = db['historia_clinica'].find_one({
            'id_atencion': id_atencion,
            'Id_exp': Id_exp
        })
        
        if not historia:
            return jsonify({}), 200
        
        return jsonify(serialize_doc(historia)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@medical_bp.route('/appointments/<int:id_atencion>/vital-signs', methods=['POST'])
@token_required
@role_required('admin', 'medico', 'enfermero')
def add_vital_signs(id_atencion):
    """Registra signos vitales"""
    data = request.get_json()
    data['id_medico'] = g.user['user_id']
    
    result = MedicalService.add_vital_signs(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al registrar signos vitales'}), 500
    
    return jsonify(result), 201

@medical_bp.route('/appointments/<int:id_atencion>/vital-signs', methods=['GET'])
@token_required
def get_vital_signs(id_atencion):
    signs = MedicalService.get_vital_signs(id_atencion)
    return jsonify(signs), 200


@medical_bp.route('/appointments/<int:id_atencion>/medical-notes', methods=['GET'])
@token_required
def get_medical_notes(id_atencion):
    """Obtiene notas médicas"""
    notes = MedicalService.get_medical_notes(id_atencion)
    return jsonify(notes), 200

@medical_bp.route('/appointments/<int:id_atencion>/medical-notes', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def add_medical_note(id_atencion):
    """Agrega nota médica"""
    data = request.get_json()
    data['id_medico'] = g.user['user_id']
    
    result = MedicalService.add_medical_note(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al agregar nota médica'}), 500
    
    return jsonify(result), 201


@medical_bp.route('/appointments/<int:id_atencion>/diagnosis', methods=['GET'])
@token_required
def get_diagnosis(id_atencion):
    """Obtiene el diagnóstico actual de una atención"""
    try:
        db = get_db()
        
        diagnosis = db['diagnosticos'].find_one(
            {'id_atencion': id_atencion},
            sort=[('fecha_registro', -1)]  # El más reciente
        )
        
        if not diagnosis:
            return jsonify({}), 200
        
        return jsonify(serialize_doc(diagnosis)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/appointments/<int:id_atencion>/diagnosis', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def add_diagnosis(id_atencion):
    """Agrega o actualiza diagnóstico"""
    try:
        db = get_db()
        data = request.get_json()
        
        # Verificar si ya existe diagnóstico para esta atención
        existing = db['diagnosticos'].find_one({'id_atencion': id_atencion})
        
        diagnosis_data = {
            'id_atencion': id_atencion,
            'diagnostico_principal': data.get('diagnostico_principal', ''),
            'diagnosticos_secundarios': data.get('diagnosticos_secundarios', ''),
            'observaciones': data.get('observaciones', ''),
            'fecha_registro': datetime.now(),
            'id_medico': ObjectId(g.user['user_id'])
        }
        
        if existing:
            # Actualizar diagnóstico existente (guardar historial primero)
            # Guardar versión anterior en historial
            history_data = {k: v for k, v in existing.items() if k != '_id'}
            history_data['id_diagnostico_original'] = existing['_id']
            history_data['fecha_modificacion'] = datetime.now()
            db['diagnosticos_historial'].insert_one(history_data)
            
            # Actualizar diagnóstico actual
            db['diagnosticos'].update_one(
                {'id_atencion': id_atencion},
                {'$set': diagnosis_data}
            )
        else:
            # Crear nuevo diagnóstico
            diagnosis_data['id_diagnostico'] = get_next_sequence('diagnosticos_id')
            db['diagnosticos'].insert_one(diagnosis_data)
        
        return jsonify({'message': 'Diagnóstico guardado correctamente'}), 200
        
    except Exception as e:
        print(f"Error guardando diagnóstico: {e}")
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/appointments/<int:id_atencion>/diagnosis/history', methods=['GET'])
@token_required
def get_diagnosis_history(id_atencion):
    """Obtiene el historial de diagnósticos"""
    try:
        db = get_db()
        
        # Obtener historial de modificaciones
        history = list(db['diagnosticos_historial'].find(
            {'id_atencion': id_atencion}
        ).sort('fecha_modificacion', -1))
        
        # También incluir el diagnóstico actual
        current = db['diagnosticos'].find_one({'id_atencion': id_atencion})
        
        result = []
        if current:
            current_copy = {k: v for k, v in current.items() if k != '_id'}
            current_copy['es_actual'] = True
            result.append(current_copy)
        
        for h in history:
            h_copy = {k: v for k, v in h.items() if k != '_id'}
            h_copy['es_actual'] = False
            result.append(h_copy)
        
        # Ordenar por fecha (más reciente primero)
        result.sort(key=lambda x: x.get('fecha_registro') or x.get('fecha_modificacion'), reverse=True)
        
        return jsonify([serialize_doc(r) for r in result]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@medical_bp.route('/appointments/<int:id_atencion>/prescriptions', methods=['GET'])
@token_required
def get_prescriptions(id_atencion):
    """Obtiene todas las recetas de una atención"""
    try:
        db = get_db()
        
        prescriptions = list(db['recetas'].find(
            {'id_atencion': id_atencion}
        ).sort('fecha_registro', -1))
        
        # Agregar nombre del médico
        for p in prescriptions:
            medico = db['users'].find_one({'_id': p.get('id_medico')})
            if medico:
                p['medico_nombre'] = medico.get('nombre', '') + ' ' + medico.get('papell', '')
        
        return jsonify([serialize_doc(p) for p in prescriptions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/appointments/<int:id_atencion>/prescriptions', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def add_prescription(id_atencion):
    """Agrega una receta médica"""
    try:
        db = get_db()
        data = request.get_json()
        
        prescription = {
            'id_receta': get_next_sequence('recetas_id'),
            'id_atencion': id_atencion,
            'medicamentos': data.get('medicamentos', []),
            'id_medico': ObjectId(g.user['user_id']),
            'fecha_registro': datetime.now()
        }
        
        db['recetas'].insert_one(prescription)
        
        return jsonify(serialize_doc(prescription)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

################################################################
############# enfermeria
###############################################################

@medical_bp.route('/appointments/<int:id_atencion>/nursing-notes', methods=['POST'])
@token_required
@role_required('admin', 'medico', 'enfermero')
def add_nursing_note(id_atencion):
    """
    Registra una nota de enfermería para un paciente
    """
    try:
        db = get_db()
        data = request.get_json()
        
        # Verificar que la atención existe
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return jsonify({'error': 'Atención no encontrada'}), 404
        
        # Crear la nota de enfermería
        nursing_note = {
            'id_nota': get_next_sequence('nursing_notes_id'),
            'id_atencion': id_atencion,
            'Id_exp': atencion['Id_exp'],
            'nota': data.get('nota_enfermeria', ''),
            'id_enfermero': ObjectId(g.user['user_id']),
            'fecha_registro': datetime.now()
        }
        
        db['nursing_notes'].insert_one(nursing_note)
        
        return jsonify({
            'message': 'Nota de enfermería guardada correctamente',
            'id_nota': nursing_note['id_nota']
        }), 201
        
    except Exception as e:
        print(f"Error en add_nursing_note: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/appointments/<int:id_atencion>/nursing-notes', methods=['GET'])
@token_required
@role_required('admin', 'medico', 'enfermero')
def get_nursing_notes(id_atencion):
    """
    Obtiene el historial de notas de enfermería de un paciente
    """
    try:
        db = get_db()
        
        pipeline = [
            {'$match': {'id_atencion': id_atencion}},
            {'$lookup': {
                'from': 'users',
                'localField': 'id_enfermero',
                'foreignField': '_id',
                'as': 'enfermero'
            }},
            {'$unwind': {'path': '$enfermero', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_nota': 1,
                'nota': 1,
                'fecha_registro': 1,
                'enfermero_nombre': {'$concat': [
                    {'$ifNull': ['$enfermero.nombre', '']}, ' ',
                    {'$ifNull': ['$enfermero.papell', '']}
                ]}
            }},
            {'$sort': {'fecha_registro': -1}}
        ]
        
        notes = list(db['nursing_notes'].aggregate(pipeline))
        
        return jsonify([serialize_doc(n) for n in notes]), 200
        
    except Exception as e:
        print(f"Error en get_nursing_notes: {e}")
        return jsonify({'error': str(e)}), 500
    
@medical_bp.route('/appointments/<int:id_atencion>/medications', methods=['POST'])
@token_required
@role_required('admin', 'medico', 'enfermero')
def add_medication(id_atencion):
    """
    Registra la administración de medicamentos por enfermería
    """
    try:
        db = get_db()
        data = request.get_json()
        
        # Verificar que la atención existe
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return jsonify({'error': 'Atención no encontrada'}), 404
        
        # Crear el registro de administración
        medication_record = {
            'id_registro': get_next_sequence('medications_registro_id'),
            'id_atencion': id_atencion,
            'Id_exp': atencion['Id_exp'],
            'medicamentos': data.get('medicamentos', []),
            'id_enfermero': ObjectId(g.user['user_id']),
            'fecha_registro': datetime.now()
        }
        
        db['medications'].insert_one(medication_record)
        
        return jsonify({
            'message': 'Administración de medicamentos registrada correctamente',
            'id_registro': medication_record['id_registro']
        }), 201
        
    except Exception as e:
        print(f"Error en add_medication: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@medical_bp.route('/appointments/<int:id_atencion>/medications', methods=['GET'])
@token_required
@role_required('admin', 'medico', 'enfermero')
def get_medications(id_atencion):
    """
    Obtiene el historial de administración de medicamentos
    """
    try:
        db = get_db()
        
        pipeline = [
            {'$match': {'id_atencion': id_atencion}},
            {'$lookup': {
                'from': 'users',
                'localField': 'id_enfermero',
                'foreignField': '_id',
                'as': 'enfermero'
            }},
            {'$unwind': {'path': '$enfermero', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_registro': 1,
                'medicamentos': 1,
                'fecha_registro': 1,
                'enfermero_nombre': {'$concat': [
                    {'$ifNull': ['$enfermero.nombre', '']}, ' ',
                    {'$ifNull': ['$enfermero.papell', '']}
                ]}
            }},
            {'$sort': {'fecha_registro': -1}}
        ]
        
        records = list(db['medications'].aggregate(pipeline))
        
        return jsonify([serialize_doc(r) for r in records]), 200
        
    except Exception as e:
        print(f"Error en get_medications: {e}")
        return jsonify({'error': str(e)}), 500