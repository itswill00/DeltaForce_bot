from utils.style_utils import get_header, get_footer, format_field, get_divider

def render_dashboard(user_dto, is_reg, briefing=None, page=1):
    """Renders a more human, community-focused dashboard."""
    text = get_header("Markas Besar Delta Force", "🏠")
    
    if not is_reg:
        text += (
            "<b>Selamat Datang, Operator!</b> 👋\n\n"
            "Senang melihatmu di sini. Biar bisa akses fitur mabar, intel, dan statistik, "
            "yuk daftarkan dirimu dulu ke komunitas.\n\n"
            "<b>Caranya gampang banget:</b>\n"
            "1️⃣ Klik tombol <b>Daftar Sekarang</b>\n"
            "2️⃣ Masukkan nama in-game (IGN) kamu\n"
            "3️⃣ Pilih role spesialisasi andalanmu"
        )
    else:
        if briefing:
            text += f"📬 <b>Kabar Hari Ini:</b>\n<i>\"{briefing}\"</i>\n\n"
        
        text += f"Halo, <b>{user_dto.ign}</b>! Siap bertugas kembali?\n"
        text += f"Saat ini kamu berada di <b>Level {user_dto.level}</b> dengan total <b>{user_dto.xp} XP</b>.\n"
        
        text += get_divider()
        if page == 1:
            text += "Mau ngapain kita hari ini? Pilih menunya di bawah ya:"
        else:
            text += "Lihat siapa yang paling jago atau cek bursa item di sini:"
            
    text += "\n" + get_footer(f"Halaman {page}/2")
    return text
