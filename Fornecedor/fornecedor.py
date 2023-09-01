import random
import time
from paho.mqtt import client as mqtt_client
import threading
import ast

topic_almoxarifado_solicita_partes = "viniciusog-sd-almoxarifado-solicitacao-partes"

broker = 'broker.emqx.io'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 10000)}'
print("client_id: " + str(client_id) + "\n")

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao MQTT Broker!")
        else:
            print("Falha ao conectar, código de retorno: %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def enviar_partes_para_almoxarifado(my_client, array_partes):
    my_dicionario_partes = {}
    for i in range(len(array_partes)):
        my_dicionario_partes[array_partes[i]] = 50

    msg = f"Fornecedor/{my_dicionario_partes}"

    result = my_client.publish(topic_almoxarifado_solicita_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Fornecedor - Partes enviadas para almoxarifado `{msg}`, tópico `{topic_almoxarifado_solicita_partes}`")
    else:
        print(f"Fornecedor - Falha ao enviar partes para almoxarifado `{msg}`, tópico {topic_almoxarifado_solicita_partes}")

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):        
        # Se houver uma solicitação de partes feita pelo almoxarifado
        if msg.topic == topic_almoxarifado_solicita_partes and not str(msg.payload.decode()).startswith("Fornecedor"):
            # "Fabrica/{numero_fabrica}/{partes_para_pedir}"
            print("-----------------------")
            print(f"Fornecedor - Recebida solicitação de partes `{msg.payload.decode()}` do tópico `{msg.topic}`\n")

            array_partes = ast.literal_eval(str(msg.payload.decode()).split("/")[1])
            enviar_partes_para_almoxarifado(client, array_partes)
            print("-----------------------")

    client.subscribe(topic_almoxarifado_solicita_partes)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    time.sleep(1)
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()