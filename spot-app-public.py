from machine import Pin, SPI
import framebuf
import time
import network
import urequests
import json
from datetime import datetime

MOSI = 11
SCK = 10    
RCLK = 9

KILOBIT   = 0xFE
HUNDREDS  = 0xFD
TENS      = 0xFB
UNITS     = 0xF7
Dot       = 0x80

SEG8Code = [
    0x3F, # 0
    0x06, # 1
    0x5B, # 2
    0x4F, # 3
    0x66, # 4
    0x6D, # 5
    0x7D, # 6
    0x07, # 7
    0x7F, # 8
    0x6F, # 9
    0x77, # A
    0x7C, # b
    0x39, # C
    0x5E, # d
    0x79, # E
    0x71  # F
    ]

SevenSegmentASCII = {
    " ":0x00, # (space) 
    "!":0x86, # ! 
    "\"":0x22, # " 
    "#":0x7E, # # 
    "$":0x6D, # $ 
    "%":0xD2, # % 
    "&":0x46, # & 
    "\"":0x20, #" 
    "(":0x29, #( 
    ")":0x0B, #) 
    "*":0x21, #* 
    "+":0x70, #+ 
    ",":0x10, #, 
    "-":0x40, #- 
    ".":0x80, #. 
    "/":0x52, #/ 
    "0":0x3F, #0 
    "1":0x06, #1 
    "2":0x5B, #2 
    "3":0x4F, #3 
    "4":0x66, #4 
    "5":0x6D, #5 
    "6":0x7D, #6 
    "7":0x07, #7 
    "8":0x7F, #8 
    "9":0x6F, #9 
    ":":0x09, #: 
    ";":0x0D, #; 
    "<":0x61, #< 
    "=":0x48, #= 
    ">":0x43, #> 
    "?":0xD3, #? 
    "@":0x5F, #@ 
    "A":0x77, #A 
    "B":0x7C, #B 
    "C":0x39, #C 
    "D":0x5E, #D 
    "E":0x79, #E 
    "F":0x71, #F 
    "G":0x3D, #G 
    "H":0x76, #H 
    "I":0x30, #I 
    "J":0x1E, #J 
    "K":0x75, #K 
    "L":0x38, #L 
    "M":0x15, #M 
    "N":0x37, #N 
    "O":0x3F, #O 
    "P":0x73, #P 
    "Q":0x6B, #Q 
    "R":0x33, #R 
    "S":0x6D, #S 
    "T":0x78, #T 
    "U":0x3E, #U 
    "V":0x3E, #V 
    "W":0x2A, #W 
    "X":0x76, #X 
    "Y":0x6E, #Y 
    "Z":0x5B, #Z 
    "[":0x39, #[ 
    "\\":0x64, #\ 
    "]":0x0F, #] 
    "^":0x23, #^ 
    "_":0x08, #_ 
    "`":0x02, #` 
    "a":0x5F, #a 
    "b":0x7C, #b 
    "c":0x58, #c 
    "d":0x5E, #d 
    "e":0x7B, #e 
    "f":0x71, #f 
    "g":0x6F, #g 
    "h":0x74, #h 
    "i":0x10, #i 
    "j":0x0C, #j 
    "k":0x75, #k 
    "l":0x30, #l 
    "m":0x14, #m 
    "n":0x54, #n 
    "o":0x5C, #o 
    "p":0x73, #p 
    "q":0x67, #q 
    "r":0x50, #r 
    "s":0x6D, #s 
    "t":0x78, #t 
    "u":0x1C, #u 
    "v":0x1C, #v 
    "w":0x14, #w 
    "x":0x76, #x 
    "y":0x6E, #y 
    "z":0x5B, #z 
    "{":0x46, #{ 
    "|":0x30, #| 
    "}":0x70, #} 
    "~":0x01, #~ 
    "":0x00, #(del) 
}

class LED_8SEG():
    def __init__(self):
        self.rclk = Pin(RCLK,Pin.OUT)
        self.rclk(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.SEG8=SevenSegmentASCII
    
    '''
    function: Send Command
    parameter: 
        Num: bit select
        Seg：segment select       
    Info:The data transfer
    '''
    def write_cmd(self, Num, Seg):    
        self.rclk(1)
        self.spi.write(bytearray([Num]))
        self.spi.write(bytearray([Seg]))
        self.rclk(0)
        time.sleep(0.002)
        self.rclk(1)

    def write_4_digits(self, fourth, third, second, first):
        for i in range(50):
            time.sleep(.0005)
            self.write_cmd(KILOBIT, self.SEG8[fourth])
            time.sleep(.0005)
            self.write_cmd(HUNDREDS, self.SEG8[third])
            time.sleep(.0005)
            self.write_cmd(TENS, self.SEG8[second])
            time.sleep(.0005)
            self.write_cmd(UNITS, self.SEG8[first])
            time.sleep(.0005)
            
    def Print(self, input_msg):
        j = 0
        for i in range(len(input_msg) - 3):
            self.write_4_digits(fourth = input_msg[i+j], third = input_msg[i + j + 1], second = input_msg[i + j + 2], first = input_msg[i + j + 3])
            time.sleep(.0)
            j += 0


## connecting to wi-fi
ssid = 'Wireless Network'
password = 'The Password'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

# Function to fetch data from API
def fetch_api_data(api_url):
    try:
        response = urequests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            response.close()
            return data
        else:
            print("Error: Failed to fetch data from API. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

def save_prices(data):
    try:
        with open("prices_data.json", "w") as file:
            json.dump(data, file)
        print("Data saved successfully.")
    except Exception as e:
        print("Error:", e)

def load_prices():
    try:
        with open("prices_data.json", "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("Error: Prices data file not found.")
        return None
    except Exception as e:
        print("Error:", e)
        return None

def find_current_price(data):
    current_time = datetime.now()
    prices = data["prices"]
    for entry in prices:
        start_time = datetime.strptime(entry["startDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime(entry["endDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if start_time <= current_time <= end_time:
            return entry["price"]
    print("Error: No price found for the current time.")
    return None

# Fetch data from API
api_url = "https://api.porssisahko.net/v1/latest-prices.json"
data = fetch_api_data(api_url)

# Save data
if data:
    save_prices(data)

# Load data
saved_data = load_prices()

# Find current price
current_price = None
if saved_data:
    current_price = find_current_price(saved_data)
    if current_price:
        print("Current price:", current_price)

# Define taxes and transfer fees
electricity_tax_rate = 0.0279372  # EUR/kWh
transfer_fee = 0.0309  # EUR/kWh
VAT = 1.24  # Value added tax is 24%

# Summing up fees and spot price
if current_price:
    display_price = current_price * VAT + transfer_fee + electricity_tax_rate
    print(display_price)  # this is the final value we want to display on the segment display.

    # Main program
    def main():
        LED = LED_8SEG()
        while True:
            # Display the calculated price continuously
            LED.Print(str(round(display_price, 2)))  # Format the price to 2 decimal places
            time.sleep(1)  # Update display every second

    if __name__ == "__main__":
        main()
else:
    print("Error: No current price available, cannot calculate display price.")
