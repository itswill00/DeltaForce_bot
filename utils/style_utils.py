def get_header(title: str, emoji: str = "🛡️") -> str:
    """Returns a clean emoji-based header."""
    return f"{emoji} <b>{title.upper()}</b>\n" + "─" * 15 + "\n"

def get_footer(text: str) -> str:
    """Returns a clean footer with a small note."""
    return f"─" * 15 + f"\n<i>{text}</i>"

def format_status(label: str, value: str) -> str:
    """Formats a status line."""
    return f"<b>{label}:</b> {value}\n"
