from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_lfg(session, player_names_with_roles):
    """Renders a friendly LFG squad gathering message."""
    player_count = len(session.players)
    max_p = session.max_players
    status_text = "Mencari Anggota" if session.status == "open" else "Sudah Deploy"
    
    tipe_str = "Hazard Operation" if session.lfg_type == "hazard" else "Havoc Warfare"
    icon = "☣️" if session.lfg_type == "hazard" else "⚔️"
    
    text = get_header(f"Mabar {tipe_str}", icon)
    
    text += f"Status Skuad: <b>{status_text}</b>\n"
    text += f"Kuota: <b>{player_count} dari {max_p} Operator</b>\n"
    text += get_divider()
    
    text += "📋 <b>Daftar Personel:</b>\n"
    for i, name_role in enumerate(player_names_with_roles):
        leader_tag = " 👑 <b>(Leader)</b>" if i == 0 else ""
        text += f"{i+1}. {name_role}{leader_tag}\n"
            
    for i in range(player_count, max_p):
        text += f"{i+1}. <i>(Masih Kosong)</i>\n"
    
    text += get_divider()
    
    if session.status == "open":
        text += "Yuk, buruan gabung sebelum skuadnya penuh!"
    else:
        text += "Sesi sudah ditutup, tim sedang bersiap bertempur."

    text += "\n" + get_footer(f"ID Sesi: {session.id.upper()}")
    
    return text
