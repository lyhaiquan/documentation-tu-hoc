/* Bai thi nghiem so 1 - Muc 3.1
 * Doc nhiet do / do am tu DHT11 va hien thi len Serial Monitor
 *
 * Noi day (Bang 1.1 cua tai lieu):
 *     Chan DATA cua module DHT-11  ->  IO 04 cua ESP32
 *     VCC -> 5V (chan VIN)   |   GND -> GND
 *
 * Thu vien can them trong Arduino IDE (Library Manager):
 *     "DHT sensor library"        (Adafruit)
 *     "Adafruit Unified Sensor"   (Adafruit)
 *
 * LUU Y KHI MO PHONG: Wokwi chi co linh kien DHT22, khong co DHT11.
 * Doi mot dong duy nhat ben duoi khi chuyen sang KIT that:
 *     KIT that  ->  #define DHTTYPE DHT11   (dang dat san o duoi)
 *     Wokwi     ->  #define DHTTYPE DHT22
 */

#include "DHT.h"

#define DHTPIN   4          // IO 04 theo Bang 1.1
#define  DHTTYPE  DHT11      // DHT11 - dung cho KIT that (Wokwi thi doi thanh DHT22)

DHT dht(DHTPIN, DHTTYPE);

int lanDo = 0;

void setup() {
  Serial.begin(115200);     // Buoc 4 cua bai: thu doi thanh 9600 roi doc lai
  dht.begin();

  Serial.println();
  Serial.println("=== Bai 1 - Muc 3.1: Doc DHT tren chan IO4 ===");
  Serial.println("Lan do | Nhiet do (C) | Nhiet do (F) | Do am (%RH)");
  Serial.println("-------+--------------+--------------+------------");
}

void loop() {
  // DHT11 co toc do lay mau khong qua 1 Hz -> doc cach nhau it nhat 2 giay
  delay(2000);

  float h = dht.readHumidity();        // do am tuong doi, %RH
  float t = dht.readTemperature();     // nhiet do, do C
  float f = dht.readTemperature(true); // nhiet do, do F

  // Cam bien khong tra ve du lieu -> gia tri NaN
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("Loi: khong doc duoc DHT. Kiem tra day DATA, nguon 5V, dung chan IO4?");
    return;
  }

  lanDo++;

  // Chi so nong buc (heat index) - nhiet do cam nhan duoc
  float hiC = dht.computeHeatIndex(t, h, false);

  Serial.printf("  %2d   |    %6.1f    |    %6.1f    |   %6.1f\n", lanDo, t, f, h);
  Serial.printf("       -> Cam giac nong buc (heat index): %.1f C\n", hiC);

  // Kiem tra dai hoat dong cua DHT11 theo tai lieu: 0..50 C, 20..95 %RH
  if (t < 0 || t > 50)  Serial.println("       ! Nhiet do ngoai dai do cua DHT11 (0..50 C)");
  if (h < 20 || h > 95) Serial.println("       ! Do am ngoai dai do cua DHT11 (20..95 %RH)");
}
