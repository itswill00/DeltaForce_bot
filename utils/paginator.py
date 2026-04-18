from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Any

class InlineKeyboardPaginator:
    """Utility to paginate InlineKeyboard buttons.
    
    Attributes:
        items: List of items to display (each item can be any object; the caller decides how to render).
        items_per_page: Number of items per page.
        callback_prefix: Prefix for callback data to identify pagination callbacks.
    """
    def __init__(self, items: List[Any], items_per_page: int = 6, callback_prefix: str = "meta_page_"):
        self.items = items
        self.items_per_page = items_per_page
        self.callback_prefix = callback_prefix
        self.total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)

    def _page_slice(self, page: int) -> List[Any]:
        start = page * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def get_page(self, page: int) -> InlineKeyboardBuilder:
        """Return an InlineKeyboardBuilder for the given page index (0‑based)."""
        builder = InlineKeyboardBuilder()
        page_items = self._page_slice(page)
        for item in page_items:
            # Expect each item to be a tuple (callback_data, button_text)
            cb_data, text = item
            builder.button(text=text, callback_data=cb_data)
        # Navigation buttons
        if self.total_pages > 1:
            if page > 0:
                builder.button(text="⬅️ Prev", callback_data=f"{self.callback_prefix}{page-1}")
            if page < self.total_pages - 1:
                builder.button(text="Next ➡️", callback_data=f"{self.callback_prefix}{page+1}")
        # Always add a close button
        builder.button(text="[ Tutup ]", callback_data="close_msg")
        # Adjust layout: 2 columns for items, navigation on separate row
        builder.adjust(2)
        return builder
