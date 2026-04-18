def get_header(title: str, icon: str = "🛡️") -> str:
    """Returns a clean, minimal header."""
    return f"{icon} <b>{title.upper()}</b>\n\n"

def get_footer(text: str = None) -> str:
    """Returns a minimal footer with a simple separator."""
    if not text:
        return ""
    return f"\n<i>{text}</i>"

def format_field(label: str, value: str) -> str:
    """Compact key-value formatting."""
    return f"<b>{label}</b>: <code>{value}</code>\n"

def progress_bar(current: int, total: int, width: int = 8) -> str:
    """Sleek and compact progress bar."""
    if total <= 0: return "<code>[--------]</code>"
    progress = min(current / total, 1.0)
    filled = int(progress * width)
    bar = "■" * filled + "□" * (width - filled)
    return f"<code>{bar}</code> {int(progress * 100)}%"

def get_divider():
    """Minimal whitespace divider."""
    return "\n"
