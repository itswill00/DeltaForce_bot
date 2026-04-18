def get_header(title: str, icon: str = "◈") -> str:
    """Returns a sleek, professional symbolic header."""
    return f"{icon} <b>{title.upper()}</b>\n\n"

def get_footer(text: str = None) -> str:
    """Returns a minimal footer with a subtle symbol."""
    if not text:
        return ""
    return f"\n<i>{text}</i>"

def format_field(label: str, value: str, icon: str = "⬢") -> str:
    """Compact symbolic field formatting."""
    return f"{icon} <b>{label}</b>: <code>{value}</code>\n"

def progress_bar(current: int, total: int, width: int = 10) -> str:
    """Geometric high-contrast progress bar."""
    if total <= 0: return "<code>▱▱▱▱▱▱▱▱▱▱</code>"
    progress = min(current / total, 1.0)
    filled = int(progress * width)
    bar = "▰" * filled + "▱" * (width - filled)
    return f"<code>{bar}</code> {int(progress * 100)}%"

def get_status_tag(is_active: bool, text: str) -> str:
    """Returns a visual status tag (● active, ○ inactive)."""
    icon = "●" if is_active else "○"
    return f"{icon} <b>{text.upper()}</b>"


def get_divider():
    """Minimal whitespace divider."""
    return "\n"

def force_height(text: str, target_lines: int = 12) -> str:
    """Pads text with empty lines to ensure consistent message height."""
    lines = text.count('\n')
    if lines < target_lines:
        padding = "\n" * (target_lines - lines)
        return text + padding
    return text

async def safe_edit_message(event, text: str, reply_markup=None):
    """
    Enterprise UI Helper: Smartly edits a message whether it has a photo or not.
    Accepts both Message and CallbackQuery events.
    """
    message = event if hasattr(event, 'caption') else getattr(event, 'message', None)
    if not message: return

    try:
        if message.photo:
            await message.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await message.edit_text(text=text, reply_markup=reply_markup)
    except Exception:
        # Fallback: if editing fails (e.g. content identical), just answer callback if exists
        if hasattr(event, 'answer'):
            await event.answer()
