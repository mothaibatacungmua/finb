from .balance_sheet.balance_sheet import render as balance_sheet_render
from .price.price import render as price_render
from .income_statement.income_statement import render as income_statement_render
from .cashflow.cashflow import render as cashflow_render

TABS_DICT = {
  'balance_sheet_analyzer': balance_sheet_render,
  'price_analyzer': price_render,
  'income_statement_analyzer': income_statement_render,
  'cashflow_analyzer': cashflow_render
}