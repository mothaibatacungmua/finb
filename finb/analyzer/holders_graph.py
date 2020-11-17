import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from finb.utils.datahub import read_major_holders, read_companies_df
from finb.utils.vn_lang import vn_tolowercase

#https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7
#https://stackoverflow.com/questions/26691442/how-do-i-add-a-new-attribute-to-an-edge-in-networkx
#https://towardsdatascience.com/tutorial-network-visualization-basics-with-networkx-and-plotly-and-a-little-nlp-57c9bbb55bb9



def create_major_holders_graph(symbols):
    G = nx.DiGraph()
    companies_df = read_companies_df()
    companies_df["company"] = companies_df["company"].str.lower()
    # print("công ty cổ phần chứng khoán ssi" in companies_df["company"].values)
    holders = set()
    # edge_lists = []
    more_symbols = set(symbols)
    fund_nodes = set()

    for symbol in symbols:
        mholder_df = read_major_holders(symbol)

        G.add_node(symbol)

        for i, r in mholder_df.iterrows():
            holder = r["Name"]
            norm_holder = holder.replace("CTCP", "công ty cổ phần").lower()
            is_symbol = False
            is_fund = False
            if vn_tolowercase(norm_holder) in companies_df["company"].values:
                holder = companies_df.index[companies_df['company'] == vn_tolowercase(norm_holder)].tolist()[0]
                more_symbols.add(holder)
                is_symbol = True
            if vn_tolowercase(holder) in companies_df["company"].values:
                holder = companies_df.index[companies_df['company'] == vn_tolowercase(holder)].tolist()[0]
                more_symbols.add(holder)
                is_symbol = True
            if "fund" in norm_holder or "investment" in norm_holder or "đầu tư" in norm_holder or "halley" in norm_holder:
                is_fund = True
                fund_nodes.add(holder)
            w = round(r["Ownership"], 6)
            G.add_edge(symbol, holder, weight=w)
            # edge_lists.append((symbol, holder))
            if not is_symbol and not is_fund:
                holders.add(holder)
    return G, more_symbols, list(holders), list(fund_nodes)

G, symbol_nodes, holder_nodes, fund_nodes = create_major_holders_graph(["PGS"])


pos = nx.spring_layout(G, k=0.2, iterations=30, scale=2)
# pos = nx.nx_agraph.graphviz_layout(G, prog="neato")
# pos = nx.spring_layout(G, k=0.3*1/np.sqrt(len(G.nodes())), iterations=20)
nx.draw_networkx_nodes(G, pos=pos, nodelist=symbol_nodes, node_color='r', node_size=1000)
nx.draw_networkx_nodes(G, pos=pos, nodelist=holder_nodes, node_color='b', node_size=1000)
nx.draw_networkx_nodes(G, pos=pos, nodelist=fund_nodes, node_color='g', node_size=1000)
nx.draw_networkx_labels(G,pos=pos, font_size=7)
nx.draw_networkx_edges(G, pos=pos)
labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)

# nx.write_graphml(G, "test.graphml")
plt.show()

