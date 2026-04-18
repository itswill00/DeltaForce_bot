from utils.style_utils import get_header, get_footer

def render_lfg(session, player_names_with_roles):
    """Symbolic minimalist LFG manifest."""
    tipe_str = "Hazard Ops" if session.lfg_type == "hazard" else "Havoc Warfare"
    
    text = get_header(f"{tipe_str}", "▣")
    
    text += f"<b>Kuota</b>: {len(session.players)}/{session.max_players}\n"
    text += f"<b>Status</b>: {'Pendaftaran Terbuka' if session.status == 'open' else 'Sesi Dimulai'}\n\n"
    
    for i, name_role in enumerate(player_names_with_roles):
        leader_tag = " ❖" if i == 0 else ""
        text += f"<code>{i+1}</code>. {name_role}{leader_tag}\n"
            
    for i in range(len(session.players), session.max_players):
        text += f"<code>{i+1}</code>. <i>(Kosong)</i>\n"
    
    if session.status == "open":
        text += "\nKlik ⬢ GABUNG untuk reservasi slot."

    return text
