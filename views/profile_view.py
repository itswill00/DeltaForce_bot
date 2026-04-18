from utils.style_utils import get_header, get_footer, format_field, progress_bar, get_divider
import math

def render_profile(user_dto, badges=None):
    """Renders an enterprise-grade tactical profile card."""
    # XP logic for progress bar
    # Next level XP = (level)^2 * 25
    current_lvl_xp = (user_dto.level - 1)**2 * 25
    next_lvl_xp = user_dto.level**2 * 25
    xp_in_level = user_dto.xp - current_lvl_xp
    xp_required = next_lvl_xp - current_lvl_xp
    
    xp_bar = progress_bar(xp_in_level, xp_required)
    badge_text = ", ".join(badges) if badges else "None"
    
    text = get_header("OPERATOR DOSSIER", "👤")
    text += format_field("CALLSIGN", user_dto.ign, "🏷️")
    text += format_field("SPECIALIST", user_dto.role or "Unassigned", "🎯")
    text += get_divider()
    
    text += format_field("LEVEL OPS", str(user_dto.level), "🏅")
    text += f"✨ <b>XP PROGRESS</b>\n{xp_bar}\n"
    text += format_field("TOTAL XP", str(user_dto.xp), "📊")
    text += get_divider()
    
    text += format_field("REPUTATION", f"⭐ {user_dto.rep_points}", "🛡️")
    text += format_field("BALANCE", f"💰 {user_dto.balance}", "🏦")
    text += format_field("MABAR SESI", str(user_dto.mabar_score), "⚔️")
    text += get_divider()
    
    text += f"🎖️ <b>HONORARY BADGES:</b>\n<code>{badge_text}</code>\n"
    text += get_footer("Tactical Profile System v4.0")
    
    return text
