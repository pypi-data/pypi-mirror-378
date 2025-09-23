import requests
from datetime import datetime

SUPABASE_URL = "https://dyvlkxavnwzbjfulvcxj.supabase.co/functions/v1/validate-license"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR5dmxreGF2bnd6YmpmdWx2Y3hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1OTUzMzAsImV4cCI6MjA3NDE3MTMzMH0.kiM_hHisAyg2TpweqHG9EbXxVJ3QywEFvDalr5otvi0"

class LicenseValidator:
    @staticmethod
    def validate_license(tier, license_key):
        if tier == 'community':
            return True
        
        try:
            # Intenta validación remota
            response = requests.post(
                f"https://{SUPABASE_URL}/functions/v1/validate-license",
                json={'license_key': license_key},
                headers={'Authorization': f'Bearer {SUPABASE_ANON_KEY}'},
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('valid', False)
        except:
            pass
        
        # Fallback offline
        try:
            parts = license_key.split('-')
            year, month, day = int(parts[1]), int(parts[2]), int(parts[3])
            expiry = datetime(year, month, day)
            return datetime.now() <= expiry
        except:
            return False