from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit

scheduler = None

def init_scheduler(app):
    """Inicializa el scheduler"""
    global scheduler
    
    if scheduler is not None:
        return scheduler
    
    scheduler = BackgroundScheduler()
    
    # Backup diario a las 2 AM
    @scheduler.scheduled_job(CronTrigger(hour=2, minute=0))
    def daily_backup():
        with app.app_context():
            from utils.backups import realizar_backup, limpiar_backups
            realizar_backup(tipo='diario', comprimir=True)
            limpiar_backups(30)  # Mantener 30 backups
    
    # Limpieza de logs cada semana
    @scheduler.scheduled_job(CronTrigger(day_of_week='sun', hour=3, minute=0))
    def clean_old_logs():
        with app.app_context():
            from utils.database import get_collection
            from datetime import timedelta
            
            logs = get_collection('logs')
            cutoff_date = datetime.now() - timedelta(days=90)
            result = logs.delete_many({'fecha': {'$lt': cutoff_date}})
            print(f"Eliminados {result.deleted_count} logs antiguos")
    
    scheduler.start()
    
    # Detener scheduler al salir
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler

def add_job(func, trigger, **kwargs):
    """Agrega un trabajo al scheduler"""
    if scheduler:
        return scheduler.add_job(func, trigger, **kwargs)
    return None

def get_scheduler():
    """Retorna el scheduler actual"""
    return scheduler