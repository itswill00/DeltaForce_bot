from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_dashboard(user_dto, is_reg, briefing=None, page=1):
    """Renders the high-impact tactical dashboard."""
    text = get_header("TACTICAL COMMAND HUB", "📱")
    
    if not is_reg:
        text += (
            "🚀 <b>IMMEDIATE ACTION REQUIRED</b>\n"
            "Unauthorized operator detected. Please initialize your profile.\n\n"
            "<b>STEPS:</b>\n"
            "1️⃣ Register IGN (In-Game Name)\n"
            "2️⃣ Select Specialist Role\n"
            "3️⃣ Access Tactical Intel"
        )
    else:
        if briefing:
            text += f"📬 <b>INTELLIGENCE BRIEFING:</b>\n<i>\"{briefing}\"</i>\n\n"
        
        text += format_field("OPERATOR", user_dto.ign, "👤")
        text += format_field("LEVEL", str(user_dto.level), "🏅")
        text += format_field("XP TOTAL", str(user_dto.xp), "✨")
        
        text += get_divider()
        if page == 1:
            text += "<i>Select deployment sector or intelligence database below:</i>"
        else:
            text += "<i>Community features and personnel leaderboard:</i>"
            
    text += get_footer(f"Sector: {'Primary' if page==1 else 'Secondary'}")
    return text
