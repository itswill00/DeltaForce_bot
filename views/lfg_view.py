from utils.style_utils import get_header, get_footer

def render_lfg(session, player_names_with_roles):
    """Compact minimalist LFG manifest."""
    tipe_str = "Hazard Ops" if session.lfg_type == "hazard" else "Havoc Warfare"
    icon = "☣️" if session.lfg_type == "hazard" else "⚔️"
    
    text = get_header(f"Mabar {tipe_str}", icon)
    
    text += f"<b>Kuota</b>: {len(session.players)}/{session.max_players}\n"
    text += f"<b>Status</b>: {'Pendaftaran Terbuka' if session.status == 'open' else 'Sesi Dimulai'}\n\n"
    
    for i, name_role in enumerate(player_names_with_roles):
        is_host = " 👑" if i == 0 else ""
        text += f"{i+1}. {name_role}{is_host}\n"
            
    for i in range(len(session.players), session.max_players):
        text += f"{i+1}. <i>(Kosong)</i>\n"
    
    if session.status == "open":
        text += "\nKlik ➕ Gabung untuk reservasi slot."

    return text
