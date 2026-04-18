from utils.style_utils import get_header, format_field

def render_operator_list():
    """Compact operator database list."""
    return get_header("Database Operator", "🚑") + "Pilih personel untuk melihat profil taktis:"

def render_operator_detail(op):
    """Compact operator dossier."""
    text = get_header(f"Operator: {op.get('name', 'N/A')}", "👤")
    
    text += format_field("SPECIALIST", op.get("role", "N/A"))
    text += f"\n<i>\"{op.get('description', 'N/A')}\"</i>\n\n"
    
    text += f"<b>Skill Aktif</b>: <code>{op.get('active_skill', 'N/A')}</code>\n"
    text += f"<b>Skill Pasif</b>: <code>{op.get('passive_skill', 'N/A')}</code>"
    
    return text
