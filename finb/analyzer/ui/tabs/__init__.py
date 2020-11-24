from .balance_sheet.balance_sheet import render as balance_sheet_render
from .price.price import render as price_render
from .income_statement.income_statement import render as income_statement_render
from .cashflow.cashflow import render as cashflow_render
from .COGS_compare.COGS_compare import render as COGS_compare_render
from .SGA_compare.SGA_compare import render as SAG_compare_render
from .revenue.revenue import render as revenue_render
from .net_income.net_income import render as net_income_render

TABS_DICT = {
  'balance_sheet_analyzer': balance_sheet_render,
  'price_analyzer': price_render,
  'income_statement_analyzer': income_statement_render,
  'cashflow_analyzer': cashflow_render,
  'cogs_compare_analyzer': COGS_compare_render,
  'sga_compare_analyzer': SAG_compare_render,
  'revenue_analyzer': revenue_render,
  'net_income_analyzer': net_income_render
}