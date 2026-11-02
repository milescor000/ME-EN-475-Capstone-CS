// --- PIN CONFIGURATION ---
const int PIN_DRIVE  = 8;  // High-side drive (connects to R_ref first)
const int PIN_RETURN = 7;  // Low-side return (connects to crucible electrode 2)
const int PIN_SENSE  = A0; // Tapped between R_ref and crucible electrode 1

// --- SAMPLING CONFIGURATION ---
// 200 Hz = 5000 microseconds per cycle (6% duty cycle, completely safe from polarization)
const unsigned long SAMPLE_INTERVAL_US = 5000; 
unsigned long lastSampleTime = 0;

void setup() {
  // 230400 baud provides over 1500 samples/sec bandwidth headroom
  Serial.begin(230400);

  // Initialize drive pins to High-Impedance on boot
  pinMode(PIN_DRIVE, INPUT);
  pinMode(PIN_RETURN, INPUT);

  // Minimal CSV header: compute voltage in Python to cut transmission payload
  Serial.println("timestamp_us,raw_adc");
}

void loop() {
  unsigned long currentTime = micros();

  // Microsecond non-blocking interval check
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US) {
    lastSampleTime = currentTime;

    // --- PHASE 1: FORWARD DRIVE ---
    pinMode(PIN_DRIVE, OUTPUT);
    pinMode(PIN_RETURN, OUTPUT);
    digitalWrite(PIN_DRIVE, HIGH);
    digitalWrite(PIN_RETURN, LOW);

    // Settle wiring and double-layer capacitance
    delayMicroseconds(40);

    // --- PHASE 2: SAMPLE ADC (~112 us duration) ---
    // Total forward pulse = 40 us settle + ~112 us read = ~152 us
    int rawADC = analogRead(PIN_SENSE);

    // --- PHASE 3: BALANCED REVERSE POLARIZATION ---
    // Reverse polarity to neutralize charge
    digitalWrite(PIN_DRIVE, LOW);
    digitalWrite(PIN_RETURN, HIGH);
    
    // Hold reverse for 150 us to balance the 152 us forward cycle
    delayMicroseconds(150);

    // --- PHASE 4: FLOAT PINS (High-Z rest for ~4700 us) ---
    pinMode(PIN_DRIVE, INPUT);
    pinMode(PIN_RETURN, INPUT);

    // --- PHASE 5: SERIAL STREAM (Compact ASCII payload: ~12 bytes) ---
    Serial.print(currentTime);
    Serial.print(",");
    Serial.println(rawADC);
  }
}