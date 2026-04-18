from utils.style_utils import get_header, get_footer, format_field

def render_dashboard(user_dto, is_reg, briefing=None, page=1):
    """Symbolic minimalist dashboard."""
    text = get_header("Delta Force Hub", "◈")
    
    if not is_reg:
        text += (
            "Halo! Silakan daftarkan Call-sign kamu untuk "
            "mengakses fitur mabar dan statistik komunitas.\n\n"
            "<b>Pendaftaran:</b>\n"
            "1. Masukkan IGN\n"
            "2. Pilih Role Spesialisasi"
        )
    else:
        if briefing:
            text += f"⌗ <i>{briefing}</i>\n\n"
        
        text += format_field("OPERATOR", user_dto.ign, "◇")
        text += format_field("LEVEL", str(user_dto.level), "◇")
        text += format_field("XP", str(user_dto.xp), "◇")
        
        text += "\nSilakan pilih menu di bawah:"
            
    text += get_footer(f"Sektor {page}/2")
    
    from utils.style_utils import force_height
    return force_height(text, 12)
