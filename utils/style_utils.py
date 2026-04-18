def get_header(title: str, icon: str = "◈") -> str:
    """Returns a sleek symbolic header."""
    return f"{icon} <b>{title.upper()}</b>\n\n"

def get_footer(text: str = None) -> str:
    """Minimal footer with subtle symbols."""
    if not text:
        return ""
    return f"\n<i>{text}</i>"

def format_field(label: str, value: str, icon: str = "⬢") -> str:
    """Compact symbolic field formatting."""
    return f"{icon} <b>{label}</b>: <code>{value}</code>\n"

def progress_bar(current: int, total: int, width: int = 10) -> str:
    """Geometric minimalist progress bar."""
    if total <= 0: return "<code>[----------]</code>"
    progress = min(current / total, 1.0)
    filled = int(progress * width)
    bar = "▰" * filled + "▱" * (width - filled)
    return f"<code>{bar}</code> {int(progress * 100)}%"

def get_divider():
    """Subtle whitespace divider."""
    return "\n"
