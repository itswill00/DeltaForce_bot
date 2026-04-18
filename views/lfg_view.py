from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_lfg(session, player_names_with_roles):
    """Renders an enterprise-grade tactical LFG message."""
    player_count = len(session.players)
    max_p = session.max_players
    status_text = "🔵 ACTIVE" if session.status == "open" else "🛡️ DEPLOYED"
    
    tipe_str = "HAZARD OPERATION" if session.lfg_type == "hazard" else "HAVOC WARFARE"
    icon = "☣️" if session.lfg_type == "hazard" else "⚔️"
    
    text = get_header(f"DEPLOYMENT ORDER #{session.id.upper()}", icon)
    
    text += format_field("OPERATION", tipe_str, "🌐")
    text += format_field("STATUS", status_text, "📡")
    text += format_field("QUOTA", f"{player_count}/{max_p} OPERATORS", "👥")
    text += get_divider()
    
    text += "📋 <b>SQUAD MANIFEST:</b>\n"
    for i, name_role in enumerate(player_names_with_roles):
        is_host = " <b>[LEADER]</b>" if i == 0 else ""
        text += f"<code>{i+1:02}</code>. {name_role}{is_host}\n"
            
    for i in range(player_count, max_p):
        text += f"<code>{i+1:02}</code>. [ 🔓 SLOT AVAILABLE ]\n"
    
    text += get_divider()
    
    if session.status == "open":
        text += "<i>⏳ Awaiting full squad authorization...</i>\n"
    else:
        text += "<i>🚀 Unit deployed to active combat area.</i>\n"

    text += get_footer(f"LFG Session ID: {session.id.upper()}")
    
    return text
