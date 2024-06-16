import network
from machine import Pin
from time import sleep
import dht
import urequests

class DHTSensor:
    def __init__(self, pin, bot_token, chat_id, wifi_ssid, wifi_password):
        self.sensor = dht.DHT11(Pin(pin))
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.led = machine.Pin('LED', machine.Pin.OUT)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.wifi = network.WLAN(network.STA_IF)
        self.connect_wifi()
    
    def connect_wifi(self):
        if not self.wifi.isconnected():
            self.toggle_led(0)
            print('Connecting to Wi-Fi...')
            self.wifi.active(True)
            self.wifi.connect(self.wifi_ssid, self.wifi_password)
            retries = 0
            max_retries = 5  # Set maximum retries before waiting longer
            while not self.wifi.isconnected():
                retries += 1
                if retries >= max_retries:
                    print('Wi-Fi connection failed. Retrying after delay...')
                    retries = 0
                    sleep(300)
                else:
                    sleep(30)
                    print(f'Retry {retries}/{max_retries}')
                    self.wifi.active(False)
                    self.wifi.active(True)
                    self.wifi.connect(self.wifi_ssid, self.wifi_password)
            print('Wi-Fi connected:', self.wifi.ifconfig())
            self.toggle_led(1)
            
    
    def read_sensor(self):
        try:
            
            sleep(2)  # Delay between readings
            self.connect_wifi()  # Ensure Wi-Fi is connected
            self.sensor.measure()  # Measure temperature and humidity
            temp = self.sensor.temperature()  # Get temperature in Celsius
            hum = self.sensor.humidity()  # Get humidity in percentage
            
            # Print the temperature and humidity
            print('Temperature:', temp, 'C')
            print('Humidity:', hum, '%')
            
            # Check conditions for sending message
            if temp > 29.0 or hum > 60.0:
                # Format message
                message = f'Temperature: {temp:.1f}°C\nHumidity: {hum:.1f}%'
                # Send message via Telegram bot
                self.send_telegram_message(message)
            
            return temp, hum
        
        except OSError as e:
            # Print detailed error message
            print('Failed to read sensor:', e)
            return None, None

    def send_telegram_message(self, message):
        try:
            url = self.api_url
            data = {
                'chat_id': self.chat_id,
                'text': message
            }
            headers = {'Content-type': 'application/json'}
            response = urequests.post(url, json=data, headers=headers)
            response.close()
            print('Message sent to Telegram')
        
        except Exception as e:
            print('Failed to send message to Telegram:', e)
    
    def toggle_led(self, state):
        self.led.value(state)

# Wi-Fi connection details
wifi_ssid = ""
wifi_password = ""

# Telegram bot details
bot_token = ''
chat_id = ''

# Initialize the sensor with Telegram bot details
sensor = DHTSensor(pin=22, bot_token=bot_token, chat_id=chat_id, wifi_ssid=wifi_ssid, wifi_password=wifi_password)

# Initialize the onboard LED
#sensor.toggle_led(1)

# Continuously read the sensor and send data via Telegram
while True:
    sensor.read_sensor()
    sleep(1800)  # Delay between sensor readings (1800 seconds = 30 minutes)

