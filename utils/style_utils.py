import math

# Tactical Aesthetic Constants
SEP_LINE = "──────────────────────────────"
T_SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def get_header(title: str, icon: str = "🛡️") -> str:
    """Returns a clean professional header."""
    return (
        f"{icon} <b>{title.upper()}</b>\n"
        f"<code>{T_SEP}</code>\n"
    )

def get_footer(text: str = None) -> str:
    """Returns a minimal footer without robotic versioning."""
    if not text:
        return f"<code>{T_SEP}</code>"
    return (
        f"<code>{T_SEP}</code>\n"
        f"<i>{text}</i>"
    )

def format_field(label: str, value: str, icon: str = "🔹") -> str:
    """Formats a data field cleanly."""
    return f"{icon} <b>{label}</b>: <code>{value}</code>\n"

def progress_bar(current: int, total: int, width: int = 10) -> str:
    """Generates a clean progress bar."""
    if total <= 0: return "<code>[----------]</code>"
    progress = min(current / total, 1.0)
    filled = int(progress * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"<code>[{bar}]</code> {int(progress * 100)}%"

def get_divider():
    """Simple separator."""
    return f"<code>{SEP_LINE}</code>\n"
