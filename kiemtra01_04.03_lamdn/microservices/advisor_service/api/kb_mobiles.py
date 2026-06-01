"""
Knowledge Base Data — Điện thoại (55 sản phẩm thực tế)
"""

MOBILES = [
    # ===== APPLE iPhone =====
    {"id": "mob_001", "name": "Apple iPhone 16 Pro Max 256GB", "brand": "Apple", "price_vnd": 34990000,
     "chip": "Apple A18 Pro", "ram_gb": 8, "storage_gb": 256, "battery_mah": 4685,
     "display": "6.9 inch Super Retina XDR OLED ProMotion 120Hz", "camera_mp": "50MP + 48MP + 12MP",
     "os": "iOS 18", "use_cases": ["premium", "photography", "gaming"],
     "highlights": "Camera Tetraprism 5x zoom, chip A18 Pro mạnh nhất, màn 6.9 inch lớn nhất"},

    {"id": "mob_002", "name": "Apple iPhone 16 Pro 128GB", "brand": "Apple", "price_vnd": 28990000,
     "chip": "Apple A18 Pro", "ram_gb": 8, "storage_gb": 128, "battery_mah": 3582,
     "display": "6.3 inch Super Retina XDR OLED 120Hz", "camera_mp": "48MP + 48MP + 12MP",
     "os": "iOS 18", "use_cases": ["premium", "photography"],
     "highlights": "iPhone nhỏ gọn cao cấp, camera 48MP góc siêu rộng, Dynamic Island"},

    {"id": "mob_003", "name": "Apple iPhone 16 128GB", "brand": "Apple", "price_vnd": 22990000,
     "chip": "Apple A18", "ram_gb": 8, "storage_gb": 128, "battery_mah": 3561,
     "display": "6.1 inch Super Retina XDR OLED 60Hz", "camera_mp": "48MP + 12MP",
     "os": "iOS 18", "use_cases": ["premium", "office"],
     "highlights": "iPhone tiêu chuẩn 2024, chip A18, Camera Control, AI iPhone"},

    {"id": "mob_004", "name": "Apple iPhone 15 128GB", "brand": "Apple", "price_vnd": 18990000,
     "chip": "Apple A16 Bionic", "ram_gb": 6, "storage_gb": 128, "battery_mah": 3349,
     "display": "6.1 inch Super Retina XDR OLED 60Hz", "camera_mp": "48MP + 12MP",
     "os": "iOS 17", "use_cases": ["office", "photography"],
     "highlights": "Dynamic Island, USB-C, camera 48MP giá hợp lý, giảm giá tốt"},

    {"id": "mob_005", "name": "Apple iPhone 14 128GB", "brand": "Apple", "price_vnd": 14990000,
     "chip": "Apple A15 Bionic", "ram_gb": 6, "storage_gb": 128, "battery_mah": 3279,
     "display": "6.1 inch Super Retina XDR OLED 60Hz", "camera_mp": "12MP + 12MP",
     "os": "iOS 17", "use_cases": ["office", "budget"],
     "highlights": "Dưới 15 triệu có iPhone bền, hiệu năng A15 tốt, hỗ trợ dài hạn"},

    {"id": "mob_006", "name": "Apple iPhone SE 2022 64GB", "brand": "Apple", "price_vnd": 9990000,
     "chip": "Apple A15 Bionic", "ram_gb": 4, "storage_gb": 64, "battery_mah": 2018,
     "display": "4.7 inch Retina LCD 60Hz", "camera_mp": "12MP",
     "os": "iOS 17", "use_cases": ["budget", "office"],
     "highlights": "iPhone rẻ nhất, chip A15 mạnh, nhỏ gọn, dành cho người thích iOS giá thấp"},

    # ===== SAMSUNG Galaxy S =====
    {"id": "mob_007", "name": "Samsung Galaxy S25 Ultra 256GB", "brand": "Samsung", "price_vnd": 33990000,
     "chip": "Snapdragon 8 Elite", "ram_gb": 12, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.9 inch Dynamic AMOLED 2X 120Hz", "camera_mp": "200MP + 50MP + 10MP + 12MP",
     "os": "Android 15 One UI 7", "use_cases": ["premium", "photography", "gaming"],
     "highlights": "Camera 200MP, S Pen tích hợp, AI Galaxy, Snapdragon 8 Elite, màn 6.9 inch"},

    {"id": "mob_008", "name": "Samsung Galaxy S25+ 256GB", "brand": "Samsung", "price_vnd": 26990000,
     "chip": "Snapdragon 8 Elite", "ram_gb": 12, "storage_gb": 256, "battery_mah": 4900,
     "display": "6.7 inch Dynamic AMOLED 2X 120Hz", "camera_mp": "50MP + 12MP + 10MP",
     "os": "Android 15", "use_cases": ["premium", "photography"],
     "highlights": "Màn lớn 6.7 inch, Galaxy AI, sạc 45W, camera 50MP chụp đêm xuất sắc"},

    {"id": "mob_009", "name": "Samsung Galaxy S25 256GB", "brand": "Samsung", "price_vnd": 22990000,
     "chip": "Snapdragon 8 Elite", "ram_gb": 12, "storage_gb": "256", "battery_mah": 4000,
     "display": "6.2 inch Dynamic AMOLED 2X 120Hz", "camera_mp": "50MP + 12MP + 10MP",
     "os": "Android 15", "use_cases": ["premium", "office"],
     "highlights": "S25 nhỏ gọn nhất, Snapdragon 8 Elite, Galaxy AI, sạc nhanh 25W"},

    {"id": "mob_010", "name": "Samsung Galaxy A55 5G 256GB", "brand": "Samsung", "price_vnd": 9990000,
     "chip": "Exynos 1480", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.6 inch Super AMOLED 120Hz", "camera_mp": "50MP + 12MP + 5MP",
     "os": "Android 14", "use_cases": ["budget", "student", "office"],
     "highlights": "Tầm trung đẳng cấp, màn AMOLED 120Hz, camera OIS, pin 5000mAh"},

    {"id": "mob_011", "name": "Samsung Galaxy A35 5G 128GB", "brand": "Samsung", "price_vnd": 7490000,
     "chip": "Exynos 1380", "ram_gb": 6, "storage_gb": 128, "battery_mah": 5000,
     "display": "6.6 inch Super AMOLED 120Hz", "camera_mp": "50MP + 8MP + 5MP",
     "os": "Android 14", "use_cases": ["budget", "student"],
     "highlights": "Dưới 8 triệu màn AMOLED 120Hz, camera tốt, bảo hành chính hãng"},

    {"id": "mob_012", "name": "Samsung Galaxy A15 4G 128GB", "brand": "Samsung", "price_vnd": 4490000,
     "chip": "MediaTek Helio G99", "ram_gb": 6, "storage_gb": 128, "battery_mah": 5000,
     "display": "6.5 inch Super AMOLED 90Hz", "camera_mp": "50MP + 5MP + 2MP",
     "os": "Android 14", "use_cases": ["budget"],
     "highlights": "Dưới 5 triệu có AMOLED, pin 5000mAh, giá rẻ nhất Samsung màn đẹp"},

    {"id": "mob_013", "name": "Samsung Galaxy Z Fold6 512GB", "brand": "Samsung", "price_vnd": 52990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 512, "battery_mah": 4400,
     "display": "7.6 inch Dynamic AMOLED gập + 6.3 inch ngoài", "camera_mp": "50MP + 12MP + 10MP",
     "os": "Android 14", "use_cases": ["premium", "creative"],
     "highlights": "Gập như cuốn sách, màn trong 7.6 inch, năng suất vô song với S Pen"},

    {"id": "mob_014", "name": "Samsung Galaxy Z Flip6 256GB", "brand": "Samsung", "price_vnd": 23990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 256, "battery_mah": 4000,
     "display": "6.7 inch Dynamic AMOLED gập + 3.4 inch Cover Screen", "camera_mp": "50MP + 12MP",
     "os": "Android 14", "use_cases": ["premium", "photography"],
     "highlights": "Gập cúc áo thời trang, màn ngoài rộng, camera selfie góc rộng"},

    # ===== XIAOMI =====
    {"id": "mob_015", "name": "Xiaomi 14 Ultra 512GB", "brand": "Xiaomi", "price_vnd": 28990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 16, "storage_gb": 512, "battery_mah": 5000,
     "display": "6.73 inch LTPO AMOLED 120Hz", "camera_mp": "50MP Leica + 50MP + 50MP + 50MP",
     "os": "Android 14 HyperOS", "use_cases": ["premium", "photography"],
     "highlights": "Camera Leica chuyên nghiệp, 4 ống kính 50MP, zoom quang 5x, sạc 90W"},

    {"id": "mob_016", "name": "Xiaomi 14 256GB", "brand": "Xiaomi", "price_vnd": 18990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 256, "battery_mah": 4610,
     "display": "6.36 inch LTPO AMOLED 120Hz", "camera_mp": "50MP Leica + 50MP + 50MP",
     "os": "Android 14 HyperOS", "use_cases": ["premium", "photography"],
     "highlights": "Snapdragon 8 Gen 3 mạnh nhất, Leica camera, nhỏ gọn, sạc 90W + 50W không dây"},

    {"id": "mob_017", "name": "Xiaomi Redmi Note 13 Pro 5G 256GB", "brand": "Xiaomi", "price_vnd": 7990000,
     "chip": "Snapdragon 7s Gen 2", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5100,
     "display": "6.67 inch AMOLED 120Hz", "camera_mp": "200MP + 8MP + 2MP",
     "os": "Android 13 MIUI 14", "use_cases": ["student", "photography", "budget"],
     "highlights": "Camera 200MP rẻ nhất thị trường, màn AMOLED 120Hz, pin 5100mAh"},

    {"id": "mob_018", "name": "Xiaomi Redmi 13C 128GB", "brand": "Xiaomi", "price_vnd": 3490000,
     "chip": "MediaTek Helio G85", "ram_gb": 4, "storage_gb": 128, "battery_mah": 5000,
     "display": "6.74 inch IPS LCD 90Hz", "camera_mp": "50MP + 2MP",
     "os": "Android 13 MIUI", "use_cases": ["budget"],
     "highlights": "Dưới 3.5 triệu, phù hợp học sinh, pin 5000mAh dùng lâu"},

    {"id": "mob_019", "name": "Xiaomi POCO X6 Pro 5G 256GB", "brand": "Xiaomi", "price_vnd": 9490000,
     "chip": "MediaTek Dimensity 8300 Ultra", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.67 inch Flow AMOLED 144Hz", "camera_mp": "64MP + 8MP + 2MP",
     "os": "Android 14 HyperOS", "use_cases": ["gaming", "student", "budget"],
     "highlights": "Gaming phone rẻ nhất 144Hz, chip mạnh, giá 9.5 triệu đáng tiền"},

    {"id": "mob_020", "name": "Xiaomi POCO F6 Pro 512GB", "brand": "Xiaomi", "price_vnd": 16990000,
     "chip": "Snapdragon 8 Gen 2", "ram_gb": 12, "storage_gb": 512, "battery_mah": 5000,
     "display": "6.67 inch LTPO AMOLED 144Hz", "camera_mp": "50MP + 8MP + 2MP",
     "os": "Android 14 HyperOS", "use_cases": ["gaming", "premium"],
     "highlights": "Snapdragon 8 Gen 2, 144Hz, sạc 67W siêu nhanh, hiệu năng/giá đỉnh"},

    # ===== OPPO =====
    {"id": "mob_021", "name": "OPPO Find X8 Pro 256GB", "brand": "OPPO", "price_vnd": 30990000,
     "chip": "MediaTek Dimensity 9300", "ram_gb": 12, "storage_gb": 256, "battery_mah": 5910,
     "display": "6.78 inch LTPO AMOLED 120Hz", "camera_mp": "50MP Hasselblad + 50MP + 50MP + 50MP",
     "os": "Android 15 ColorOS 15", "use_cases": ["premium", "photography"],
     "highlights": "Camera Hasselblad 4 ống kính, pin 5910mAh, sạc 80W, màu độc đáo"},

    {"id": "mob_022", "name": "OPPO Find X7 Ultra 256GB", "brand": "OPPO", "price_vnd": 26990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.82 inch LTPO AMOLED 120Hz", "camera_mp": "50MP Hasselblad + 48MP + 50MP",
     "os": "Android 14 ColorOS 14", "use_cases": ["premium", "photography"],
     "highlights": "Periscope zoom 6x, Hasselblad tuning, sạc không dây 50W"},

    {"id": "mob_023", "name": "OPPO Reno12 Pro 5G 256GB", "brand": "OPPO", "price_vnd": 13990000,
     "chip": "MediaTek Dimensity 7300 Energy", "ram_gb": 12, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.7 inch AMOLED 120Hz", "camera_mp": "50MP + 8MP + 50MP selfie",
     "os": "Android 14 ColorOS 14", "use_cases": ["photography", "office", "student"],
     "highlights": "Camera AI chân dung đẹp, selfie 50MP, AI Eraser, thiết kế mỏng"},

    {"id": "mob_024", "name": "OPPO A3 Pro 5G 256GB", "brand": "OPPO", "price_vnd": 7490000,
     "chip": "MediaTek Dimensity 7050", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5100,
     "display": "6.67 inch FHD+ LCD 120Hz", "camera_mp": "50MP + 2MP",
     "os": "Android 14 ColorOS 14", "use_cases": ["student", "budget"],
     "highlights": "Chống nước IP66, pin 5100mAh, 5G tầm trung giá tốt"},

    # ===== VIVO =====
    {"id": "mob_025", "name": "Vivo X100 Ultra 256GB", "brand": "Vivo", "price_vnd": 29990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 16, "storage_gb": 256, "battery_mah": 5500,
     "display": "6.82 inch LTPO AMOLED 120Hz", "camera_mp": "50MP ZEISS + 200MP + 50MP",
     "os": "Android 14 OriginOS 4", "use_cases": ["premium", "photography"],
     "highlights": "Camera ZEISS chuyên nghiệp, zoom 200MP, pin 5500mAh, sạc 80W"},

    {"id": "mob_026", "name": "Vivo V30e 5G 256GB", "brand": "Vivo", "price_vnd": 8990000,
     "chip": "Snapdragon 6 Gen 1", "ram_gb": 8, "storage_gb": 256, "battery_mah": 6000,
     "display": "6.78 inch AMOLED 120Hz", "camera_mp": "50MP ZEISS + 8MP",
     "os": "Android 14 FuntouchOS", "use_cases": ["student", "photography"],
     "highlights": "Pin 6000mAh bền nhất tầm giá, camera ZEISS, AI portrait đẹp"},

    {"id": "mob_027", "name": "Vivo Y28 5G 128GB", "brand": "Vivo", "price_vnd": 4990000,
     "chip": "MediaTek Dimensity 6300", "ram_gb": 4, "storage_gb": 128, "battery_mah": 6000,
     "display": "6.56 inch IPS 90Hz", "camera_mp": "50MP + 2MP",
     "os": "Android 14", "use_cases": ["budget"],
     "highlights": "Pin khủng 6000mAh, 5G dưới 5 triệu, dùng lâu không lo hết pin"},

    # ===== REALME =====
    {"id": "mob_028", "name": "Realme GT6 5G 512GB", "brand": "Realme", "price_vnd": 13990000,
     "chip": "Snapdragon 8s Gen 3", "ram_gb": 16, "storage_gb": 512, "battery_mah": 5500,
     "display": "6.78 inch LTPO AMOLED 144Hz", "camera_mp": "50MP Sony + 8MP + 2MP",
     "os": "Android 14 Realme UI 5.0", "use_cases": ["gaming", "student"],
     "highlights": "Snapdragon 8s Gen 3, 144Hz, sạc 120W siêu nhanh, giá 14 triệu"},

    {"id": "mob_029", "name": "Realme 12 Pro+ 5G 256GB", "brand": "Realme", "price_vnd": 9990000,
     "chip": "Snapdragon 7s Gen 2", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.7 inch AMOLED 120Hz", "camera_mp": "50MP Sony + 64MP periscope + 8MP",
     "os": "Android 14", "use_cases": ["photography", "student"],
     "highlights": "Zoom periscope giá 10 triệu, camera Sony, thiết kế da vân"},

    {"id": "mob_030", "name": "Realme C67 5G 128GB", "brand": "Realme", "price_vnd": 4490000,
     "chip": "MediaTek Dimensity 6100+", "ram_gb": 6, "storage_gb": 128, "battery_mah": 5000,
     "display": "6.72 inch IPS 90Hz", "camera_mp": "108MP + 2MP",
     "os": "Android 14", "use_cases": ["budget"],
     "highlights": "Camera 108MP giá rẻ nhất, pin 5000mAh, 5G dưới 4.5 triệu"},

    # ===== GOOGLE =====
    {"id": "mob_031", "name": "Google Pixel 9 Pro 256GB", "brand": "Google", "price_vnd": 29990000,
     "chip": "Google Tensor G4", "ram_gb": 16, "storage_gb": 256, "battery_mah": 4700,
     "display": "6.3 inch LTPO OLED 120Hz", "camera_mp": "50MP + 48MP + 48MP",
     "os": "Android 15 (Stock)", "use_cases": ["photography", "premium"],
     "highlights": "Android thuần gốc, camera AI tốt nhất, cập nhật 7 năm, Magic Eraser AI"},

    {"id": "mob_032", "name": "Google Pixel 8a 128GB", "brand": "Google", "price_vnd": 14990000,
     "chip": "Google Tensor G3", "ram_gb": 8, "storage_gb": 128, "battery_mah": 4492,
     "display": "6.1 inch OLED 120Hz", "camera_mp": "64MP + 13MP",
     "os": "Android 14", "use_cases": ["photography", "office"],
     "highlights": "Pixel giá tầm trung, camera Night Sight xuất sắc, update 7 năm"},

    # ===== ONEPLUS =====
    {"id": "mob_033", "name": "OnePlus 12 512GB", "brand": "OnePlus", "price_vnd": 22990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 16, "storage_gb": 512, "battery_mah": 5400,
     "display": "6.82 inch LTPO AMOLED 120Hz", "camera_mp": "50MP Hasselblad + 48MP + 64MP",
     "os": "Android 14 OxygenOS 14", "use_cases": ["gaming", "premium"],
     "highlights": "Sạc 100W siêu nhanh, Hasselblad camera, cảm biến vân tay siêu âm"},

    {"id": "mob_034", "name": "OnePlus Nord CE4 5G 256GB", "brand": "OnePlus", "price_vnd": 8990000,
     "chip": "Snapdragon 7 Gen 3", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5500,
     "display": "6.7 inch FHD+ AMOLED 120Hz", "camera_mp": "50MP + 8MP",
     "os": "Android 14", "use_cases": ["student", "gaming"],
     "highlights": "Snapdragon 7 Gen 3, sạc 100W nhanh nhất tầm giá, màn AMOLED"},

    # ===== SONY =====
    {"id": "mob_035", "name": "Sony Xperia 1 VI 256GB", "brand": "Sony", "price_vnd": 33990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.5 inch OLED 1-120Hz variable", "camera_mp": "52MP Zeiss + 12MP + 48MP",
     "os": "Android 14", "use_cases": ["photography", "premium", "creative"],
     "highlights": "Camera Zeiss chuyên nghiệp, zoom 170mm, quay video cinema 4K, loa stereo"},

    # ===== NOKIA =====
    {"id": "mob_036", "name": "Nokia G42 5G 128GB", "brand": "Nokia", "price_vnd": 5990000,
     "chip": "Snapdragon 480+", "ram_gb": 6, "storage_gb": 128, "battery_mah": 5000,
     "display": "6.56 inch IPS 90Hz", "camera_mp": "50MP + 2MP + 2MP",
     "os": "Android 13 Stock", "use_cases": ["budget", "office"],
     "highlights": "Có thể tự thay pin và màn hình, bảo mật tốt, Android gốc ổn định"},

    # ===== SAMSUNG MID RANGE tiếp =====
    {"id": "mob_037", "name": "Samsung Galaxy A54 5G 256GB", "brand": "Samsung", "price_vnd": 8990000,
     "chip": "Exynos 1380", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.4 inch Super AMOLED 120Hz", "camera_mp": "50MP OIS + 12MP + 5MP",
     "os": "Android 14 One UI 6", "use_cases": ["student", "photography", "office"],
     "highlights": "Camera OIS ban đêm tốt, màn AMOLED sắc nét, 4 năm cập nhật OS"},

    {"id": "mob_038", "name": "Samsung Galaxy M55 5G 256GB", "brand": "Samsung", "price_vnd": 8490000,
     "chip": "Snapdragon 7 Gen 1", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.7 inch Super AMOLED 120Hz", "camera_mp": "50MP OIS + 8MP + 2MP",
     "os": "Android 14", "use_cases": ["student", "gaming"],
     "highlights": "Snapdragon 7 Gen 1 manh cho tầm giá, màn AMOLED 6.7 inch"},

    # ===== HUAWEI =====
    {"id": "mob_039", "name": "Huawei Pura 70 Ultra 512GB", "brand": "Huawei", "price_vnd": 35990000,
     "chip": "Kirin 9010", "ram_gb": 16, "storage_gb": 512, "battery_mah": 5000,
     "display": "6.8 inch LTPO OLED 120Hz", "camera_mp": "50MP Leica + 40MP + 12MP",
     "os": "HarmonyOS 4.2", "use_cases": ["premium", "photography"],
     "highlights": "Camera Leica siêu đỉnh, ống kính biến tiêu cự, không có Google (Huawei App)"},

    # ===== THÊM CÁC MÁY PHỔ THÔNG =====
    {"id": "mob_040", "name": "OPPO A3x 4G 64GB", "brand": "OPPO", "price_vnd": 2990000,
     "chip": "Unisoc T612", "ram_gb": 4, "storage_gb": 64, "battery_mah": 5000,
     "display": "6.72 inch IPS 90Hz", "camera_mp": "8MP + 2MP",
     "os": "Android 14", "use_cases": ["budget"],
     "highlights": "Rẻ nhất thị trường dưới 3 triệu, pin bền, dùng cho cha mẹ/ông bà"},

    {"id": "mob_041", "name": "Xiaomi Redmi A3x 64GB", "brand": "Xiaomi", "price_vnd": 2590000,
     "chip": "Unisoc T606", "ram_gb": 3, "storage_gb": 64, "battery_mah": 5000,
     "display": "6.71 inch IPS 90Hz", "camera_mp": "8MP",
     "os": "Android 14", "use_cases": ["budget"],
     "highlights": "Rẻ nhất Xiaomi, màn 6.7 inch, pin 5000mAh, siêu phù hợp người cao tuổi"},

    {"id": "mob_042", "name": "Samsung Galaxy A05 64GB", "brand": "Samsung", "price_vnd": 2990000,
     "chip": "MediaTek Helio G85", "ram_gb": 4, "storage_gb": 64, "battery_mah": 5000,
     "display": "6.7 inch IPS 90Hz", "camera_mp": "50MP + 2MP",
     "os": "Android 13", "use_cases": ["budget"],
     "highlights": "Samsung giá dưới 3 triệu, màn to, pin lâu, bảo hành chính hãng"},

    {"id": "mob_043", "name": "POCO M6 Pro 5G 256GB", "brand": "Xiaomi", "price_vnd": 5990000,
     "chip": "Snapdragon 4 Gen 2", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.67 inch AMOLED 120Hz", "camera_mp": "64MP + 8MP + 2MP",
     "os": "Android 14 HyperOS", "use_cases": ["student", "budget", "gaming"],
     "highlights": "AMOLED 120Hz + 5G dưới 6 triệu, camera 64MP, đáng tiền nhất tầm này"},

    {"id": "mob_044", "name": "Vivo V29e 5G 128GB", "brand": "Vivo", "price_vnd": 7990000,
     "chip": "Snapdragon 695", "ram_gb": 8, "storage_gb": 128, "battery_mah": 4800,
     "display": "6.67 inch AMOLED 120Hz", "camera_mp": "64MP ZEISS + 8MP",
     "os": "Android 13", "use_cases": ["photography", "student"],
     "highlights": "Camera ZEISS tầm trung, AMOLED đẹp, thiết kế thời trang"},

    {"id": "mob_045", "name": "iPhone 13 128GB", "brand": "Apple", "price_vnd": 12990000,
     "chip": "Apple A15 Bionic", "ram_gb": 4, "storage_gb": 128, "battery_mah": 3227,
     "display": "6.1 inch Super Retina XDR OLED 60Hz", "camera_mp": "12MP + 12MP",
     "os": "iOS 17", "use_cases": ["office", "student"],
     "highlights": "iPhone tầm trung tốt, chip A15 mạnh lâu dài, chụp ảnh đẹp giá 13 triệu"},

    {"id": "mob_046", "name": "Samsung Galaxy S24 FE 256GB", "brand": "Samsung", "price_vnd": 14990000,
     "chip": "Exynos 2500", "ram_gb": 8, "storage_gb": 256, "battery_mah": 4700,
     "display": "6.7 inch Dynamic AMOLED 120Hz", "camera_mp": "50MP + 10MP + 12MP",
     "os": "Android 15 One UI 7", "use_cases": ["student", "photography"],
     "highlights": "Fan Edition giá tốt, Galaxy AI, camera 3 ống kính, màn AMOLED"},

    {"id": "mob_047", "name": "OPPO Find N3 Flip 512GB", "brand": "OPPO", "price_vnd": 21990000,
     "chip": "Dimensity 9200", "ram_gb": 12, "storage_gb": 512, "battery_mah": 4300,
     "display": "6.8 inch AMOLED gập + 3.26 inch ngoài", "camera_mp": "50MP Hasselblad + 48MP",
     "os": "Android 14 ColorOS 13", "use_cases": ["premium", "photography"],
     "highlights": "Flip phone nhỏ gọn Hasselblad, màn ngoài lớn 3.26 inch, sạc 44W"},

    {"id": "mob_048", "name": "Xiaomi 13T Pro 512GB", "brand": "Xiaomi", "price_vnd": 16990000,
     "chip": "MediaTek Dimensity 9200+", "ram_gb": 12, "storage_gb": 512, "battery_mah": 5000,
     "display": "6.67 inch AMOLED 144Hz", "camera_mp": "50MP Leica + 50MP + 50MP",
     "os": "Android 14 HyperOS", "use_cases": ["photography", "gaming"],
     "highlights": "Leica 3 ống kính 50MP, 144Hz, sạc 120W giá 17tr, hiệu năng/giá đỉnh"},

    {"id": "mob_049", "name": "Realme GT Neo6 5G 256GB", "brand": "Realme", "price_vnd": 10990000,
     "chip": "Snapdragon 8s Gen 3", "ram_gb": 12, "storage_gb": 256, "battery_mah": 5500,
     "display": "6.78 inch OLED 144Hz", "camera_mp": "50MP Sony + 8MP",
     "os": "Android 14 Realme UI 5", "use_cases": ["gaming", "student"],
     "highlights": "Snapdragon 8s Gen 3 mạnh nhất tầm 11tr, 144Hz OLED, sạc 100W"},

    {"id": "mob_050", "name": "Samsung Galaxy S23 FE 256GB", "brand": "Samsung", "price_vnd": 10990000,
     "chip": "Exynos 2200", "ram_gb": 8, "storage_gb": 256, "battery_mah": 4500,
     "display": "6.4 inch Dynamic AMOLED 120Hz", "camera_mp": "50MP + 8MP + 10MP",
     "os": "Android 14", "use_cases": ["student", "photography"],
     "highlights": "Samsung cao cấp tầm 11tr, camera 3 ống kính, Galaxy AI features"},

    {"id": "mob_051", "name": "OnePlus Open 512GB", "brand": "OnePlus", "price_vnd": 38990000,
     "chip": "Snapdragon 8 Gen 2", "ram_gb": 16, "storage_gb": 512, "battery_mah": 4805,
     "display": "7.82 inch LTPO3 AMOLED gập + 6.31 inch ngoài", "camera_mp": "48MP Hasselblad + 48MP + 64MP",
     "os": "Android 14 OxygenOS 14", "use_cases": ["premium", "creative"],
     "highlights": "Foldable mỏng nhất thế giới, Hasselblad camera, sạc 67W"},

    {"id": "mob_052", "name": "Motorola Edge 50 Ultra 512GB", "brand": "Motorola", "price_vnd": 16990000,
     "chip": "Snapdragon 8s Gen 3", "ram_gb": 12, "storage_gb": 512, "battery_mah": 4500,
     "display": "6.7 inch pOLED 165Hz", "camera_mp": "50MP + 50MP + 64MP",
     "os": "Android 14", "use_cases": ["photography", "gaming"],
     "highlights": "Màn 165Hz hiếm thấy, camera 3 ống kính 50MP, sạc 125W + 50W không dây"},

    {"id": "mob_053", "name": "ASUS ROG Phone 8 Pro 256GB", "brand": "ASUS", "price_vnd": 27990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 16, "storage_gb": 256, "battery_mah": 5500,
     "display": "6.78 inch AMOLED 165Hz", "camera_mp": "50MP + 13MP + 32MP",
     "os": "Android 14 ROG UI", "use_cases": ["gaming", "premium"],
     "highlights": "Gaming phone số 1, nút vai AirTrigger, tản nhiệt active, 165Hz"},

    {"id": "mob_054", "name": "Nubia Red Magic 9 Pro 256GB", "brand": "Nubia", "price_vnd": 19990000,
     "chip": "Snapdragon 8 Gen 3", "ram_gb": 16, "storage_gb": 256, "battery_mah": 6000,
     "display": "6.8 inch AMOLED 120Hz", "camera_mp": "50MP + 50MP + 8MP",
     "os": "Android 14 RedMagic OS 9", "use_cases": ["gaming"],
     "highlights": "Fan tản nhiệt nội bộ, pin 6000mAh, RGB lighting, giá gaming tốt"},

    {"id": "mob_055", "name": "Xiaomi Redmi Note 13 4G 256GB", "brand": "Xiaomi", "price_vnd": 5990000,
     "chip": "MediaTek Helio G99 Ultra", "ram_gb": 8, "storage_gb": 256, "battery_mah": 5000,
     "display": "6.67 inch AMOLED 120Hz", "camera_mp": "108MP + 8MP + 2MP",
     "os": "Android 13 MIUI 14", "use_cases": ["student", "photography", "budget"],
     "highlights": "AMOLED 120Hz dưới 6 triệu, camera 108MP, giá tốt nhất phân khúc"},
]
