// ==============================================
// CYPHER QUERIES - Neo4j Knowledge Graph
// E-Commerce AI Service
// Mở Neo4j Browser: http://localhost:7474
// ==============================================


// ------ 1. KIỂM TRA DỮ LIỆU ------

// Xem tổng quan graph (giới hạn 50 nodes)
MATCH (n) RETURN n LIMIT 50;

// Thống kê số nodes và relationships
MATCH (u:User) WITH COUNT(u) AS users
MATCH (p:Product) WITH users, COUNT(p) AS products
MATCH ()-[r]->() WITH users, products, COUNT(r) AS rels
RETURN users, products, rels;


// ------ 2. SẢN PHẨM USER TƯƠNG TÁC NHIỀU NHẤT ------

// Sản phẩm user 1 tương tác nhiều nhất (có trọng số)
MATCH (u:User {id: 1})-[r]->(p:Product)
WITH p,
     SUM(CASE type(r) WHEN 'ADD_TO_CART' THEN 3
                      WHEN 'CLICK'       THEN 2
                      ELSE 1 END) AS score
RETURN p.id AS product_id, p.name AS name, score
ORDER BY score DESC
LIMIT 5;

// Lịch sử tất cả hành vi của user 1
MATCH (u:User {id: 1})-[r]->(p:Product)
RETURN u.id AS user_id, type(r) AS action, p.id AS product_id, p.name AS product_name
ORDER BY p.id;


// ------ 3. SẢN PHẨM PHỔ BIẾN NHẤT ------

// Top 10 sản phẩm phổ biến (tính cả trọng số hành vi)
MATCH (u:User)-[r]->(p:Product)
WITH p,
     SUM(CASE type(r) WHEN 'ADD_TO_CART' THEN 3
                      WHEN 'CLICK'       THEN 2
                      ELSE 1 END) AS score,
     COUNT(DISTINCT u) AS unique_users
RETURN p.id AS product_id, p.name AS name, score, unique_users
ORDER BY score DESC
LIMIT 10;

// Top sản phẩm được ADD_TO_CART nhiều nhất
MATCH (u:User)-[:ADD_TO_CART]->(p:Product)
RETURN p.id AS product_id, p.name AS name, COUNT(*) AS cart_count
ORDER BY cart_count DESC
LIMIT 10;

// Phân tích theo danh mục
MATCH (u:User)-[r]->(p:Product)
RETURN p.category AS category, COUNT(r) AS total_interactions
ORDER BY total_interactions DESC;


// ------ 4. SẢN PHẨM TƯƠNG TỰ (Collaborative Filtering) ------

// Sản phẩm tương tự với product 1 (iPhone 15 Pro Max)
MATCH (u:User)-[]->(p:Product {id: 1})
MATCH (u)-[]->(other:Product)
WHERE other.id <> 1
WITH other, COUNT(DISTINCT u) AS common_users
RETURN other.id AS product_id, other.name AS name, common_users
ORDER BY common_users DESC
LIMIT 5;

// Sản phẩm hay đi kèm nhau (user hay mua cả hai)
MATCH (u:User)-[]->(p1:Product)
MATCH (u)-[]->(p2:Product)
WHERE p1.id < p2.id
WITH p1, p2, COUNT(DISTINCT u) AS common_users
WHERE common_users >= 5
RETURN p1.name AS product_A, p2.name AS product_B, common_users
ORDER BY common_users DESC
LIMIT 10;


// ------ 5. VISUALIZE (Dùng để chụp ảnh báo cáo) ------

// Visualize: 1 User cụ thể và các sản phẩm (đẹp để chụp ảnh)
MATCH path = (u:User {id: 1})-[r]->(p:Product)
RETURN path;

// Visualize: 5 users và sản phẩm họ add_to_cart
MATCH path = (u:User)-[:ADD_TO_CART]->(p:Product)
WHERE u.id IN [1, 2, 3, 4, 5]
RETURN path;

// Visualize: Toàn bộ graph với 1 category (Điện thoại)
MATCH path = (u:User)-[r]->(p:Product {category: 'Điện thoại'})
RETURN path LIMIT 100;

// Visualize: Sản phẩm phổ biến nhất với tất cả user tương tác
MATCH path = (u:User)-[r]->(p:Product)
WHERE p.id IN [1, 7, 26]  // Thay bằng top sản phẩm sau khi import
RETURN path LIMIT 80;
