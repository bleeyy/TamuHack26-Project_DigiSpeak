
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

Adafruit_MPU6050 mpu;

// Flex sensor analog pins
const int FLEX_PINS[5] = {A0, A1, A2, A3, A4};

const unsigned long SAMPLE_INTERVAL_MS = 20; // 50 Hz
unsigned long lastSampleTime = 0;

float rollDeg = 0.0f;
float pitchDeg = 0.0f;
float yawDeg = 0.0f;

float previousGyroZ = 0.0f;
unsigned long previousIMUTime = 0;

const float RAD_TO_DEG_F = 57.2957795f;
const float GRAVITY = 9.80665f;

void setup() {
  Serial.begin(115200);

  // Initialize I2C and the MPU-6050.
  Wire.begin();

  if (!mpu.begin()) {
    // Send errors to the serial monitor, not as data rows.
    Serial.println("# ERROR: MPU6050 not detected");
    while (true) {
      delay(100);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // Initialize analog inputs.
  for (int i = 0; i < 5; i++) {
    pinMode(FLEX_PINS[i], INPUT);
  }

  // Get initial acceleration to estimate starting tilt.
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  rollDeg = atan2f(
      accel.acceleration.y,
      accel.acceleration.z
  ) * RAD_TO_DEG_F;

  pitchDeg = atan2f(
      -accel.acceleration.x,
      sqrtf(
          accel.acceleration.y * accel.acceleration.y +
          accel.acceleration.z * accel.acceleration.z
      )
  ) * RAD_TO_DEG_F;

  previousIMUTime = micros();
}

void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime < SAMPLE_INTERVAL_MS) {
    return;
  }

  lastSampleTime = now;

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  // Convert acceleration from m/s^2 to g.
  float ax = accel.acceleration.x / GRAVITY;
  float ay = accel.acceleration.y / GRAVITY;
  float az = accel.acceleration.z / GRAVITY;

  // Accelerometer-based tilt estimates.
  float accelRoll = atan2f(
      accel.acceleration.y,
      accel.acceleration.z
  ) * RAD_TO_DEG_F;

  float accelPitch = atan2f(
      -accel.acceleration.x,
      sqrtf(
          accel.acceleration.y * accel.acceleration.x * 0.0f +
          accel.acceleration.y * accel.acceleration.y +
          accel.acceleration.z * accel.acceleration.z
      )
  ) * RAD_TO_DEG_F;

  // Integrate gyroscope angular velocity.
  // Gyro values from this library are in radians/second.
  unsigned long currentMicros = micros();
  float dt = (currentMicros - previousIMUTime) / 1000000.0f;
  previousIMUTime = currentMicros;

  if (dt > 0.0f && dt < 0.2f) {
    float gx = gyro.gyro.x * RAD_TO_DEG_F;
    float gy = gyro.gyro.y * RAD_TO_DEG_F;
    float gz = gyro.gyro.z * RAD_TO_DEG_F;

    // Complementary filter for roll and pitch.
    rollDeg = 0.98f * (rollDeg + gx * dt)
            + 0.02f * accelRoll;

    pitchDeg = 0.98f * (pitchDeg + gy * dt)
             + 0.02f * accelPitch;

    // Yaw is gyro-integrated and will drift over time.
    yawDeg += gz * dt;
  }

  // Output acceleration (g), angles (degrees), then five flex readings.
  Serial.print(ax, 4); Serial.print(',');
  Serial.print(ay, 4); Serial.print(',');
  Serial.print(az, 4); Serial.print(',');

  Serial.print(rollDeg, 2); Serial.print(',');
  Serial.print(pitchDeg, 2); Serial.print(',');
  Serial.print(yawDeg, 2);

  for (int i = 0; i < 5; i++) {
    Serial.print(',');
    Serial.print(analogRead(FLEX_PINS[i]));
  }

  Serial.println();
}
