from utils.style_utils import get_header, get_footer, format_field, progress_bar

def render_profile(user_dto, badges=None):
    """Symbolic minimalist profile card."""
    current_lvl_xp = (user_dto.level - 1)**2 * 25
    next_lvl_xp = user_dto.level**2 * 25
    xp_in_level = user_dto.xp - current_lvl_xp
    xp_required = next_lvl_xp - current_lvl_xp
    
    xp_bar = progress_bar(xp_in_level, xp_required)
    badge_text = ", ".join(badges) if badges else "Kosong"
    
    text = get_header("Profil Personel", "◇")
    
    text += format_field("CALLSIGN", user_dto.ign, "⬢")
    text += format_field("SPECIALIST", user_dto.role or "N/A", "⬢")
    text += "\n"
    
    text += f"<b>LEVEL {user_dto.level}</b>\n"
    text += f"{xp_bar} <code>({user_dto.xp} XP)</code>\n\n"
    
    text += format_field("REPUTASI", str(user_dto.rep_points), "‣")
    text += format_field("SALDO", f"{user_dto.balance} Koin", "‣")
    text += format_field("MABAR", f"{user_dto.mabar_score} Sesi", "‣")
    text += "\n"
    
    text += f"<b>BADGES</b>: <i>{badge_text}</i>"
    
    return text
