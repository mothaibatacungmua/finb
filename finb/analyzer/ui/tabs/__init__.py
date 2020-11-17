from .balance_sheet.balance_sheet import render as balance_sheet_render
from .price.price import render as price_render

TABS_DICT = {
  'balance_sheet_analyzer': balance_sheet_render,
  'price_analyzer': price_render
}