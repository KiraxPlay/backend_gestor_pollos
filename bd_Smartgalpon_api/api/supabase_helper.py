import os
from supabase import create_client, Client

class SupabaseSimple:
    """Versión minimalista para REST API"""
    
    def __init__(self):
        self.url = os.environ.get('SUPABASE_URL')
        self.key = os.environ.get('SUPABASE_SERVICE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Faltan variables de entorno SUPABASE_URL o SUPABASE_SERVICE_KEY")
        
        self.client = create_client(self.url, self.key)
    
    def rpc(self, procedure: str, params: dict = None):
        """Ejecutar procedimiento almacenado"""
        try:
            return self.client.rpc(procedure, params or {}).execute()
        except Exception as e:
            print(f"Error RPC {procedure}: {e}")
            raise
    
    def from_table(self, table: str):
        """Acceder a tabla"""
        return self.client.table(table)

# Instancia global
db = SupabaseSimple()
