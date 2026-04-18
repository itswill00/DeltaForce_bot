import math

# Tactical Aesthetic Constants
SEP_LINE = "──────────────────────────────"
T_SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def get_header(title: str, icon: str = "🛡️") -> str:
    """Returns a high-impact tactical header."""
    return (
        f"{icon} <b>{title.upper()}</b>\n"
        f"<code>{T_SEP}</code>\n"
    )

def get_footer(version: str = "v4.0.0-PRO") -> str:
    """Returns a clean tactical footer."""
    return (
        f"<code>{T_SEP}</code>\n"
        f"<i>📡 Delta Force Hub | {version}</i>"
    )

def format_field(label: str, value: str, icon: str = "🔹") -> str:
    """Formats a data field with a fixed-width look."""
    return f"{icon} <b>{label:12}</b> : <code>{value}</code>\n"

def progress_bar(current: int, total: int, width: int = 10) -> str:
    """Generates a tactical progress bar."""
    if total <= 0: return "<code>[----------]</code>"
    progress = min(current / total, 1.0)
    filled = int(progress * width)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(progress * 100)
    return f"<code>[{bar}]</code> {percent}%"

def get_divider():
    """Simple separator."""
    return f"<code>{SEP_LINE}</code>\n"
