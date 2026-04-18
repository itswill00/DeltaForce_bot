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

def progress_bar(current: int, total: int, width: int = 8) -> str:
    """Geometric minimalist progress bar."""
    if total <= 0: return "<code>[--------]</code>"
    progress = min(current / total, 1.0)
    filled = int(progress * width)
    bar = "■" * filled + "□" * (width - filled)
    return f"<code>{bar}</code> {int(progress * 100)}%"

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
