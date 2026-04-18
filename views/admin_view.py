from utils.style_utils import get_header, format_field, get_divider

def render_admin_dashboard(stats):
    """Owner's high-level community statistics view."""
    text = get_header("Admin Command Center", "◈")
    
    text += "📊 <b>GLOBAL STATISTICS</b>\n"
    text += format_field("TOTAL USER", str(stats['total_users']), "👥")
    text += format_field("AVG LEVEL", str(stats['avg_level']), "🏅")
    text += format_field("TOTAL COIN", str(stats['total_coins']), "💰")
    text += get_divider()
    
    text += "🎯 <b>ROLE DISTRIBUTION</b>\n"
    for role, count in stats['roles'].items():
        text += f"‣ <b>{role:10}</b>: <code>{count}</code>\n"
        
    text += "\n<i>Gunakan menu di bawah untuk manajemen personel.</i>"
    from utils.style_utils import force_height
    return force_height(text, 12)

def render_admin_user_detail(user_dto):
    """Detailed user view for admin management."""
    text = get_header("Personnel Audit", "🔍")
    
    text += format_field("CALLSIGN", user_dto.ign, "🏷️")
    text += format_field("USER ID", str(user_dto.id), "🆔")
    text += format_field("ROLE", user_dto.role or "N/A", "🎯")
    text += get_divider()
    
    text += format_field("LEVEL", str(user_dto.level), "🏅")
    text += format_field("XP", str(user_dto.xp), "✨")
    text += format_field("COINS", str(user_dto.balance), "💰")
    text += format_field("REP", str(user_dto.rep_points), "⭐")
    
    text += get_divider()
    text += f"🕒 <b>Last Active</b>: <code>{user_dto.last_login or 'Unknown'}</code>\n"
    text += f"🛡️ <b>Is Admin</b>: <code>{'YES' if user_dto.is_admin else 'NO'}</code>"
    
    from utils.style_utils import force_height
    return force_height(text, 12)
