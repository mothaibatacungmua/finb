### Vietnam Stock Market Analyzer without database

This system has a simple design, all market data in `*.csv` or `*.json`. 

#### Setup environment

Run the following command to crawl all market symbols (also initialize core data for the system):

```bash
$ git clone 
$ cd finb
$ pip install -r requirements.txt
$ export PYTHONPATH=$(pwd)
$ python finb/crawl/sectors.py
```

#### Run UI

UI components written by [`dash`](https://dash.plotly.com/) design by the card concept, its html structure:

```
[------------Input names of card------------]
  [------------card 1 contents------------]
  [------------card 2 contents------------]
```

Cards' code in the directory `finb/analyzer/ui`. To add a card module, do same thing as `finb/analyzer/ui/tabs/balance_sheet`.

Run UI by:
```
$ python analyzer/ui/server.py
```