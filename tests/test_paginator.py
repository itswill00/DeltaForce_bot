import pytest
from utils.paginator import InlineKeyboardPaginator

def test_paginator_basic():
    items = [(f"data_{i}", f"Button {i}") for i in range(10)]
    paginator = InlineKeyboardPaginator(items, items_per_page=4)
    
    assert paginator.total_pages == 3
    
    # Page 0
    builder = paginator.get_page(0)
    markup = builder.as_markup()
    # 4 items + Next + Close = 6 buttons
    assert len(markup.inline_keyboard) == 4 # adjust(2) called, so 2 rows of 2, then navigation.
    # Total buttons: 4 (items) + 1 (Next) + 1 (Tutup) = 6
    flat_buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(flat_buttons) == 6
    assert flat_buttons[4].text == "Next ➡️"
    assert flat_buttons[5].text == "[ Tutup ]"

def test_paginator_last_page():
    items = [(f"data_{i}", f"Button {i}") for i in range(10)]
    paginator = InlineKeyboardPaginator(items, items_per_page=4)
    
    # Page 2 (last page, 2 items)
    builder = paginator.get_page(2)
    markup = builder.as_markup()
    flat_buttons = [b for row in markup.inline_keyboard for b in row]
    # 2 items + Prev + Tutup = 4 buttons
    assert len(flat_buttons) == 4
    assert flat_buttons[2].text == "⬅️ Prev"
    assert flat_buttons[3].text == "[ Tutup ]"
