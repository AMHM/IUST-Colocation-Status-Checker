import threading
import time
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import paho.mqtt.client as mqtt
import ntplib
import jdatetime
from datetime import datetime
import pytz

MQTT_BROKER = "pub.metable.ir"
MQTT_PORT = 32090
MQTT_USER_NAME = "monazzah@iust.ac.ir"
MQTT_PASSWORD = "Monazzah@123456"
MQTT_TOPIC = "monazzah@iust.ac.ir/IUST-ITS/Colocation-Status"
NTP_SERVER = "pool.ntp.org"
IRAN_TZ = "Asia/Tehran"

def get_iran_time_jalali():
    try:
        client = ntplib.NTPClient()
        response = client.request(NTP_SERVER, version=3)
        utc_dt = datetime.utcfromtimestamp(response.tx_time)
        iran_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(IRAN_TZ))
    except Exception as e:
        print(f"Failed to get NTP time: {e}")
        iran_dt = datetime.now(pytz.timezone(IRAN_TZ))

    jalali_dt = jdatetime.datetime.fromgregorian(datetime=iran_dt)
    date_str = jalali_dt.strftime('%Y/%m/%d')
    time_str = jalali_dt.strftime('%H:%M:%S')
    return date_str, time_str

def mqtt_keep_alive(client):
    while True:
        date_str, time_str = get_iran_time_jalali()
        message = f"تاریخ: {date_str} - ساعت: {time_str}: keep alive"
        result = client.publish(MQTT_TOPIC,json.dumps({"Date": date_str, "Time": time_str, "message": "keep alive"}))
        #result = client.publish(MQTT_TOPIC, message)
        status = result[0]
        if status == 0:
            print(f"Published: {message}")
        else:
            print("Failed to send message to topic")
        time.sleep(60)

def setup_mqtt():
    def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n" % rc)
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER_NAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()
    return client

def start_http_server(port=8000):
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("", port), handler)
    print(f"HTTP server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    mqtt_client = setup_mqtt()
    mqtt_keep_alive(mqtt_client)
