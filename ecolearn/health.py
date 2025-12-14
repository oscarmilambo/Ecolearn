# ecolearn/health.py - Health check endpoints for Render
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import time

def health_check(request):
    """
    Health check endpoint for Render deployment
    Checks database, cache, and basic application health
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check', 'test', 30)
        if cache.get('health_check') == 'test':
            health_status['checks']['cache'] = 'healthy'
        else:
            health_status['checks']['cache'] = 'unhealthy: cache not working'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Redis check (for channels)
    try:
        if hasattr(settings, 'REDIS_URL'):
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status['checks']['redis'] = 'healthy'
        else:
            health_status['checks']['redis'] = 'not configured'
    except Exception as e:
        health_status['checks']['redis'] = f'unhealthy: {str(e)}'
        # Don't mark overall status as unhealthy for Redis issues
    
    # Application check
    health_status['checks']['application'] = 'healthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

def readiness_check(request):
    """
    Readiness check - ensures app is ready to serve traffic
    """
    try:
        # Check if migrations are applied
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            return JsonResponse({
                'status': 'not_ready',
                'reason': 'pending_migrations'
            }, status=503)
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': time.time()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'reason': str(e)
        }, status=503)