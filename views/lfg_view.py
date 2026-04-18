from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_lfg(session, player_names_with_roles):
    """Renders a clean and professional LFG squad gathering message."""
    player_count = len(session.players)
    max_p = session.max_players
    status_text = "Mencari Tim" if session.status == "open" else "Sesi Berjalan"
    
    tipe_str = "Hazard Ops" if session.lfg_type == "hazard" else "Havoc Warfare"
    icon = "☣️" if session.lfg_type == "hazard" else "⚔️"
    
    text = get_header(f"{tipe_str}", icon)
    
    text += f"Status: <b>{status_text}</b>\n"
    text += f"Operator: <b>{player_count} / {max_p}</b>\n"
    text += get_divider()
    
    text += "📋 <b>Manifest Skuad:</b>\n"
    for i, name_role in enumerate(player_names_with_roles):
        leader_tag = " 👑" if i == 0 else ""
        text += f"{i+1}. {name_role}{leader_tag}\n"
            
    for i in range(player_count, max_p):
        text += f"{i+1}. <i>(Kosong)</i>\n"
    
    text += get_divider()
    
    if session.status == "open":
        text += "Silakan klik tombol di bawah untuk bergabung."
    else:
        text += "Sesi pendaftaran telah ditutup."

    text += "\n" + get_footer(f"Session ID: {session.id.upper()}")
    
    return text
