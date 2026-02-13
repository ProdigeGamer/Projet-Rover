"""
-----------------------> NE PAS MODIFIER CE SCRIPT <-------------------

Classe Python pour contrôler le bas niveau (interface i2C, autres) des capteurs et actuateurs du ROVER IPSA

Voir les exemples d'utilisation en bas du script (après 'if __name__ == "__main__":')
"""
import struct
import time, utime
from machine import I2C, Pin, PWM, time_pulse_us




MOTOR_I2C_ADDRESS = 0x26        
TICKS_PER_REVOLUTION = 2340
SAMPLE_INTERVAL = 0.01  # 0.01 seconds = 10 ms
REG = {
            'TYPE': 0x01,
            'DEADZONE': 0x02,
            'PULSE_PER_LINE': 0x03,
            'PHASE_COUNT': 0x04,
            'WHEEL_DIAMETER': 0x05,
            'SPEED': 0x06,
            'PWM': 0x07,
            'ENCODER_DELTA': [0x10, 0x11, 0x12, 0x13],
            'ENCODER_HIGH': [0x20, 0x22, 0x24, 0x26],
            'ENCODER_LOW':  [0x21, 0x23, 0x25, 0x27],
        }

SERVO_PIN = 22

SONAR_TRIG_PIN = 21
SONAR_ECHO_PIN = 20

class IpsaRoverLib:
    def __init__(self):

        self.i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=200000)         

        self.PWM_MIN = 600
        self.PWM_MAX = 2000

        self.current_pwms  = [0, 0, 0, 0]
        
        # Servo
        self.servo_pwm = PWM(Pin(SERVO_PIN, Pin.OUT))
        self.servo_pwm.freq(50)
        self.servo_period_us = int(1_000_000 / 50)

        # Sonar SR04
        self.trig_pin = Pin(SONAR_TRIG_PIN, Pin.OUT)
        self.echo_pin = Pin(SONAR_ECHO_PIN, Pin.IN)
        self.trig_pin.low()

    # -------------------------
    # Gestion de l'i2c
    # -------------------------
    def write_register(self, reg, data_bytes):
        if self.i2c is None:
            raise RuntimeError("I2C non initialisée. Appeler motor.init_i2c(i2c) avant.")
        self.i2c.writeto_mem(MOTOR_I2C_ADDRESS, reg, bytearray(data_bytes))
    
    def read_register(self, reg, length):
        if self.i2c is None:
            raise RuntimeError("I2C non initialisée. Appeler motor.init_i2c(i2c) avant.")
        return self.i2c.readfrom_mem(MOTOR_I2C_ADDRESS, reg, length)
    
    def float_to_bytes(self, value):
        return struct.pack('<f', value)
 
    # -------------------------
    # Motor Configuration for type 3 TT DC Motor
    # -------------------------
    def set_motor_parameters(self):
        self.write_register(REG['TYPE'], [3])                             # Motor type 3: TT encoder motor
        time.sleep(0.05)
        self.write_register(REG['PHASE_COUNT'], [0x00, 45])               # 45 phase count
        time.sleep(0.05)
        self.write_register(REG['PULSE_PER_LINE'], [0x00, 13])            # 13 pulse/line
        time.sleep(0.05)
        self.write_register(REG['WHEEL_DIAMETER'], list(self.float_to_bytes(60.0)))  # 65 mm diameter
        time.sleep(0.05)
        self.write_register(REG['DEADZONE'], [0x04, 0xE2])                # 1250 (0x04E2) deadzone
        time.sleep(0.05)
    
    # -------------------------
    # I. Partie Moteur
    # -------------------------
 
    # -------------------------
    # Encoder Readings
    # -------------------------
    def read_total_encoder_counts(self):  # Total Nb of ticks (wheel position)
        counts = []
        for high_reg, low_reg in zip(REG['ENCODER_HIGH'], REG['ENCODER_LOW']):
            high = self.read_register(high_reg, 2)
            low = self.read_register(low_reg, 2)
            value = ((high[0] << 8) | high[1]) << 16 | ((low[0] << 8) | low[1])
            if value & 0x80000000:
                value -= 0x100000000
            counts.append(value)
        return counts
 
 
    def read_encoder_deltas(self):       # Nb ticks for 10 ms
        ticks = []
        for reg in REG['ENCODER_DELTA']:
            buf = self.read_register(reg, 2)
            value = (buf[0] << 8) | buf[1]
            if value & 0x8000:
                value -= 0x10000
            ticks.append(value)
        return ticks
  
    # -------------------------
    # RPM Calculation
    # -------------------------
    
    def calculate_rpm(self, ticks, ticks_per_rev = TICKS_PER_REVOLUTION, interval = SAMPLE_INTERVAL):
        revolutions = ticks / ticks_per_rev
        rps = revolutions / interval
        rpm = rps * 60
        return rpm
    
    def percent_pwm(self, pc):
        return self.PWM_MIN + (self.PWM_MAX-self.PWM_MIN)*(.01*pc)
    # -------------------------
    # Motor Control
    # -------------------------
    def control_motors_pwm(self, pwm1, pwm2, pwm3, pwm4):
        pwms = []
        for v in (pwm1, pwm2, pwm3, pwm4):
            pwms.extend([(v >> 8) & 0xFF, v & 0xFF])
        self.write_register(REG['PWM'], pwms)

    def control_motor_percent(self, pc1, pc2, pc3, pc4):        
        PWM1 = self.percent_pwm(pc1)
        PWM2 = self.percent_pwm(pc2)
        PWM3 = self.percent_pwm(pc3)
        PWM4 = self.percent_pwm(pc4)

        self.control_motors_pwm(PWM1, PWM2, PWM3, PWM4)

    def control_motor_speed(self, m1, m2, m3, m4): 
        """
        min -1000 
        max +1000
        """
        speeds = [] 
        for v in (m1, m2, m3, m4): 
            speeds.extend([(v >> 8) & 0xFF, v & 0xFF]) 
            self.write_register(REG['SPEED'], speeds)
    # -------------------------
    # Servo Control
    # -------------------------
    def set_servo_pulse_us(self, pulse_us):
        """
        PWM servo en microsecondes (typiquement 1000–2000 µs).
        """
        if not 0 < pulse_us < self.servo_period_us:
            raise ValueError("pulse_us must be smaller than PWM period")

        duty_u16 = int((pulse_us / self.servo_period_us) * 65535)
        self.servo_pwm.duty_u16(duty_u16)
        
    # -------------------------
    # Sonar Control
    # -------------------------
    
    def read_sonar_echo_time_ms(self, pulses=5, timeout_us=30000, inter_pulse_delay_ms=5):
        """
        Mesure le temps d'écho du SR04 avec moyennage sur plusieurs pulses.

        pulses : nombre de mesures à intégrer (défaut = 5)
        timeout_us : timeout pour chaque mesure
        inter_pulse_delay_ms : délai entre pulses (évite l'auto-écho)

        Retour :
            float : temps d'écho moyen en ms
            None  : si aucune mesure valide
        """
        if pulses <= 0:
            raise ValueError("pulses must be > 0")

        valid_samples = 0
        echo_time_sum_us = 0

        for _ in range(pulses):
            # Trigger 10 µs
            self.trig_pin.low()
            utime.sleep_us(2)
            self.trig_pin.high()
            utime.sleep_us(10)
            self.trig_pin.low()

            try:
                echo_time_us = time_pulse_us(
                    self.echo_pin,
                    1,
                    timeout_us
                )
            except OSError:
                echo_time_us = -1

            if echo_time_us > 0:
                echo_time_sum_us += echo_time_us
                valid_samples += 1

            # Délai inter-pulse (recommandé ≥ 2 ms, ici 5 ms par défaut)
            utime.sleep_ms(inter_pulse_delay_ms)

        if valid_samples == 0:
            return None

        return (echo_time_sum_us / valid_samples) / 1000.0
    

    
if __name__ == "__main__":
    
    driver = IpsaRoverLib()
    ## Déplacement
    driver.control_motor_speed(0, 0, 0, 0)
    time.sleep(.5)
    driver.control_motor_speed(-100, -100, -100, -100)
    time.sleep(.5)
    ticks = driver.read_encoder_deltas()
    print(f"1 : {driver.read_encoder_deltas()}")
    print(f"RPM : {driver.calculate_rpm(ticks[0])}")
    time.sleep(2)
    driver.control_motor_speed(0, 0, 0, 0)

    # Servo
    for us in range(1000,2000,50):
        driver.set_servo_pulse_us(us)
        time.sleep(.1)

    #Sonar
    for mes in range(10):
        echo_time_ms = driver.read_sonar_echo_time_ms()
        print(f"Temps de vol de l'onde : {echo_time_ms}")
        time.sleep(.5)
    


     
 

