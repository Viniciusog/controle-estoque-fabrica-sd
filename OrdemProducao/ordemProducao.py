
import random
import time
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
topic = "viniciusog-sd-ordem-producao"
client_id = f'python-mqtt-{random.randint(0, 10000)}'
print("client_id: " + str(client_id) + "\n")
# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao MQTT Broker!")
        else:
            print("Falha ao conectar, código de retorno: %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    while True:
        tamanho_ordem_producao = input("Insira o tamanho da ordem de produção: ")
        msg = str(tamanho_ordem_producao)
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Ordem de produção `{msg}` enviada ao tópico `{topic}`")
        else:
            print(f"Falha ao enviar ordem de produção ao tópico {topic}")

def run():
    client = connect_mqtt()
    time.sleep(1)
    client.loop_start()
    publish(client)
    client.loop_stop()

if __name__ == '__main__':
    run()
