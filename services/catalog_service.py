from utils.database import get_collection, serialize_doc, get_next_sequence

class CatalogService:
    # ==================== SERVICIOS ====================
    @staticmethod
    def get_services():
        """Obtiene todos los servicios"""
        collection = get_collection('cat_servicios')
        
        pipeline = [
            {'$lookup': {
                'from': 'service_type',
                'localField': 'tipo',
                'foreignField': 'ser_type_id',
                'as': 'tipo_info'
            }},
            {'$unwind': {'path': '$tipo_info', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_serv': 1,
                'serv_cve': 1,
                'serv_desc': 1,
                'serv_costo': 1,
                'serv_umed': 1,
                'serv_activo': 1,
                'tipo': 1,
                'tipo_desc': '$tipo_info.ser_type_desc'
            }},
            {'$sort': {'id_serv': 1}}
        ]
        
        services = list(collection.aggregate(pipeline))
        return [serialize_doc(s) for s in services]
    
    @staticmethod
    def create_service(data):
        """Crea un nuevo servicio"""
        collection = get_collection('cat_servicios')
        
        # Verificar si ya existe la clave
        existing = collection.find_one({'serv_cve': data['serv_cve']})
        if existing:
            return None, 'Ya existe un servicio con esa clave'
        
        id_serv = get_next_sequence('cat_servicios_id_serv')
        
        service = {
            'id_serv': id_serv,
            'serv_cve': data['serv_cve'],
            'serv_desc': data['serv_desc'],
            'serv_costo': float(data['serv_costo']),
            'serv_costo2': float(data.get('serv_costo2', 0)),
            'serv_costo3': float(data.get('serv_costo3', 0)),
            'serv_costo4': float(data.get('serv_costo4', 0)),
            'serv_costo5': float(data.get('serv_costo5', 0)),
            'serv_costo6': float(data.get('serv_costo6', 0)),
            'serv_costo7': float(data.get('serv_costo7', 0)),
            'serv_costo8': float(data.get('serv_costo8', 0)),
            'serv_umed': data.get('serv_umed', ''),
            'serv_activo': 'SI',
            'tipo': int(data['tipo']),
            'proveedor': data.get('proveedor', ''),
            'grupo': data.get('grupo', ''),
            'codigo_sat': data.get('codigo_sat', ''),
            'c_cveuni': data.get('c_cveuni', ''),
            'c_nombre': 'SERVICIO',
            'iva': float(data.get('iva', 16)) / 100
        }
        
        collection.insert_one(service)
        return serialize_doc(service), None
    
    @staticmethod
    def update_service(id_serv, data):
        """Actualiza un servicio"""
        collection = get_collection('cat_servicios')
        
        update_data = {}
        allowed_fields = ['serv_cve', 'serv_desc', 'serv_costo', 'serv_costo2', 
                         'serv_costo3', 'serv_costo4', 'serv_costo5', 'serv_costo6',
                         'serv_costo7', 'serv_costo8', 'serv_umed', 'tipo', 
                         'proveedor', 'grupo', 'codigo_sat', 'c_cveuni', 'iva']
        
        for field in allowed_fields:
            if field in data:
                if field.startswith('serv_costo') or field == 'iva':
                    update_data[field] = float(data[field])
                elif field == 'tipo':
                    update_data[field] = int(data[field])
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return None
        
        result = collection.update_one(
            {'id_serv': id_serv},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return CatalogService.get_services()
    
    @staticmethod
    def delete_service(id_serv):
        """Elimina un servicio"""
        collection = get_collection('cat_servicios')
        
        # Verificar si está siendo usado en alguna cuenta
        db = collection.database
        used = db['cuenta_paciente'].find_one({'id_serv': id_serv})
        
        if used:
            return False
        
        result = collection.delete_one({'id_serv': id_serv})
        return result.deleted_count > 0
    
    # ==================== DIAGNÓSTICOS ====================
    @staticmethod
    def get_diagnostics():
        """Obtiene todos los diagnósticos"""
        collection = get_collection('cat_diag')
        
        diagnostics = list(collection.find({}, {
            'id_diag': 1,
            'diag': 1,
            'id_cie10': 1
        }).sort('id_diag', 1))
        
        return [serialize_doc(d) for d in diagnostics]
    
    @staticmethod
    def create_diagnostic(data):
        """Crea un nuevo diagnóstico"""
        collection = get_collection('cat_diag')
        
        id_diag = get_next_sequence('cat_diag_id_diag')
        
        diagnostic = {
            'id_diag': id_diag,
            'diag': data['diag'],
            'id_cie10': data['id_cie10']
        }
        
        collection.insert_one(diagnostic)
        return serialize_doc(diagnostic), None
    
    @staticmethod
    def update_diagnostic(id_diag, data):
        """Actualiza un diagnóstico"""
        collection = get_collection('cat_diag')
        
        update_data = {}
        if 'diag' in data:
            update_data['diag'] = data['diag']
        if 'id_cie10' in data:
            update_data['id_cie10'] = data['id_cie10']
        
        if not update_data:
            return None
        
        result = collection.update_one(
            {'id_diag': id_diag},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return CatalogService.get_diagnostics()
    
    @staticmethod
    def delete_diagnostic(id_diag):
        """Elimina un diagnóstico"""
        collection = get_collection('cat_diag')
        
        result = collection.delete_one({'id_diag': id_diag})
        return result.deleted_count > 0