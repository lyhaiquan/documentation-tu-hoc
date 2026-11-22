/* Bai thi nghiem so 1 - Muc 3.2
 * Doc khoang cach tu cam bien sieu am US-015 va hien thi len Serial Monitor
 *
 * Noi day (Bang 1.4 cua tai lieu):
 *     TRIGGER  ->  IO 02
 *     ECHO     ->  IO 04
 *     VCC -> 5V   |   GND -> GND
 *
 * Khong can thu vien ngoai.
 *
 * CANH BAO PHAN CUNG THAT: chan ECHO cua US-015 / HC-SR04 xuat muc cao 5V,
 * trong khi chan GPIO cua ESP32 chi chiu 3,3V. Tren KIT thi nghiem cua truong
 * da co mach xu ly san. Neu tu lam o nha phai chia ap bang 2 dien tro
 * (1k + 2k) tren duong ECHO, hoac dung ban HC-SR04P chay 3,3V.
 */

const int TRIG_PIN = 2;   // IO 02
const int ECHO_PIN = 4;   // IO 04

// Nhiet do moi truong, dung de hieu chinh van toc song sieu am.
// Day chinh la cau tra loi cho cau hoi Buoc 4 cua bai.
float nhietDoC = 25.0;

// Gioi han do cua US-015 theo Bang 1.3: tu 2 cm den 2,5 m
const float D_MIN = 2.0;
const float D_MAX = 250.0;

// Thoi gian cho toi da (microsecond). 30000 us ~ 5 m ca di lan ve.
const unsigned long TIMEOUT_US = 30000UL;

int lanDo = 0;

// Van toc song am trong khong khi, don vi cm/us
// v(m/s) = 331,3 + 0,606 * T(C)   ->  chia 10000 de doi ra cm/us
float vanTocAm(float tC) {
  return (331.3 + 0.606 * tC) / 10000.0;
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  Serial.println();
  Serial.println("=== Bai 1 - Muc 3.2: Do khoang cach bang US-015 ===");
  Serial.printf("Nhiet do dat: %.1f C  ->  van toc song am: %.1f m/s\n",
                nhietDoC, vanTocAm(nhietDoC) * 10000.0);
  Serial.println("Lan do | Thoi gian (us) | Khoang cach (cm)");
  Serial.println("-------+----------------+------------------");
}

void loop() {
  // 1. Phat mot xung muc cao 10 us vao chan TRIGGER
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // 2. Do do rong xung muc cao tra ve tren chan ECHO
  //    Do rong nay chinh la thoi gian song di + ve
  unsigned long thoiGian = pulseIn(ECHO_PIN, HIGH, TIMEOUT_US);

  lanDo++;

  if (thoiGian == 0) {
    Serial.printf("  %2d   |     (het gio)  |  khong co vat can trong tam do\n", lanDo);
    delay(500);
    return;
  }

  // 3. Cong thuc tinh khoang cach
  //    khoang cach = thoi gian * van toc / 2
  //    Chia 2 vi thoi gian do duoc la ca luot di VA luot ve cua song.
  float khoangCach = (thoiGian * vanTocAm(nhietDoC)) / 2.0;

  Serial.printf("  %2d   |     %6lu     |      %6.2f\n", lanDo, thoiGian, khoangCach);

  // Canh bao vung mu - phuc vu Buoc 5 cua bai
  if (khoangCach < D_MIN)
    Serial.println("       ! Nam trong VUNG MU gan (< 2 cm), ket qua khong tin cay");
  if (khoangCach > D_MAX)
    Serial.println("       ! Vuot qua tam do toi da (> 250 cm), ket qua khong tin cay");

  // So sanh voi cach tinh gan dung 0,034 cm/us thuong gap trong giao trinh
  float xapXi = thoiGian * 0.034 / 2.0;
  Serial.printf("       (neu lay 340 m/s co dinh: %.2f cm  ->  lech %.2f cm)\n",
                xapXi, xapXi - khoangCach);

  delay(500);
}
