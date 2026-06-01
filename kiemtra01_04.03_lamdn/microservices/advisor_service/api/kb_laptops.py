"""
Knowledge Base Data — Laptop (60 sản phẩm thực tế)
"""

LAPTOPS = [
    # ===== APPLE =====
    {"id": "lap_001", "name": "Apple MacBook Air M3 13 inch 2024", "brand": "Apple", "price_vnd": 28990000,
     "cpu": "Apple M3 8-core", "ram_gb": 8, "storage_gb": 256, "gpu": "Apple M3 10-core GPU",
     "display": "13.6 inch Liquid Retina 2560x1664", "battery_h": 18, "weight_kg": 1.24,
     "os": "macOS Sonoma", "use_cases": ["student", "office", "creative", "developer"],
     "highlights": "Pin 18 giờ, hiệu năng vượt trội, không quạt, siêu mỏng nhẹ, màn hình Retina sắc nét"},

    {"id": "lap_002", "name": "Apple MacBook Air M2 13 inch 2022", "brand": "Apple", "price_vnd": 22990000,
     "cpu": "Apple M2 8-core", "ram_gb": 8, "storage_gb": 256, "gpu": "Apple M2 8-core GPU",
     "display": "13.6 inch Liquid Retina 2560x1664", "battery_h": 18, "weight_kg": 1.24,
     "os": "macOS", "use_cases": ["student", "office", "creative"],
     "highlights": "Giá tốt hơn M3, pin 18 giờ, thiết kế siêu mỏng, phù hợp sinh viên"},

    {"id": "lap_003", "name": "Apple MacBook Pro M3 14 inch 2024", "brand": "Apple", "price_vnd": 44990000,
     "cpu": "Apple M3 Pro 11-core", "ram_gb": 18, "storage_gb": 512, "gpu": "Apple M3 Pro 14-core GPU",
     "display": "14.2 inch Liquid Retina XDR 3024x1964 ProMotion 120Hz", "battery_h": 22, "weight_kg": 1.55,
     "os": "macOS Sonoma", "use_cases": ["creative", "developer", "premium"],
     "highlights": "Màn hình ProMotion 120Hz, RAM 18GB, pin 22 giờ, hiệu năng chuyên nghiệp"},

    {"id": "lap_004", "name": "Apple MacBook Pro M4 14 inch 2025", "brand": "Apple", "price_vnd": 52990000,
     "cpu": "Apple M4 Pro 12-core", "ram_gb": 24, "storage_gb": 512, "gpu": "Apple M4 Pro 20-core GPU",
     "display": "14.2 inch Liquid Retina XDR 120Hz", "battery_h": 24, "weight_kg": 1.55,
     "os": "macOS Sequoia", "use_cases": ["creative", "developer", "premium"],
     "highlights": "Chip M4 mạnh nhất 2025, RAM 24GB, pin 24 giờ, cho dân chuyên nghiệp"},

    # ===== DELL =====
    {"id": "lap_005", "name": "Dell XPS 13 9340 Intel Core Ultra 7", "brand": "Dell", "price_vnd": 35990000,
     "cpu": "Intel Core Ultra 7 155H", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Arc Graphics",
     "display": "13.4 inch OLED 2880x1920 60Hz", "battery_h": 12, "weight_kg": 1.17,
     "os": "Windows 11", "use_cases": ["premium", "office", "developer"],
     "highlights": "Màn hình OLED đẹp nhất phân khúc, siêu nhỏ gọn, vỏ nhôm cao cấp"},

    {"id": "lap_006", "name": "Dell Inspiron 15 3520 i5-1235U", "brand": "Dell", "price_vnd": 13990000,
     "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "15.6 inch FHD 1920x1080 120Hz", "battery_h": 8, "weight_kg": 1.76,
     "os": "Windows 11", "use_cases": ["student", "office", "budget"],
     "highlights": "Giá cực tốt, màn hình 120Hz mượt, phù hợp sinh viên văn phòng"},

    {"id": "lap_007", "name": "Dell Inspiron 16 Plus 7630 i7-13700H RTX 4060", "brand": "Dell", "price_vnd": 29990000,
     "cpu": "Intel Core i7-13700H", "ram_gb": 16, "storage_gb": 512, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "16 inch QHD+ 2560x1600 165Hz", "battery_h": 8, "weight_kg": 2.0,
     "os": "Windows 11", "use_cases": ["gaming", "creative", "developer"],
     "highlights": "RTX 4060 mạnh, màn QHD 165Hz, cân được game AAA lẫn đồ họa"},

    {"id": "lap_008", "name": "Dell Alienware m16 R2 RTX 4090", "brand": "Dell", "price_vnd": 79990000,
     "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4090 16GB",
     "display": "16 inch QHD+ 240Hz", "battery_h": 5, "weight_kg": 3.49,
     "os": "Windows 11", "use_cases": ["gaming", "premium"],
     "highlights": "Gaming laptop mạnh nhất, RTX 4090, màn 240Hz, cho game thủ chuyên nghiệp"},

    {"id": "lap_009", "name": "Dell Latitude 5540 i5-1335U", "brand": "Dell", "price_vnd": 19990000,
     "cpu": "Intel Core i5-1335U", "ram_gb": 16, "storage_gb": 256, "gpu": "Intel Iris Xe",
     "display": "15.6 inch FHD IPS", "battery_h": 10, "weight_kg": 1.78,
     "os": "Windows 11 Pro", "use_cases": ["office", "business"],
     "highlights": "Dành cho doanh nghiệp, bảo mật tốt, bền bỉ, hỗ trợ VPN"},

    # ===== HP =====
    {"id": "lap_010", "name": "HP Spectre x360 14 i7-1355U OLED", "brand": "HP", "price_vnd": 42990000,
     "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch OLED 2880x1800 90Hz touch", "battery_h": 15, "weight_kg": 1.41,
     "os": "Windows 11", "use_cases": ["premium", "creative", "office"],
     "highlights": "Gập 360 độ, màn OLED cảm ứng, thiết kế sang trọng nhất HP"},

    {"id": "lap_011", "name": "HP Pavilion 15 i5-1235U", "brand": "HP", "price_vnd": 14990000,
     "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "15.6 inch FHD IPS", "battery_h": 8, "weight_kg": 1.75,
     "os": "Windows 11", "use_cases": ["student", "office", "budget"],
     "highlights": "Giá vừa phải, màn IPS chống chói tốt, phù hợp sinh viên"},

    {"id": "lap_012", "name": "HP Omen 16 RTX 4070 i9-13900HX", "brand": "HP", "price_vnd": 49990000,
     "cpu": "Intel Core i9-13900HX", "ram_gb": 16, "storage_gb": 1024, "gpu": "NVIDIA RTX 4070 8GB",
     "display": "16.1 inch QHD 240Hz", "battery_h": 6, "weight_kg": 2.61,
     "os": "Windows 11", "use_cases": ["gaming", "creative"],
     "highlights": "Gaming cao cấp, RTX 4070, màn 240Hz, tản nhiệt mạnh"},

    {"id": "lap_013", "name": "HP EliteBook 840 G10 i7-1355U", "brand": "HP", "price_vnd": 33990000,
     "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 1920x1200 IPS", "battery_h": 12, "weight_kg": 1.34,
     "os": "Windows 11 Pro", "use_cases": ["business", "office"],
     "highlights": "Laptop doanh nghiệp cao cấp HP, bảo mật chip TPM, bền MIL-SPEC"},

    {"id": "lap_014", "name": "HP Envy 13 x360 i7-1355U 2-in-1", "brand": "HP", "price_vnd": 24990000,
     "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "13.3 inch 2560x1600 OLED touch", "battery_h": 10, "weight_kg": 1.32,
     "os": "Windows 11", "use_cases": ["creative", "office", "student"],
     "highlights": "2-in-1 gập gọn, màn OLED 2K cảm ứng, bút cảm ứng tích hợp"},

    # ===== LENOVO =====
    {"id": "lap_015", "name": "Lenovo ThinkPad X1 Carbon Gen 12 i7-1365U", "brand": "Lenovo", "price_vnd": 47990000,
     "cpu": "Intel Core i7-1365U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 2560x1600 IPS", "battery_h": 15, "weight_kg": 1.12,
     "os": "Windows 11 Pro", "use_cases": ["business", "developer", "office"],
     "highlights": "Nhẹ nhất phân khúc business (1.12kg), pin 15h, bàn phím huyền thoại"},

    {"id": "lap_016", "name": "Lenovo IdeaPad Slim 5 i5-13420H", "brand": "Lenovo", "price_vnd": 15990000,
     "cpu": "Intel Core i5-13420H", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel UHD",
     "display": "16 inch 1920x1200 IPS", "battery_h": 9, "weight_kg": 1.76,
     "os": "Windows 11", "use_cases": ["student", "office", "budget"],
     "highlights": "RAM 16GB, màn 16 inch rộng, giá hợp lý cho sinh viên"},

    {"id": "lap_017", "name": "Lenovo Legion 5 Pro RTX 4060 Ryzen 7 7745HX", "brand": "Lenovo", "price_vnd": 34990000,
     "cpu": "AMD Ryzen 7 7745HX", "ram_gb": 16, "storage_gb": 512, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "16 inch 2560x1600 165Hz IPS", "battery_h": 6, "weight_kg": 2.4,
     "os": "Windows 11", "use_cases": ["gaming", "creative"],
     "highlights": "Gaming tầm trung tốt nhất, RTX 4060, màn QHD 165Hz, giá cực hợp lý"},

    {"id": "lap_018", "name": "Lenovo Legion 7 RTX 4070 i9-13900HX", "brand": "Lenovo", "price_vnd": 55990000,
     "cpu": "Intel Core i9-13900HX", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4070 Ti 12GB",
     "display": "16 inch 2560x1600 240Hz IPS", "battery_h": 5, "weight_kg": 2.7,
     "os": "Windows 11", "use_cases": ["gaming", "creative", "premium"],
     "highlights": "Gaming flagship Lenovo, RTX 4070Ti, màn 240Hz, RAM 32GB"},

    {"id": "lap_019", "name": "Lenovo Yoga 9i 14 i7-1360P OLED 2-in-1", "brand": "Lenovo", "price_vnd": 38990000,
     "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 2880x1800 OLED 90Hz touch", "battery_h": 14, "weight_kg": 1.49,
     "os": "Windows 11", "use_cases": ["creative", "premium", "office"],
     "highlights": "2-in-1 cao cấp, màn OLED 2.8K, loa Bowers & Wilkins, sang trọng"},

    # ===== ASUS =====
    {"id": "lap_020", "name": "ASUS ROG Strix G16 RTX 4080 i9-14900HX", "brand": "ASUS", "price_vnd": 72990000,
     "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4080 12GB",
     "display": "16 inch 2560x1600 240Hz IPS", "battery_h": 4, "weight_kg": 2.9,
     "os": "Windows 11", "use_cases": ["gaming", "premium"],
     "highlights": "Cỗ máy gaming đỉnh cao, RTX 4080, màn 240Hz, tản nhiệt 3 quạt"},

    {"id": "lap_021", "name": "ASUS TUF Gaming F15 RTX 4060 i7-13700H", "brand": "ASUS", "price_vnd": 26990000,
     "cpu": "Intel Core i7-13700H", "ram_gb": 16, "storage_gb": 512, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "15.6 inch FHD 144Hz IPS", "battery_h": 6, "weight_kg": 2.2,
     "os": "Windows 11", "use_cases": ["gaming", "student"],
     "highlights": "Gaming bền bỉ, giá phải chăng, RTX 4060, MIL-SPEC chịu va đập"},

    {"id": "lap_022", "name": "ASUS ZenBook 14 OLED UX3405 i7-1355U", "brand": "ASUS", "price_vnd": 24990000,
     "cpu": "Intel Core Ultra 7 155H", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Arc Graphics",
     "display": "14 inch 2880x1800 OLED 120Hz", "battery_h": 12, "weight_kg": 1.2,
     "os": "Windows 11", "use_cases": ["student", "creative", "office", "premium"],
     "highlights": "OLED đẹp nhất tầm 25tr, siêu nhẹ 1.2kg, pin 12h, màn sắc nét"},

    {"id": "lap_023", "name": "ASUS VivoBook 15 X1504 i5-1235U", "brand": "ASUS", "price_vnd": 12990000,
     "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "15.6 inch FHD IPS", "battery_h": 7, "weight_kg": 1.7,
     "os": "Windows 11", "use_cases": ["student", "budget", "office"],
     "highlights": "Rẻ nhất phân khúc i5 chính hãng, phù hợp sinh viên ngân sách thấp"},

    {"id": "lap_024", "name": "ASUS ROG Zephyrus G14 RTX 4060 Ryzen 9 7940HS", "brand": "ASUS", "price_vnd": 42990000,
     "cpu": "AMD Ryzen 9 7940HS", "ram_gb": 16, "storage_gb": 1024, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "14 inch 2560x1600 165Hz IPS", "battery_h": 10, "weight_kg": 1.65,
     "os": "Windows 11", "use_cases": ["gaming", "creative", "premium"],
     "highlights": "Gaming + mỏng nhẹ, Ryzen 9 mạnh, màn QHD 165Hz, pin tốt cho gaming"},

    # ===== ACER =====
    {"id": "lap_025", "name": "Acer Predator Helios 16 RTX 4080 i9-13900HX", "brand": "Acer", "price_vnd": 65990000,
     "cpu": "Intel Core i9-13900HX", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4080 12GB",
     "display": "16 inch 2560x1600 250Hz IPS", "battery_h": 4, "weight_kg": 3.1,
     "os": "Windows 11", "use_cases": ["gaming", "premium"],
     "highlights": "Gaming flagship Acer, màn 250Hz cực mượt, tản nhiệt AeroBlade"},

    {"id": "lap_026", "name": "Acer Nitro V 15 RTX 4060 i5-13420H", "brand": "Acer", "price_vnd": 22990000,
     "cpu": "Intel Core i5-13420H", "ram_gb": 8, "storage_gb": 512, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "15.6 inch FHD 165Hz IPS", "battery_h": 5, "weight_kg": 2.4,
     "os": "Windows 11", "use_cases": ["gaming", "student"],
     "highlights": "Gaming rẻ nhất có RTX 4060, giá 23tr, phù hợp game thủ sinh viên"},

    {"id": "lap_027", "name": "Acer Swift Go 14 OLED i7-1355U", "brand": "Acer", "price_vnd": 19990000,
     "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 2880x1800 OLED 90Hz", "battery_h": 10, "weight_kg": 1.25,
     "os": "Windows 11", "use_cases": ["student", "office", "creative"],
     "highlights": "OLED dưới 20tr, siêu nhẹ, pin 10h, đáng tiền nhất phân khúc"},

    {"id": "lap_028", "name": "Acer Aspire 5 i5-1235U", "brand": "Acer", "price_vnd": 11990000,
     "cpu": "Intel Core i5-1235U", "ram_gb": 8, "storage_gb": 256, "gpu": "Intel Iris Xe",
     "display": "15.6 inch FHD IPS", "battery_h": 7, "weight_kg": 1.7,
     "os": "Windows 11", "use_cases": ["student", "budget"],
     "highlights": "Rẻ nhất phân khúc, phù hợp sinh viên ngân sách 12 triệu"},

    # ===== MSI =====
    {"id": "lap_029", "name": "MSI Titan GT77 RTX 4090 i9-13980HX", "brand": "MSI", "price_vnd": 99990000,
     "cpu": "Intel Core i9-13980HX", "ram_gb": 64, "storage_gb": 2048, "gpu": "NVIDIA RTX 4090 16GB",
     "display": "17.3 inch UHD 144Hz mini-LED", "battery_h": 3, "weight_kg": 3.9,
     "os": "Windows 11", "use_cases": ["gaming", "premium"],
     "highlights": "Laptop gaming mạnh nhất thế giới, RTX 4090, RAM 64GB, mọi game max settings"},

    {"id": "lap_030", "name": "MSI Modern 14 B7M Ryzen 5 7530U", "brand": "MSI", "price_vnd": 14990000,
     "cpu": "AMD Ryzen 5 7530U", "ram_gb": 8, "storage_gb": 512, "gpu": "AMD Radeon",
     "display": "14 inch FHD IPS", "battery_h": 9, "weight_kg": 1.4,
     "os": "Windows 11", "use_cases": ["student", "office", "budget"],
     "highlights": "Mỏng nhẹ 1.4kg, pin 9h, cực phù hợp sinh viên đi lại nhiều"},

    {"id": "lap_031", "name": "MSI Stealth 16 Studio RTX 4070 i9-13900H", "brand": "MSI", "price_vnd": 58990000,
     "cpu": "Intel Core i9-13900H", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4070 8GB",
     "display": "16 inch 4K OLED 60Hz", "battery_h": 6, "weight_kg": 2.1,
     "os": "Windows 11", "use_cases": ["creative", "premium", "developer"],
     "highlights": "Màn 4K OLED tuyệt đẹp, RTX 4070, cho nhà thiết kế và content creator"},

    # ===== SAMSUNG =====
    {"id": "lap_032", "name": "Samsung Galaxy Book4 Ultra RTX 4070 i9-14900H", "brand": "Samsung", "price_vnd": 62990000,
     "cpu": "Intel Core i9-14900H", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4070 8GB",
     "display": "16 inch 3K Dynamic AMOLED 120Hz", "battery_h": 8, "weight_kg": 1.86,
     "os": "Windows 11", "use_cases": ["creative", "premium", "gaming"],
     "highlights": "Màn AMOLED 3K đẹp nhất, tích hợp AI Samsung, hệ sinh thái Galaxy"},

    {"id": "lap_033", "name": "Samsung Galaxy Book4 Pro 360 i7-1360P AMOLED", "brand": "Samsung", "price_vnd": 38990000,
     "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 3K AMOLED 120Hz touch 2-in-1", "battery_h": 12, "weight_kg": 1.51,
     "os": "Windows 11", "use_cases": ["creative", "office", "premium"],
     "highlights": "2-in-1 màn AMOLED 3K, kết nối Galaxy S-series, bút S-Pen tích hợp"},

    # ===== RAZER =====
    {"id": "lap_034", "name": "Razer Blade 16 RTX 4090 i9-14900HX", "brand": "Razer", "price_vnd": 95990000,
     "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 2048, "gpu": "NVIDIA RTX 4090 16GB",
     "display": "16 inch UHD+ 240Hz mini-LED", "battery_h": 5, "weight_kg": 2.69,
     "os": "Windows 11", "use_cases": ["gaming", "premium", "creative"],
     "highlights": "Gaming laptop sang trọng nhất, tản nhiệt vapor chamber, đèn RGB Chroma"},

    # ===== MICROSOFT =====
    {"id": "lap_035", "name": "Microsoft Surface Laptop 6 i7-1365U", "brand": "Microsoft", "price_vnd": 41990000,
     "cpu": "Intel Core i7-1365U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "13.5 inch 2256x1504 PixelSense touch", "battery_h": 19, "weight_kg": 1.28,
     "os": "Windows 11", "use_cases": ["office", "premium", "student"],
     "highlights": "Pin 19 giờ xuất sắc, màn PixelSense tỉ lệ 3:2 rộng, cảm ứng chính xác"},

    # ===== LG =====
    {"id": "lap_036", "name": "LG Gram 14 2024 i7-1360P Intel Evo", "brand": "LG", "price_vnd": 29990000,
     "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 2560x1600 IPS DCI-P3 99%", "battery_h": 22, "weight_kg": 0.99,
     "os": "Windows 11", "use_cases": ["office", "student", "business"],
     "highlights": "Nhẹ nhất thế giới dưới 1kg, pin 22 giờ kỷ lục, MIL-SPEC 7 tiêu chuẩn"},

    {"id": "lap_037", "name": "LG Gram 17 2024 i7 Ultra", "brand": "LG", "price_vnd": 39990000,
     "cpu": "Intel Core Ultra 7 155H", "ram_gb": 32, "storage_gb": 1024, "gpu": "Intel Arc Graphics",
     "display": "17 inch 2560x1600 IPS", "battery_h": 18, "weight_kg": 1.35,
     "os": "Windows 11", "use_cases": ["office", "developer", "business"],
     "highlights": "Màn 17 inch nhưng chỉ 1.35kg, pin 18h, RAM 32GB, đa nhiệm cực tốt"},

    # ===== HUAWEI =====
    {"id": "lap_038", "name": "Huawei MateBook X Pro 2024 i7-1360P", "brand": "Huawei", "price_vnd": 36990000,
     "cpu": "Intel Core i7-1360P", "ram_gb": 16, "storage_gb": 1024, "gpu": "Intel Iris Xe",
     "display": "14.2 inch 3.1K OLED 90Hz", "battery_h": 14, "weight_kg": 1.26,
     "os": "Windows 11", "use_cases": ["premium", "office", "creative"],
     "highlights": "Màn OLED 3.1K siêu đẹp, nhẹ 1.26kg, cảm ứng, kết nối hệ sinh thái Huawei"},

    # ===== XIAOMI =====
    {"id": "lap_039", "name": "Xiaomi Book Pro 16 2024 i9-13900H OLED", "brand": "Xiaomi", "price_vnd": 33990000,
     "cpu": "Intel Core i9-13900H", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "16 inch 3.2K OLED 120Hz", "battery_h": 9, "weight_kg": 1.8,
     "os": "Windows 11", "use_cases": ["creative", "premium", "developer"],
     "highlights": "OLED 3.2K + RTX 4060 hiếm thấy tầm giá, RAM 32GB, giá tốt"},

    # ===== THÊM CÁC SẢN PHẨM ĐÁ GIÁ =====
    {"id": "lap_040", "name": "Acer Aspire 3 i3-1215U 2024", "brand": "Acer", "price_vnd": 8990000,
     "cpu": "Intel Core i3-1215U", "ram_gb": 4, "storage_gb": 256, "gpu": "Intel UHD",
     "display": "15.6 inch FHD", "battery_h": 6, "weight_kg": 1.7,
     "os": "Windows 11 Home", "use_cases": ["budget", "student"],
     "highlights": "Rẻ nhất thị trường dưới 10 triệu, phù hợp soạn văn bản, học Online"},

    {"id": "lap_041", "name": "Lenovo IdeaPad 1 Celeron N4020", "brand": "Lenovo", "price_vnd": 6990000,
     "cpu": "Intel Celeron N4020", "ram_gb": 4, "storage_gb": 128, "gpu": "Intel UHD",
     "display": "14 inch HD", "battery_h": 7, "weight_kg": 1.5,
     "os": "Windows 11 Home S", "use_cases": ["budget"],
     "highlights": "Dưới 7 triệu, chỉ dùng cho soạn thảo, xem phim, học online cơ bản"},

    {"id": "lap_042", "name": "ASUS VivoBook Go 15 Ryzen 5 7520U", "brand": "ASUS", "price_vnd": 11490000,
     "cpu": "AMD Ryzen 5 7520U", "ram_gb": 8, "storage_gb": 512, "gpu": "AMD Radeon",
     "display": "15.6 inch FHD", "battery_h": 8, "weight_kg": 1.75,
     "os": "Windows 11", "use_cases": ["student", "budget"],
     "highlights": "Ryzen 5 mạnh hơn i3, giá 11.5tr, tốc độ khá cho sinh viên"},

    {"id": "lap_043", "name": "HP Victus 15 RTX 3050 i5-12450H", "brand": "HP", "price_vnd": 16990000,
     "cpu": "Intel Core i5-12450H", "ram_gb": 8, "storage_gb": 512, "gpu": "NVIDIA RTX 3050 4GB",
     "display": "15.6 inch FHD 144Hz IPS", "battery_h": 6, "weight_kg": 2.29,
     "os": "Windows 11", "use_cases": ["gaming", "student"],
     "highlights": "Gaming rẻ nhất có card rời RTX, màn 144Hz, giá 17tr"},

    {"id": "lap_044", "name": "Dell G15 5530 RTX 4060 i7-13650HX", "brand": "Dell", "price_vnd": 28990000,
     "cpu": "Intel Core i7-13650HX", "ram_gb": 16, "storage_gb": 512, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "15.6 inch FHD 165Hz IPS", "battery_h": 5, "weight_kg": 2.81,
     "os": "Windows 11", "use_cases": ["gaming", "student"],
     "highlights": "Gaming phổ thông, RTX 4060, giá mid-range, tản nhiệt tốt"},

    {"id": "lap_045", "name": "ASUS ProArt Studiobook 16 RTX 4070 i9 OLED", "brand": "ASUS", "price_vnd": 68990000,
     "cpu": "Intel Core i9-13980HX", "ram_gb": 64, "storage_gb": 2048, "gpu": "NVIDIA RTX 4070 8GB",
     "display": "16 inch 3.2K OLED 120Hz 100% DCI-P3", "battery_h": 8, "weight_kg": 2.4,
     "os": "Windows 11 Pro", "use_cases": ["creative", "premium"],
     "highlights": "Dành cho nhà thiết kế chuyên nghiệp, màn OLED chuẩn màu 100% DCI-P3, RAM 64GB"},

    {"id": "lap_046", "name": "Lenovo Legion Pro 7 RTX 4090 i9-14900HX", "brand": "Lenovo", "price_vnd": 89990000,
     "cpu": "Intel Core i9-14900HX", "ram_gb": 32, "storage_gb": 1024, "gpu": "NVIDIA RTX 4090 16GB",
     "display": "16 inch 2560x1600 240Hz IPS", "battery_h": 4, "weight_kg": 3.1,
     "os": "Windows 11", "use_cases": ["gaming", "premium"],
     "highlights": "Gaming flagship Legion, RTX 4090, tản nhiệt ColdFront 5.0, màn 240Hz"},

    {"id": "lap_047", "name": "HP Dragonfly Pro Chromebook i5-1235U", "brand": "HP", "price_vnd": 19990000,
     "cpu": "Intel Core i5-1235U", "ram_gb": 16, "storage_gb": 256, "gpu": "Intel Iris Xe",
     "display": "14 inch 2560x1600 IPS touch", "battery_h": 11, "weight_kg": 1.4,
     "os": "ChromeOS", "use_cases": ["student", "office"],
     "highlights": "Chromebook cao cấp, bảo mật tốt, nhẹ, dùng ứng dụng Google tốt nhất"},

    {"id": "lap_048", "name": "MSI Creator M16 RTX 4060 i7-13700H OLED", "brand": "MSI", "price_vnd": 39990000,
     "cpu": "Intel Core i7-13700H", "ram_gb": 16, "storage_gb": 512, "gpu": "NVIDIA RTX 4060 8GB",
     "display": "16 inch 4K OLED 60Hz 100% DCI-P3", "battery_h": 7, "weight_kg": 2.0,
     "os": "Windows 11", "use_cases": ["creative", "developer"],
     "highlights": "Màn 4K OLED chuẩn màu cho creator, RTX 4060 render nhanh"},

    {"id": "lap_049", "name": "Apple MacBook Air M1 13 inch", "brand": "Apple", "price_vnd": 17990000,
     "cpu": "Apple M1 8-core", "ram_gb": 8, "storage_gb": 256, "gpu": "Apple M1 7-core GPU",
     "display": "13.3 inch Retina 2560x1600", "battery_h": 18, "weight_kg": 1.29,
     "os": "macOS", "use_cases": ["student", "office"],
     "highlights": "MacBook rẻ nhất, pin 18h, hoàn toàn không quạt, tuyệt vời cho sinh viên"},

    {"id": "lap_050", "name": "Acer Swift 5 Ultrabook i7-1355U", "brand": "Acer", "price_vnd": 22990000,
     "cpu": "Intel Core i7-1355U", "ram_gb": 16, "storage_gb": 512, "gpu": "Intel Iris Xe",
     "display": "14 inch 2560x1600 IPS touch", "battery_h": 11, "weight_kg": 1.07,
     "os": "Windows 11", "use_cases": ["office", "student", "business"],
     "highlights": "Siêu nhẹ 1.07kg, cảm ứng, pin 11h, ultrabook di động tốt nhất Acer"},
]
