from supabase import create_client

SUPABASE_URL = "https://uajcmeseaipjrplvndrp.supabase.co"
SUPABASE_KEY = "sb_publishable_qYT6mm4kXCDujn33uJN8oA_ZbO9ux6h"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)