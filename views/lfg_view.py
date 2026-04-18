from utils.style_utils import get_header, get_footer, get_status_tag

def render_lfg(session, player_names_with_roles):
    """Refined minimalist LFG for high-scale scannability."""
    tipe_str = "Hazard Ops" if session.lfg_type == "hazard" else "Havoc Warfare"
    
    # High-impact status line
    status_label = "Mencari Tim" if session.status == 'open' else "Sesi Berjalan"
    status_view = get_status_tag(session.status == 'open', status_label)
    
    text = get_header(f"{tipe_str}", "▣")
    
    text += f"{status_view}\n"
    text += f"📊 <b>Kuota</b>: <code>{len(session.players)}/{session.max_players}</code>\n\n"
    
    for i, name_role in enumerate(player_names_with_roles):
        is_host = " ❖" if i == 0 else ""
        text += f"<code>{i+1:02}</code>. {name_role}{is_host}\n"
            
    for i in range(len(session.players), session.max_players):
        text += f"<code>{i+1}</code>. <i>(Kosong)</i>\n"
    
    if session.status == "open":
        text += "\nKlik ⬢ GABUNG untuk reservasi slot."

    from utils.style_utils import force_height
    return force_height(text, 12)
