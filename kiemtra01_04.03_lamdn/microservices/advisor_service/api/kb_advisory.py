"""
Knowledge Base — Tư vấn theo use-case, FAQ, so sánh, hướng dẫn chọn mua
"""

ADVISORY_DOCS = [
    # ========== HƯỚNG DẪN CHỌN LAPTOP ==========
    {
        "id": "adv_001",
        "title": "Chọn laptop cho sinh viên ngân sách dưới 15 triệu",
        "category": "laptop_guide",
        "content": """Để chọn laptop cho sinh viên với ngân sách dưới 15 triệu, cần ưu tiên:
1. CPU: Intel Core i5 thế hệ 12-13 hoặc AMD Ryzen 5 7xxx - đủ mạnh cho học tập
2. RAM: Tối thiểu 8GB, tốt nhất 16GB để chạy nhiều ứng dụng cùng lúc
3. Pin: Ưu tiên máy pin 8-10 giờ để dùng cả ngày không cần sạc
4. Màn hình: IPS Full HD 1920x1080, tốt hơn nếu có 120Hz
5. Trọng lượng: Dưới 1.8kg để di chuyển nhẹ nhàng
Gợi ý tốt nhất: Acer Aspire 5 (12tr), Dell Inspiron 15 (14tr), ASUS VivoBook 15 (13tr), HP Pavilion 15 (15tr).
Nếu có thể nâng ngân sách lên 17-20 triệu: Acer Swift Go 14 OLED (20tr) - màn OLED rất đẹp."""
    },
    {
        "id": "adv_002",
        "title": "Chọn laptop gaming dưới 25 triệu",
        "category": "laptop_guide",
        "content": """Laptop gaming dưới 25 triệu cần chú ý:
1. GPU: Minimum RTX 4060 8GB để chơi game AAA mượt mà ở 1080p/1440p
2. CPU: Intel i7/i9 hoặc AMD Ryzen 7/9 H-series hiệu năng cao
3. RAM: 16GB DDR5, có thể nâng lên 32GB
4. Màn hình: 144Hz minimum, tốt nhất 165Hz FHD hoặc QHD
5. Tản nhiệt: Cực quan trọng, cần 2-3 quạt và heat pipe tốt
Top picks: ASUS TUF Gaming F15 RTX4060 (27tr), Acer Nitro V RTX4060 (23tr), HP Victus RTX3050 (17tr).
Lưu ý: Gaming laptop nặng 2-3kg và pin chỉ 4-6 giờ, không phù hợp đi học mang theo hàng ngày."""
    },
    {
        "id": "adv_003",
        "title": "Chọn laptop doanh nghiệp, văn phòng cao cấp",
        "category": "laptop_guide",
        "content": """Laptop doanh nghiệp/văn phòng cao cấp cần:
1. Độ bền: Chuẩn MIL-SPEC 810H chịu va đập, rung, nhiệt độ khắc nghiệt
2. Pin: Tối thiểu 12-15 giờ để dùng cả ngày công tác không sạc
3. Bảo mật: Webcam IR nhận diện khuôn mặt, cảm biến vân tay, TPM 2.0, vPro
4. Màn hình: 2K/QHD+ tỉ lệ 16:10 rộng hơn, chống lóa tốt
5. RAM: 16-32GB cho đa nhiệm
6. Laptop siêu nhẹ: Dưới 1.3kg cho người hay đi công tác
Top picks: Lenovo ThinkPad X1 Carbon (48tr), HP EliteBook 840 (34tr), Dell Latitude 5540 (20tr), LG Gram 14 (30tr).
ThinkPad có bàn phím tốt nhất thế giới, LG Gram nhẹ nhất, EliteBook bảo mật tốt nhất."""
    },
    {
        "id": "adv_004",
        "title": "So sánh MacBook Air M2 vs M3 - nên mua cái nào",
        "category": "laptop_comparison",
        "content": """MacBook Air M2 vs M3 - so sánh chi tiết:
MacBook Air M2 (23tr): Chip M2 vẫn rất mạnh (2022), màn 13.6 inch Retina siêu đẹp, pin 18h, không quạt.
MacBook Air M3 (29tr): Chip M3 nhanh hơn 20-25%, hỗ trợ 2 màn hình ngoài (M2 chỉ 1 màn), WiFi 6E.
Kết luận: Nếu ngân sách eo hẹp - mua M2 vẫn đủ mạnh dùng 5-7 năm.
Nếu dùng 2 màn hình ngoài hoặc cần chip mới nhất - chọn M3.
Cả hai đều: Pin 18 giờ, không quạt, mỏng nhẹ 1.24kg, màn Liquid Retina đẹp, iMessage/AirDrop."""
    },
    {
        "id": "adv_005",
        "title": "Laptop cho lập trình viên, developer",
        "category": "laptop_guide",
        "content": """Developer cần laptop với:
1. RAM: Tối thiểu 16GB, tốt nhất 32GB để chạy Docker, VM, nhiều tab browser
2. CPU mạnh: Đa nhân, đa luồng - M3 Pro, Intel i7/i9 HX, Ryzen 9
3. SSD nhanh: PCIe 4.0, tối thiểu 512GB
4. Màn hình: 14-16 inch, 2K trở lên để nhìn code sắc nét
5. Bàn phím: Gõ thoải mái (ThinkPad nổi tiếng nhất)
6. Pin: Tốt để làm việc café/meeting
Top: MacBook Pro M3 Pro (45tr) - pin 22h, hiệu năng đỉnh; Lenovo ThinkPad X1 Carbon (48tr) - bàn phím huyền thoại;
Dell XPS 13 (36tr) - siêu nhỏ gọn; ASUS ZenBook 14 OLED (25tr) - OLED đẹp giá tốt.
Nhiều dev chọn MacBook vì Unix-based, hệ sinh thái tốt."""
    },
    {
        "id": "adv_006",
        "title": "Laptop cho thiết kế đồ họa, video editing, content creator",
        "category": "laptop_guide",
        "content": """Laptop đồ họa/video editing cần:
1. Màn hình: OLED hoặc mini-LED, độ phủ màu DCI-P3 90%+, Delta E < 2
2. GPU: RTX 4060+ để render, AI, xuất video nhanh
3. RAM: 16-32GB cho After Effects, Premiere, Photoshop
4. SSD: NVMe nhanh để làm việc với file lớn
5. CPU: Đa nhân, H-series hiệu năng cao
Top: ASUS ProArt Studiobook 16 OLED (69tr) - chuẩn màu chuyên nghiệp; MSI Stealth 16 4K OLED (59tr);
ASUS ROG Zephyrus G14 (43tr) - nhẹ mà mạnh; MacBook Pro M3 Pro (45tr) - Final Cut Pro xuất video cực nhanh.
Với video editor: MacBook M3 Pro xuất video nhanh hơn Windows laptop cùng giá nhờ chip Neural Engine."""
    },
    {
        "id": "adv_007",
        "title": "Laptop nhẹ nhất thị trường - top ultrabook dưới 1.3kg",
        "category": "laptop_guide",
        "content": """Top laptop siêu nhẹ dưới 1.3kg:
1. LG Gram 14 (30tr) - 0.99kg, nhẹ nhất thế giới, pin 22h, MIL-SPEC 7 tiêu chuẩn
2. Apple MacBook Air M3 (29tr) - 1.24kg, pin 18h, không quạt
3. Dell XPS 13 (36tr) - 1.17kg, màn OLED đẹp, nhỏ gọn nhất Dell
4. Acer Swift 5 (23tr) - 1.07kg, cảm ứng, giá tốt hơn
5. Lenovo ThinkPad X1 Carbon (48tr) - 1.12kg, bàn phím đỉnh, doanh nghiệp
6. HP Spectre x360 (43tr) - 1.41kg, gập 360, OLED touch
Lưu ý: Máy nhẹ thường đánh đổi hiệu năng, GPU rời, hoặc pin nhỏ hơn."""
    },
    {
        "id": "adv_008",
        "title": "MacBook vs Windows laptop - nên chọn gì",
        "category": "laptop_comparison",
        "content": """MacBook (macOS) vs Windows Laptop - so sánh toàn diện:
MacBook ưu điểm: Pin cực tốt (18-22h), im lặng không quạt (Air), hệ thống ổn định, ít virus, tích hợp iPhone/iPad, Final Cut Pro, Logic Pro, update dài hạn.
MacBook nhược: Giá cao, không chơi game được (game PC ít trên macOS), khó nâng cấp RAM/SSD, cổng kết nối ít.
Windows ưu điểm: Đa dạng giá/cấu hình, chơi game tốt, phần mềm nhiều (AutoCAD, game), cổng kết nối phong phú, nâng cấp được.
Windows nhược: Pin thường ngắn hơn, nặng hơn, cần cài driver, bảo mật phức tạp hơn.
Nên chọn MacBook nếu: Dùng iPhone, làm việc sáng tạo, cần pin lâu, ghét cài lại Windows.
Nên chọn Windows nếu: Chơi game, cần phần mềm đặc thù, ngân sách linh hoạt, lập trình backend/game."""
    },

    # ========== HƯỚNG DẪN CHỌN ĐIỆN THOẠI ==========
    {
        "id": "adv_009",
        "title": "Chọn điện thoại cho học sinh sinh viên dưới 5 triệu",
        "category": "mobile_guide",
        "content": """Điện thoại học sinh/sinh viên dưới 5 triệu:
1. Ưu tiên pin to (5000mAh+) để dùng cả ngày học
2. Màn hình IPS hoặc AMOLED, 90Hz trở lên
3. Camera: 48-64MP đủ tốt để chụp tài liệu, selfie
4. RAM: Tối thiểu 4GB, tốt nhất 6-8GB
5. Bộ nhớ: 128GB để lưu video học, app
Top picks dưới 5tr: Xiaomi Redmi A3x (3tr), Samsung Galaxy M15 (4tr), Realme C67 5G (4.5tr), POCO M6 Pro 5G (6tr - hơi vượt ngân sách nhưng xứng đáng).
Lưu ý: Máy dưới 3 triệu thường dùng chip yếu, chỉ đủ dùng cơ bản, không chơi game nặng được."""
    },
    {
        "id": "adv_010",
        "title": "Điện thoại chụp ảnh đẹp nhất tầm 10-15 triệu",
        "category": "mobile_guide",
        "content": """Camera phone tốt nhất tầm 10-15 triệu:
1. Xiaomi Redmi Note 13 Pro 5G (8tr) - Camera 200MP giá rẻ nhất
2. Samsung Galaxy A55 5G (10tr) - Camera OIS tốt, màn AMOLED
3. Realme 12 Pro+ (10tr) - Zoom periscope cực hiếm tầm giá
4. Google Pixel 8a (15tr) - AI camera tốt nhất Android tầm giá
5. iPhone 14 (15tr) - Camera iPhone tổng thể xuất sắc, video siêu mượt
6. Samsung Galaxy A54 (9tr) - OIS, chụp đêm tốt
Tiêu chí camera tốt: OIS (chống rung), khẩu độ f/1.8 trở xuống, chụp đêm tốt, AI xử lý ảnh.
Google Pixel nổi tiếng AI camera xử lý ảnh đẹp nhất dù spec không khủng."""
    },
    {
        "id": "adv_011",
        "title": "iPhone nào đáng mua nhất 2024 theo từng tầm giá",
        "category": "mobile_guide",
        "content": """iPhone đáng mua theo tầm giá 2024:
Dưới 10 triệu: iPhone SE 2022 (10tr) - chip A15 mạnh, nhỏ gọn, nhưng pin yếu, màn HD
Tầm 13-15 triệu: iPhone 13 (13tr) - 5G, camera tốt, hỗ trợ iOS dài hạn, đáng mua nhất
Tầm 15-20 triệu: iPhone 14 (15tr) - Dynamic Island dòng tiêu chuẩn, 48MP camera, USB-C
Tầm 20-25 triệu: iPhone 15 (19tr) - USB-C, camera 48MP, Dynamic Island
Tầm 25-35 triệu: iPhone 16 (23tr) - chip A18, AI features, Camera Control
Trên 35 triệu: iPhone 16 Pro (29tr) hoặc Pro Max (35tr) - Tetraprism zoom, ProMotion 120Hz, chip A18 Pro
Lưu ý: iPhone giữ giá trị tốt, hỗ trợ iOS 6+ năm, hệ sinh thái Apple liền mạch."""
    },
    {
        "id": "adv_012",
        "title": "Samsung vs iPhone - nên mua điện thoại nào",
        "category": "mobile_comparison",
        "content": """Samsung Android vs iPhone iOS - so sánh toàn diện:
iPhone ưu điểm: iOS mượt mà, bảo mật tốt nhất, camera video xuất sắc, hệ sinh thái Apple (Mac, iPad, Watch), cập nhật 6 năm, giữ giá tốt.
iPhone nhược: Giá cao, không hỗ trợ thẻ nhớ, cổng Lightning/USB-C tùy model, tùy biến ít.
Samsung ưu điểm: Màn AMOLED đẹp nhất Android, camera đa năng (zoom 100x Ultra), Android tùy biến, giá đa dạng từ 3tr-53tr.
Samsung nhược: One UI nhiều bloatware, tản nhiệt mid-range yếu hơn, cập nhật OS 4 năm.
Chọn iPhone nếu: Có Mac/iPad/AirPods, cần bảo mật cao, quay video chuyên nghiệp.
Chọn Samsung nếu: Muốn màn hình đẹp, dùng Android, ngân sách linh hoạt, cần zoom xa."""
    },
    {
        "id": "adv_013",
        "title": "Điện thoại gaming tốt nhất 2024",
        "category": "mobile_guide",
        "content": """Gaming phone top 2024:
Flagship gaming: ASUS ROG Phone 8 Pro (28tr) - AirTrigger, 165Hz, tản nhiệt active; Nubia Red Magic 9 Pro (20tr) - fan tản nhiệt, pin 6000mAh.
Tầm cao: iPhone 16 Pro (29tr) - GPU Apple A18 Pro cực mạnh, không lag; Samsung Galaxy S25 Ultra (34tr) - Snapdragon 8 Elite.
Tầm trung gaming: POCO F6 Pro (17tr) - Snapdragon 8 Gen 2, 144Hz; Realme GT Neo6 (11tr) - 8s Gen 3, 100W.
Tầm thấp: POCO X6 Pro (9.5tr) - Dimensity 8300 Ultra, 144Hz; OnePlus Nord CE4 (9tr) - Snapdragon 7 Gen 3.
Tiêu chí gaming phone: Chip mạnh nhất tầm giá, màn ≥120Hz, pin ≥4500mAh, sạc nhanh, tản nhiệt tốt."""
    },
    {
        "id": "adv_014",
        "title": "Điện thoại pin khủng dùng cả ngày không lo cạn",
        "category": "mobile_guide",
        "content": """Điện thoại pin lớn nhất 2024:
1. Vivo Y28 5G (5tr) - Pin 6000mAh, dùng 2 ngày không cần sạc
2. Nubia Red Magic 9 Pro (20tr) - Pin 6000mAh gaming phone
3. Vivo V30e (9tr) - Pin 6000mAh + AMOLED
4. Realme C67 5G (4.5tr) - Pin 5000mAh giá rẻ
5. Samsung Galaxy A55 (10tr) - Pin 5000mAh + sạc 25W
6. Xiaomi Redmi Note 13 Pro (8tr) - Pin 5100mAh + sạc 67W
Mẹo: Pin lớn nhưng sạc chậm cũng không tiện - nên chọn máy có sạc 45W+ để thời gian sạc nhanh.
Pin 5000mAh thường dùng được 1.5-2 ngày với tần suất thông thường."""
    },
    {
        "id": "adv_015",
        "title": "Điện thoại nào nên mua cho người cao tuổi cha mẹ",
        "category": "mobile_guide",
        "content": """Điện thoại cho cha mẹ/ông bà cần:
1. Màn hình to, chữ lớn dễ đọc: ≥6.5 inch
2. Pin lâu để không phải sạc thường xuyên: ≥5000mAh
3. Đơn giản, ít bloatware: Samsung One UI hay iOS dễ dùng nhất
4. Giá vừa phải không cần đắt
5. Nút bấm rõ ràng, âm lượng to
Top choices: iPhone SE 2022 (10tr) - iOS đơn giản nếu họ quen dùng; Samsung Galaxy A05 (3tr) - giá rẻ màn to;
Vivo Y28 5G (5tr) - pin khủng 6000mAh, không lo hết pin; Redmi A3x (2.6tr) - siêu rẻ, pin ổn.
Lưu ý: Tránh chọn máy quá nhiều tính năng phức tạp, ưu tiên ổn định và đơn giản."""
    },
    {
        "id": "adv_016",
        "title": "Điện thoại gập đáng mua nhất 2024 - foldable phone",
        "category": "mobile_guide",
        "content": """Foldable phone đáng mua 2024:
Loại sách (dạng tablet): Samsung Galaxy Z Fold6 (53tr) - nhất thị trường, S Pen, màn trong 7.6 inch; OnePlus Open (39tr) - mỏng nhất, giá tốt hơn.
Loại cúc áo (flip): Samsung Galaxy Z Flip6 (24tr) - thời trang, màn ngoài 3.4 inch; OPPO Find N3 Flip (22tr) - Hasselblad camera; Motorola Razr 50 Ultra (22tr).
Foldable ưu điểm: Đa nhiệm tốt (2 app cùng lúc), cầm nhỏ gọn khi đóng, màn hình lớn khi mở.
Foldable nhược: Giá rất cao, bản lề dễ bám bụi, màn trong dễ trầy, pin thường nhỏ hơn.
Khuyến nghị: Chỉ mua foldable khi ngân sách trên 22 triệu và thực sự cần đa nhiệm cao."""
    },
    {
        "id": "adv_017",
        "title": "Chọn điện thoại Xiaomi - dòng nào phù hợp",
        "category": "mobile_guide",
        "content": """Hệ sinh thái Xiaomi phù hợp với mọi ngân sách:
Dưới 3tr: Redmi A3x, Redmi A3 - cơ bản, pin lâu
3-6tr: Redmi 13C, Redmi Note 13 4G, POCO M6 Pro 5G - đáng tiền nhất phân khúc
6-10tr: Redmi Note 13 Pro 5G - camera 200MP, AMOLED; POCO X6 Pro - gaming 144Hz
10-17tr: POCO F6 Pro - Snapdragon 8 Gen 2, flagship killer; Xiaomi 13T Pro - Leica camera
Trên 17tr: Xiaomi 14 - Snapdragon 8 Gen 3, Leica; Xiaomi 14 Ultra - camera Leica 4 ống kính
Lưu ý: MIUI/HyperOS có nhiều quảng cáo mặc định, cần tắt trong cài đặt. Bảo hành Việt Nam đang mở rộng."""
    },
    {
        "id": "adv_018",
        "title": "Điện thoại 5G giá rẻ nhất - dưới 6 triệu có 5G không",
        "category": "mobile_guide",
        "content": """Điện thoại 5G giá rẻ nhất thị trường 2024:
Dưới 5tr có 5G: Vivo Y28 5G (5tr), Realme C67 5G (4.5tr), Redmi 13C 5G (4.9tr), Samsung Galaxy A25 5G (5tr)
5-7tr có 5G chất lượng: POCO M6 Pro 5G (6tr) - AMOLED 120Hz; Samsung Galaxy A35 5G (7.5tr); OnePlus Nord CE4 (9tr)
5G có thực sự cần thiết không? Ở Việt Nam 5G đang mở rộng nhưng chưa phủ hết. Nếu sống thành phố lớn - có 5G tốt hơn.
Máy 5G thường tốn pin hơn 4G khi dùng 5G liên tục. Có thể tắt 5G để tiết kiệm pin."""
    },
    {
        "id": "adv_019",
        "title": "Nên mua điện thoại cũ hay mới - tư vấn thực tế",
        "category": "mobile_guide",
        "content": """Mua điện thoại cũ vs mới - phân tích thực tế:
Mua mới ưu điểm: Bảo hành chính hãng 12-24 tháng, pin mới 100%, không có lỗi ẩn, cập nhật OS mới nhất, an tâm.
Mua cũ ưu điểm: Tiết kiệm 30-50% ngân sách, mua được máy cấu hình cao hơn cùng tiền, iPhone cũ vẫn bền.
Lưu ý khi mua cũ: Kiểm tra IMEI, dung lượng pin (Android: AccuBattery, iOS: Cài đặt/Pin), test camera các chế độ, kiểm tra màn hình spots, test loa micro, kiểm tra iCloud/Google Account đã xóa chưa.
Nên mua iPhone cũ vì: Giữ giá, bền, cập nhật iOS lâu. Tránh Samsung cũ vì pin xuống nhanh."""
    },
    {
        "id": "adv_020",
        "title": "Camera điện thoại - giải thích megapixel, khẩu độ, OIS",
        "category": "mobile_education",
        "content": """Hiểu về camera điện thoại:
Megapixel (MP): Không phải cứ MP cao là ảnh đẹp. 200MP chia thành pixel nhỏ, chụp tối kém. Camera xử lý AI quan trọng hơn.
Khẩu độ (f/số): f/1.8 tốt hơn f/2.2. Số càng nhỏ = thu sáng tốt = chụp đêm đẹp hơn.
OIS (Optical Image Stabilisation): Chống rung quang học - ảnh và video ít bị nhòe khi di chuyển, quan trọng cho video và chụp đêm.
Zoom quang vs zoom số: Zoom quang (2x, 5x, 10x) giữ chất lượng ảnh. Zoom số làm mờ ảnh.
Periscope zoom: Kỹ thuật zoom quang xa nhất, thường 5x-10x quang học, hay thấy ở flagship.
AI camera: Google Pixel, Apple iPhone dùng AI xử lý ảnh rất tốt dù sensor không phải to nhất."""
    },
    {
        "id": "adv_021",
        "title": "Sạc nhanh điện thoại - 65W, 100W, 120W khác gì nhau",
        "category": "mobile_education",
        "content": """Tìm hiểu sạc nhanh điện thoại:
Sạc thường (18-25W): Sạc đầy 1.5-2 giờ. Phổ biến ở Samsung, iPhone.
Sạc nhanh 45-67W: Sạc đầy 1-1.5 giờ. Xiaomi, OPPO tầm trung.
Sạc siêu nhanh 80-120W: Sạc đầy 30-45 phút. Xiaomi 14, OPPO Find X8, Realme GT6.
Sạc 240W (Xiaomi): Sạc đầy chỉ 9 phút - nhanh nhất thế giới hiện tại.
Sạc không dây: 15W (iPhone), 50W (Xiaomi), 80W (IQOO). Tiện nhưng chậm hơn có dây.
Lưu ý: Sạc nhanh quá nhiều lần làm pin chai nhanh hơn. Tốt nhất là không sạc qua đêm thường xuyên.
Apple chủ động hạn chế sạc theo lịch ngủ để bảo vệ pin."""
    },
    {
        "id": "adv_022",
        "title": "Chip điện thoại - Snapdragon, Exynos, Dimensity khác gì nhau",
        "category": "mobile_education",
        "content": """So sánh chip điện thoại phổ biến:
Snapdragon (Qualcomm): Mạnh nhất Android, hiệu năng/watt tốt, GPU Adreno tốt cho game, 5G modem tốt. Snapdragon 8 Gen 3 > 8s Gen 3 > 7 Gen 3 > 6 Gen 1.
Dimensity (MediaTek): Giá rẻ hơn Snapdragon cùng cấp, nhiều tính năng AI, Dimensity 9300 = flagship. Chỉ có điểm trừ là nóng hơn chút.
Exynos (Samsung): Samsung tự làm, thường yếu hơn Snapdragon cùng thời, CPU tốt nhưng GPU Xclipse yếu hơn Adreno.
Apple A-series: Mạnh nhất toàn thế giới, vượt trội Snapdragon 20-30%, Neural Engine AI đỉnh.
Kirin (Huawei): Tự sản xuất, không có 5G do lệnh cấm Mỹ, chỉ dùng trên thiết bị Huawei."""
    },
    {
        "id": "adv_023",
        "title": "Màn hình điện thoại - OLED vs LCD vs AMOLED khác gì",
        "category": "mobile_education",
        "content": """So sánh công nghệ màn hình điện thoại:
LCD (IPS): Hiển thị màu sắc chính xác, dùng đèn nền, đen không thực sự đen, tiêu thụ pin nhiều hơn, giá rẻ.
OLED: Tự phát sáng từng pixel, đen tuyệt đối (tắt pixel), tiết kiệm pin khi hiển thị nội dung tối, màu sắc rực rỡ. Nhược: Ghosting, màu đôi khi quá bão hòa.
AMOLED: Là OLED của Samsung, chất lượng tương đương OLED thông thường, tốt cho độ sáng cao.
Super AMOLED: AMOLED thế hệ mới, sáng hơn, tiết kiệm điện hơn, ít phản chiếu ánh sáng mặt trời.
LTPO: Màn hình adaptive refresh rate, tự động 1-120Hz tùy nội dung, tiết kiệm pin tốt nhất.
Khuyến nghị: Ưu tiên AMOLED/OLED nếu ngân sách cho phép. LCD vẫn tốt cho tầm giá thấp."""
    },
    {
        "id": "adv_024",
        "title": "Top 5 điện thoại đáng mua nhất tháng 4/2024 theo từng tầm giá",
        "category": "mobile_ranking",
        "content": """Top điện thoại đáng mua tháng 4/2024:
Dưới 5tr: POCO M6 Pro 5G (6tr nhưng sale 5.5tr) - AMOLED 120Hz, Snapdragon, 5G; Realme C67 5G (4.5tr).
5-10tr: Xiaomi Redmi Note 13 Pro 5G (8tr) - Camera 200MP, AMOLED, sạc 67W; Samsung Galaxy A55 5G (10tr) - Camera OIS.
10-15tr: Google Pixel 8a (15tr) - AI camera đỉnh, stock Android; iPhone 14 (15tr) - bền, hệ sinh thái Apple.
15-25tr: Xiaomi 13T Pro (17tr) - Leica 3 ống kính, 120W; Samsung Galaxy S24 FE (15tr) - flagship feel.
25-35tr: iPhone 16 (23tr) - AI features; Samsung Galaxy S25 (23tr) - Snapdragon 8 Elite; Xiaomi 14 (19tr).
Trên 35tr: iPhone 16 Pro Max (35tr) hoặc Samsung S25 Ultra (34tr) - đỉnh cao nhất."""
    },
    {
        "id": "adv_025",
        "title": "Cách bảo quản pin điện thoại và laptop bền lâu",
        "category": "tips",
        "content": """Mẹo bảo quản pin bền lâu:
Cho điện thoại/laptop:
1. Không để pin xuống dưới 20% thường xuyên - gây hao mòn pin nhanh
2. Không sạc đầy 100% mọi lúc - giữ 20-80% là lý tưởng
3. Tránh sạc qua đêm liên tục (nhiều thiết bị đã có tính năng optimize charging)
4. Tránh để thiết bị nóng khi sạc - nhiệt độ cao phá hủy pin
5. Dùng cáp sạc chính hãng hoặc MFi/USB-IF certified
6. iPhone có chế độ Optimized Battery Charging - bật lên
7. Android: Nhiều máy có Smart Charging - bật lên
Thực tế: Pin lithium-ion sau 500 chu kỳ sạc đầy còn ~80% dung lượng. Nếu giữ 20-80% thì 1 chu kỳ = 2 lần sạc từ 40% lên 80%, kéo dài tuổi thọ pin gấp đôi."""
    },
    {
        "id": "adv_026",
        "title": "So sánh laptop gaming: Lenovo Legion vs ASUS ROG vs Acer Predator vs MSI",
        "category": "laptop_comparison",
        "content": """So sánh 4 hãng gaming laptop top đầu:
Lenovo Legion: Tản nhiệt ColdFront tốt nhất, màn QHD165Hz đẹp, tỉ lệ giá/hiệu năng tốt nhất, hỗ trợ nâng cấp RAM/SSD dễ. Best: Legion 5 Pro, Legion 7.
ASUS ROG: Thiết kế đẹp mắt nhất, phần mềm Armoury Crate nhiều tính năng, màn sắc nét, đa dạng từ gaming đến creator. Best: ROG Zephyrus G14 (mỏng nhẹ), ROG Strix G16 (hiệu năng).
Acer Predator: Tản nhiệt AeroBlade 5th gen mạnh, màn 250Hz+ nhiều model, giá cạnh tranh. Nhược: nặng và to hơn. Best: Predator Helios 16/18.
MSI: Thiết kế gaming cổ điển, màn 4K OLED ở một số model, dòng Creator cho thiết kế tốt. Best: MSI Titan GT77 (cực mạnh), MSI Stealth (mỏng).
Khuyến nghị: Budget mid-range → Lenovo Legion 5 Pro; Muốn mỏng nhẹ → ASUS ROG Zephyrus G14."""
    },
    {
        "id": "adv_027",
        "title": "Laptop dưới 10 triệu có đáng mua không - thực tế",
        "category": "laptop_guide",
        "content": """Laptop dưới 10 triệu - thực tế có nên mua không:
Chip tầm này: Core i3 thế hệ 10-12, Celeron N, Pentium - đủ cho văn phòng, học online, xem phim.
KHÔNG làm được: Chơi game nặng, đồ họa, render video, chạy máy ảo, lập trình nhiều tool đồng thời.
LÀM ĐƯỢC: Word/Excel/PowerPoint, Zoom/Google Meet, xem phim/YouTube, lướt web 10+ tab, học lập trình cơ bản.
Top dưới 10tr: Acer Aspire 3 i3 (9tr), Lenovo IdeaPad 1 Celeron (7tr), ASUS VivoBook Go Ryzen 3 (9tr).
Lời khuyên: Nếu chỉ cần văn phòng - mua được. Nếu cần mạnh hơn - tiết kiệm thêm lên 13-15tr mua i5 đáng hơn nhiều."""
    },
    {
        "id": "adv_028",
        "title": "Nên mua laptop hay iPad cho sinh viên",
        "category": "laptop_comparison",
        "content": """Laptop vs iPad cho sinh viên:
iPad (kèm bàn phím) ưu: Nhẹ hơn, pin tốt hơn, touches/Apple Pencil tốt cho ghi chú, xem phim. Giá iPad + bàn phím: 15-25tr.
iPad nhược: Không cài được phần mềm Windows/Linux, không làm được nhiều task lập trình, hạn chế file management, không xử lý được file Office phức tạp.
Laptop ưu: Hệ điều hành đầy đủ, làm được mọi thứ, phần mềm đa dạng, phù hợp lập trình, thiết kế, kế toán.
Khuyến nghị: Nếu học ngành Kỹ thuật, CNTT, Kinh tế, Kế toán → cần laptop thật sự.
Nếu học ngành Nghệ thuật, Văn học, Y khoa → iPad + bàn phím + Apple Pencil có thể đủ.
Tốt nhất: Laptop laptop cho học sâu, iPad bổ sung nếu cần ghi chú tay."""
    },
    {
        "id": "adv_029",
        "title": "RAM 8GB vs 16GB - có cần nâng cấp không",
        "category": "laptop_education",
        "content": """RAM 8GB vs 16GB laptop - khi nào cần nâng cấp:
RAM 8GB đủ dùng cho: Văn phòng, xem phim, lướt web 10-15 tab, học online, lập trình đơn giản.
RAM 8GB KHÔNG đủ cho: Chạy Docker/VM, mở 20+ tab Chrome, Photoshop + Premiere cùng lúc, Android Studio + nhiều app.
RAM 16GB: Khuyến nghị cho mọi người dùng 2024 vì phần mềm ngày càng nặng.
RAM 32GB: Dành cho developer chạy nhiều VM, designer dùng phần mềm nặng, chỉnh video 4K.
MacBook RAM: Khác với RAM thường - RAM MacBook M-series dùng chung với GPU, 8GB M3 tương đương 16GB Windows laptop. Cân nhắc trước khi so sánh."""
    },
    {
        "id": "adv_030",
        "title": "SSD vs HDD - tại sao laptop cần SSD",
        "category": "laptop_education",
        "content": """SSD vs HDD - tại sao SSD quan trọng:
HDD (ổ cứng xoay): Chậm (100-150MB/s đọc), dễ hỏng khi va đập, tiêu thụ pin nhiều, nặng. Giá rẻ.
SSD SATA: Nhanh hơn HDD 5-6 lần (500MB/s), bền hơn, nhẹ hơn.
SSD NVMe PCIe 3.0: 2000-3500MB/s, khởi động Windows 10-15 giây.
SSD NVMe PCIe 4.0: 5000-7000MB/s, chuẩn cao cấp 2023-2024.
SSD NVMe PCIe 5.0: 10000MB/s+, mới nhất 2024.
Kết luận: Laptop 2024 phải có SSD NVMe, không nên mua máy chỉ có HDD. Ít nhất 256GB, tốt nhất 512GB.
Mẹo: Nếu máy có HDD - thay SSD là nâng cấp rẻ nhất và hiệu quả nhất."""
    },
]
