# Bài thí nghiệm số 1 — Cảm biến & ESP32 (PTIT, môn IoT và ứng dụng)

Bộ mô phỏng để tập trước ở nhà, không cần mua linh kiện.

## Chạy trên Wokwi (khuyên dùng)

1. Mở https://wokwi.com → **New Project** → chọn **ESP32**.
2. Dán nội dung `sketch.ino` vào tab code.
3. Mở tab `diagram.json`, xóa hết, dán nội dung `diagram.json` của cùng thư mục.
4. Thư mục nào có `libraries.txt` thì tạo thêm tab tên `libraries.txt` và dán vào.
5. Bấm nút ▶ (Start). Serial Monitor hiện ở dưới.

| Thư mục | Nội dung | Chân nối |
|---|---|---|
| `01-blink` | Ví dụ khởi động: nháy LED | IO13 → L1 |
| `02-dht11` | Mục 3.1 — nhiệt độ, độ ẩm | DATA → IO4 |
| `03-sieu-am` | Mục 3.2 — đo khoảng cách | TRIG → IO2, ECHO → IO4 |

## Khi chuyển sang KIT thật

- `02-dht11/sketch.ino`: đổi `#define DHTTYPE DHT22` thành `DHT11`.
  (Wokwi không có linh kiện DHT11, chỉ có DHT22 — code còn lại giống hệt.)
- Arduino IDE: Tools → Board → **ESP32 Dev Module**, chọn đúng cổng COM.
- Thư viện cần cài: *DHT sensor library* + *Adafruit Unified Sensor* (Adafruit).

## Mô phỏng offline

Mở `mo-phong.html` bằng trình duyệt — bàn thí nghiệm ảo chạy đúng công thức
của hai sketch trên, kéo thanh trượt để đổi nhiệt độ / khoảng cách và xem
Serial Monitor phản ứng. Dùng để trả lời các câu hỏi trong báo cáo
(vùng mù, công thức tính khoảng cách, ảnh hưởng của nhiệt độ).
