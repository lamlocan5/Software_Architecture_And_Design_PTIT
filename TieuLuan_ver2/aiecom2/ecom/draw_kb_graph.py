import os
import sys
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"

# Connect to Neo4j
try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
except Exception as e:
    print(f"Error connecting to Neo4j: {e}")
    sys.exit(1)

query = """
MATCH (u:User)-[r]->(p:Product)
RETURN u.id AS user_id, type(r) AS action, p.id AS product_id, p.name AS product_name
LIMIT 20
"""

records = []
with driver.session() as session:
    result = session.run(query)
    for record in result:
        records.append({
            "user_id": record["user_id"],
            "action": record["action"],
            "product_id": record["product_id"],
            "product_name": record["product_name"]
        })

driver.close()

# Draw Graph
G = nx.DiGraph()

for r in records:
    u_node = f"User {r['user_id']}"
    # Bẻ chữ tên sản phẩm cho đỡ dài
    name = r['product_name']
    if len(name) > 15:
        name = name[:15] + "\n" + name[15:]
    p_node = f"P{r['product_id']}:\n{name}"
    
    # Gán màu sắc cho Node
    if u_node not in G:
        G.add_node(u_node, color='#87CEFA', type='user') # Xanh dương nhạt
    if p_node not in G:
        G.add_node(p_node, color='#98FB98', type='product') # Xanh lá nhạt
        
    G.add_edge(u_node, p_node, label=r['action'])

# Layout & Config Vẽ
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, k=1.5, seed=42)

colors = [nx.get_node_attributes(G, 'color').get(node, 'gray') for node in G.nodes()]

# Vẽ các thành phần
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=3500, edgecolors='black', linewidths=1.5)
nx.draw_networkx_edges(G, pos, edge_color='#555555', width=1.5, arrowsize=20, connectionstyle='arc3,rad=0.1')
nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8, label_pos=0.5)

plt.title("Neo4j Knowledge Base Graph (20 Relationships)", fontsize=16, fontweight='bold', pad=20)
plt.axis('off')

# Tự động lưu ảnh ra Desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "KB_Graph_20_Rows.png")
plt.savefig(desktop_path, bbox_inches='tight', dpi=300)
print(f"✅ Đã lưu ảnh tự động tại: {desktop_path}")

# Hiển thị ảnh
plt.show()
