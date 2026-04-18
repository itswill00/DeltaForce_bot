import json
import os
from aiogram import Router, types, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from services.user_service import UserService
from utils.style_utils import get_header

router = Router()

# Load map data once for inline use
MAP_DATA_PATH = "data/maps.json"
MAP_DB = {}
if os.path.exists(MAP_DATA_PATH):
    with open(MAP_DATA_PATH, "r", encoding="utf-8") as f:
        MAP_DB = json.load(f)

@router.inline_query()
async def inline_handler(inline_query: InlineQuery, user_service: UserService):
    query = inline_query.query.strip().lower()
    results = []

    # 1. Profile Search (ign [name])
    if query.startswith("ign "):
        search_name = query[4:].strip()
        all_users = await user_service.get_all_users()
        
        matches = []
        for uid, user in all_users.items():
            if search_name in user.ign.lower():
                matches.append(user)
        
        for i, user in enumerate(matches[:5]):
            text = get_header("KARTU PROFIL OPERATOR", "👤")
            text += (
                f"<b>IGN:</b> <code>{user.ign}</code>\n"
                f"<b>ROLE:</b> {user.role or 'N/A'}\n"
                f"<b>LEVEL:</b> {user.level}\n"
                f"<b>REP:</b> ⭐ {user.rep_points}"
            )
            
            results.append(InlineQueryResultArticle(
                id=f"profile_{i}",
                title=f"Profil: {user.ign}",
                description=f"Role: {user.role or 'N/A'} | Level: {user.level}",
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML"
                ),
                thumb_url="https://img.icons8.com/ios-filled/50/000000/user.png"
            ))

    # 2. Map Sharing (map)
    elif "map" in query or not query:
        for map_id, mdata in MAP_DB.items():
            if query and query not in mdata["name"].lower() and "map" not in query:
                continue
                
            text = get_header(f"INTEL PETA: {mdata['name'].upper()}", "📍")
            text += f"<b>Deskripsi:</b> {mdata.get('description', 'Data intelijen terbatas.')}\n\n"
            text += "<i>Gunakan /map di DM bot untuk navigasi detail.</i>"
            
            results.append(InlineQueryResultArticle(
                id=f"map_{map_id}",
                title=f"Peta: {mdata['name']}",
                description="Bagikan info intelijen peta ini.",
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML"
                ),
                thumb_url="https://img.icons8.com/ios-filled/50/000000/map.png"
            ))

    # 3. Loot / Red Items (loot)
    if "loot" in query or not query:
        red_items = [
            "Portable Military Radar (~2.2JT)",
            "Fuel Cell (~500RB)",
            "Blade Server (~800RB)",
            "Rare Fossil (~1.5JT)",
            "Military Laptop (~400RB)"
        ]
        
        text = get_header("ITEM PRIORITAS (RED)", "💎")
        text += "Daftar item berharga tinggi saat ini:\n\n" + \
                "\n".join([f"• {item}" for item in red_items])
        
        results.append(InlineQueryResultArticle(
            id="loot_list",
            title="Daftar Loot Berharga",
            description="Bagikan daftar item dengan nilai jual tinggi.",
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML"
            ),
            thumb_url="https://img.icons8.com/ios-filled/50/000000/diamond.png"
        ))

    await inline_query.answer(results=results[:20], cache_time=300)
