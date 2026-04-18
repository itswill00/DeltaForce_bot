from utils.style_utils import get_header, get_footer, format_field, progress_bar, get_divider
import math

def render_profile(user_dto, badges=None):
    """Renders a clean and mature operator profile card."""
    current_lvl_xp = (user_dto.level - 1)**2 * 25
    next_lvl_xp = user_dto.level**2 * 25
    xp_in_level = user_dto.xp - current_lvl_xp
    xp_required = next_lvl_xp - current_lvl_xp
    
    xp_bar = progress_bar(xp_in_level, xp_required)
    badge_text = ", ".join(badges) if badges else "Belum ada badge"
    
    text = get_header("Profil Personel", "👤")
    text += f"Callsign: <b>{user_dto.ign}</b>\n"
    text += f"Role: <code>{user_dto.role or 'Belum dipilih'}</code>\n"
    text += get_divider()
    
    text += f"🎖 <b>Level: {user_dto.level}</b>\n"
    text += f"Progres XP: {xp_bar}\n"
    text += f"<i>({user_dto.xp} XP terakumulasi)</i>\n"
    text += get_divider()
    
    text += f"⭐ Reputasi: <b>{user_dto.rep_points}</b>\n"
    text += f"💰 Saldo: <b>{user_dto.balance} Koin</b>\n"
    text += f"⚔️ Total Mabar: <b>{user_dto.mabar_score} Sesi</b>\n"
    text += get_divider()
    
    text += f"🏅 <b>Badges:</b>\n<i>{badge_text}</i>\n"
    text += get_footer()
    
    return text
