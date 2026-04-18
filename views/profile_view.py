from utils.style_utils import get_header, get_footer, format_field, progress_bar

def render_profile(user_dto, equipped_badge_name=None):
    """Symbolic minimalist profile card with equipped badge."""
    current_lvl_xp = (user_dto.level - 1)**2 * 25
    next_lvl_xp = user_dto.level**2 * 25
    xp_in_level = user_dto.xp - current_lvl_xp
    xp_required = next_lvl_xp - current_lvl_xp
    
    xp_bar = progress_bar(xp_in_level, xp_required)
    
    # Menampilkan badge utama
    badge_display = f"🎖️ <b>{equipped_badge_name}</b>" if equipped_badge_name else "<i>Belum memasang badge</i>"
    
    text = get_header("Profil Personel", "◇")
    
    text += format_field("CALLSIGN", user_dto.ign, "⬢")
    text += format_field("SPECIALIST", user_dto.role or "N/A", "⬢")
    text += f"{badge_display}\n\n"
    
    text += f"<b>LEVEL {user_dto.level}</b>\n"
    text += f"{xp_bar} <code>({user_dto.xp} XP)</code>\n\n"
    
    text += format_field("REPUTASI", str(user_dto.rep_points), "‣")
    text += format_field("SALDO", f"{user_dto.balance} Koin", "‣")
    text += format_field("MABAR", f"{user_dto.mabar_score} Sesi", "‣")
    
    from utils.style_utils import force_height
    return force_height(text, 12)
