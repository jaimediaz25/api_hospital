import os
import json
import zipfile
from datetime import datetime
from utils.database import get_collection, get_db
import shutil

BACKUP_DIR = 'backups'

def realizar_backup(tipo='completa', formato='json', colecciones=None, comprimir=True):
    """Realiza backup de la base de datos"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{tipo}_{timestamp}"
    
    if comprimir:
        backup_path = os.path.join(BACKUP_DIR, f"{backup_name}.zip")
        zip_file = zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED)
    else:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        os.makedirs(backup_path, exist_ok=True)
    
    db = get_db()
    
    if not colecciones:
        colecciones = db.list_collection_names()
    
    for coleccion in colecciones:
        data = list(db[coleccion].find({}))
        
        if formato == 'json':
            # Convertir ObjectId a string
            for doc in data:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            json_data = json.dumps(data, default=str, ensure_ascii=False)
            
            if comprimir:
                zip_file.writestr(f"{coleccion}.json", json_data)
            else:
                with open(os.path.join(backup_path, f"{coleccion}.json"), 'w', encoding='utf-8') as f:
                    f.write(json_data)
    
    if comprimir:
        zip_file.close()
    
    return backup_path

def restaurar_backup(backup_file):
    """Restaura backup"""
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    db = get_db()
    
    if backup_file.endswith('.zip'):
        with zipfile.ZipFile(backup_path, 'r') as zip_file:
            temp_dir = 'temp_restore'
            zip_file.extractall(temp_dir)
            
            for file in os.listdir(temp_dir):
                if file.endswith('.json'):
                    coleccion = file.replace('.json', '')
                    with open(os.path.join(temp_dir, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    db[coleccion].drop()
                    if data:
                        db[coleccion].insert_many(data)
            
            shutil.rmtree(temp_dir)
    else:
        # Restaurar desde carpeta
        for file in os.listdir(backup_path):
            if file.endswith('.json'):
                coleccion = file.replace('.json', '')
                with open(os.path.join(backup_path, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                db[coleccion].drop()
                if data:
                    db[coleccion].insert_many(data)
    
    return True

def list_backups():
    """Lista backups disponibles"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for file in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, file)
        stat = os.stat(file_path)
        backups.append({
            'filename': file,
            'size': stat.st_size,
            'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return sorted(backups, key=lambda x: x['date'], reverse=True)

def limpiar_backups(keep=5):
    """Limpia backups antiguos"""
    backups = list_backups()
    for backup in backups[keep:]:
        os.remove(os.path.join(BACKUP_DIR, backup['filename']))

def check_db_health():
    """Verifica salud de la base de datos"""
    try:
        db = get_db()
        db.command('ping')
        return {'status': 'ok', 'message': 'Database connected'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def job_backup_auto(app):
    """Tarea programada para backup automático"""
    with app.app_context():
        realizar_backup(tipo='automatico', comprimir=True)
        limpiar_backups(10)