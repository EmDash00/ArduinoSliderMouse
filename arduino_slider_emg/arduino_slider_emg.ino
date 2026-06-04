// Struct to hold all sensor data
struct SensorData {
  int emg1;      // bicep EMG
  int emg2;      // tricep EMG
  int slider;    // slider position
};

// Slider setup (A2)
constexpr int
  analogInPinSlider = A2,
  analogInPinEMG1 = A0, // bicep
  analogInPinEMG2 = A1; // tricep
                        //
SensorData data;

void setup() {
  Serial.begin(115200);
}

void loop() {
  // Create struct instance and populate with readings
  data.slider = analogRead(analogInPinSlider);     // Slider min 0-max 674
  data.emg1 = analogRead(analogInPinEMG1);         // EMG1, A0
  data.emg2 = analogRead(analogInPinEMG2);         // EMG2, A1

  sendToPC(data);
}

void sendToPC(SensorData& data) {
  // Cast the struct pointer to byte pointer and send
  Serial.write((byte*)&data, sizeof(SensorData));  // Sends 24 bytes (3 doubles × 8 bytes)
  Serial.write('\n');
}
