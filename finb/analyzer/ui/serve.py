from finb.analyzer.ui.app import application
from finb.analyzer.ui.layout import *

if __name__ == "__main__":
  application.run_server(debug=True, use_reloader=True)