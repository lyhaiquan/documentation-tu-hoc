/* Bai thi nghiem so 1 - Vi du khoi dong: nhay LED chan 13
 * KIT Arduino ESP32 (WeMos D1 R32 / ESP32 Dev Module)
 * Noi day: IO13  ->  L1 (den LED so 1 tren KIT thi nghiem IoT)
 *
 * Cau hoi cua bai: "Tan so nhay cua den LED la bao nhieu? Giai thich tai sao?"
 * Tra loi: 1s sang + 1s tat = chu ky T = 2s  ->  f = 1/T = 0,5 Hz
 */

const int LED_PIN = 13;

void setup() {
  Serial.begin(115200);        // dat toc do cong serial
  pinMode(LED_PIN, OUTPUT);    // dat chan 13 la chan xuat tin hieu
  Serial.println("=== Bai 1 - Nhay LED chan 13 ===");
}

void loop() {
  digitalWrite(LED_PIN, HIGH); // bat LED: dua dien ap chan 13 len muc cao
  delay(1000);                 // tre 1000 ms = 1 s
  digitalWrite(LED_PIN, LOW);  // tat LED: dua dien ap chan 13 xuong muc thap
  delay(1000);                 // tre 1 s

  Serial.println("Nhay LED o chan so 13  |  T = 2s  ->  f = 0.5 Hz");
}
