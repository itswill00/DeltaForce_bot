from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_operator_list():
    """Renders the operator database main screen."""
    text = get_header("OPERATOR DATABASE", "🚑")
    text += "Accessing TiMi-Global Dossiers...\n"
    text += "Select specialist for tactical capability assessment:"
    text += "\n" + get_footer("Dossier v1.0")
    return text

def render_operator_detail(op):
    """Renders detailed operator tactical dossier."""
    text = get_header(f"DOSSIER: {op.get('name', 'N/A').upper()}", "👤")
    
    text += format_field("SPECIALIST", op.get("role", "N/A"), "🎯")
    text += get_divider()
    text += f"<i>\"{op.get('description', 'No description available.')}\"</i>\n\n"
    
    text += "🛠️ <b>TACTICAL ABILITIES:</b>\n"
    text += f"• <b>ACTIVE :</b> <code>{op.get('active_skill', 'N/A')}</code>\n"
    text += f"• <b>PASSIVE:</b> <code>{op.get('passive_skill', 'N/A')}</code>\n"
    
    text += get_divider()
    text += get_footer("Access level: CLASSIFIED")
    return text
