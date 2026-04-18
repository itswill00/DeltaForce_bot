from utils.style_utils import get_header, get_footer, format_field, progress_bar

def render_profile(user_dto, equipped_badge_name=None):
    """Refined symbolic profile card for maximum clarity."""
    current_lvl_xp = (user_dto.level - 1)**2 * 25
    next_lvl_xp = user_dto.level**2 * 25
    xp_in_level = user_dto.xp - current_lvl_xp
    xp_required = next_lvl_xp - current_lvl_xp
    
    xp_bar = progress_bar(xp_in_level, xp_required)
    badge_view = f"🎖 <b>{equipped_badge_name.upper()}</b>" if equipped_badge_name else "<i>No Badge Equipped</i>"
    
    text = get_header("Profil Personel", "◇")
    
    text += f"🏷 <b>{user_dto.ign.upper()}</b>\n"
    text += f"🎯 <code>{user_dto.role or 'RECRUIT'}</code>\n"
    text += f"{badge_view}\n\n"
    
    text += f"🏅 <b>LEVEL {user_dto.level}</b>\n"
    text += f"{xp_bar} <code>{user_dto.xp} XP</code>\n\n"
    
    text += format_field("REPUTASI", str(user_dto.rep_points), "‣")
    text += format_field("SALDO", f"{user_dto.balance} Koin", "‣")
    text += format_field("MABAR", f"{user_dto.mabar_score} Sesi", "‣")
    
    from utils.style_utils import force_height
    return force_height(text, 12)
