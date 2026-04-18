from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_dashboard(user_dto, is_reg, briefing=None, page=1):
    """Renders a clean, professional dashboard."""
    text = get_header("Delta Force Indonesia", "🏠")
    
    if not is_reg:
        text += (
            "<b>Halo! Selamat bergabung di komunitas.</b> 👋\n\n"
            "Daftarkan ID Operator kamu agar statistik mabar, level, dan badge "
            "kamu bisa tercatat secara permanen.\n\n"
            "<b>Langkah awal:</b>\n"
            "1️⃣ Masukkan nama in-game (IGN)\n"
            "2️⃣ Pilih role spesialisasi kamu"
        )
    else:
        if briefing:
            text += f"📢 <b>Info Hari Ini:</b>\n<i>\"{briefing}\"</i>\n\n"
        
        text += f"Halo, <b>{user_dto.ign}</b>! Siap mabar lagi hari ini?\n"
        text += f"Level kamu: <b>{user_dto.level}</b> | Total XP: <b>{user_dto.xp}</b>\n"
        
        text += get_divider()
        if page == 1:
            text += "Silakan pilih menu utama di bawah:"
        else:
            text += "Fitur komunitas dan peringkat operator:"
            
    text += "\n" + get_footer()
    return text
