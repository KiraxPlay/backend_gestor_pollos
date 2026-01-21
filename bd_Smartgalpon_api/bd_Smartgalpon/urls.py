from django.contrib import admin
from django.urls import path, include
import psycopg2
import os

#para pruebas

def test_stored_procedures(request):
    """Test específico para procedimientos almacenados"""
    try:
        # Conectar directamente a Supabase
        conn = psycopg2.connect(
            host='db.fmwqtpzzanzrtfvldlhz.supabase.co',
            port=5432,
            database='postgres',
            user='postgres',
            password='PeXm3GiXZYRDkNzv',
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        
        # 1. Verificar que podemos ejecutar SQL
        cursor.execute("SELECT 1 as test")
        test1 = cursor.fetchone()[0]
        
        # 2. Verificar tablas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            LIMIT 5
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # 3. Verificar procedimientos almacenados
        cursor.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_type = 'FUNCTION'
            LIMIT 5
        """)
        functions = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return JsonResponse({
            'success': True,
            'connection': '✅ Conectado a Supabase',
            'test_query': test1,
            'tables_found': tables,
            'functions_found': functions,
            'message': '✅ Procedimientos almacenados accesibles'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'connection_test': '❌ No se puede conectar a Supabase',
            'next_steps': [
                '1. Verificar Network Restrictions en Supabase',
                '2. Probar con sslmode=disable temporalmente',
                '3. Contactar a Render support sobre puerto 5432'
            ]
        }, status=500)




urlpatterns = [
    path('test-procedimientos' , test_stored_procedures, name='test-procedures'),
    path('admin/', admin.site.urls),
    path('api/ponedoras/', include('api.urlsPonedoras')),
    path('api/', include('api.urls'))
]
