import random
import time
from paho.mqtt import client as mqtt_client
import threading
import ast

class Almoxarifado:
    # dependendo do tamanho do lote, iremos alocar + ou - linhas de producao
    def __init__(self, estoque_partes):
        self.estoque_partes = estoque_partes

    def decrementar_estoque_partes(self, array_qtd, numero_linha):
        for i in range(len(self.array_qtd)):
            self.estoque_partes[produtos[numero_linha][i]] -= array_qtd[i]

    def imprimir(self):
        print("-> Amoxarifado")
        print(f"Qtd Linhas: {self.quantidade_linhas}\nEstoque Produtos Prontos: {self.estoque_produtos_prontos}\nEstoque partes: {self.estoque_partes}\nOrdem de produção:{self.ordem_producao}\n")

broker = 'broker.emqx.io'
port = 1883
topic_fabrica_solitica_partes = "viniciusog-sd-fabrica-solicitacao-partes"
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

def enviar_partes_para_fabrica(my_client, fabrica_numero, array_partes):
    my_dicionario_partes = {}
    for i in range(len(array_partes)):
        my_dicionario_partes[array_partes[i]] = 3 # Estamos enviando 3 unidades de cada parte solicitada 

    msg = f"Almoxarifado/Fabrica/{fabrica_numero}/{my_dicionario_partes}"

    result = my_client.publish(topic_fabrica_solitica_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Almoxarifado - Partes enviadas para fábrica `{msg}`, tópico `{topic_fabrica_solitica_partes}`")
    else:
        print(f"Almoxarifado - Enviando partes para fábrica `{msg}`, tópico {topic_fabrica_solitica_partes}")

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print("Almoxarifado recebeu mensagem")
        
        if msg.topic == topic_fabrica_solitica_partes and not str(msg.payload.decode()).startswith("Almoxarifado"):
            # "Fabrica/{numero_fabrica}/{partes_para_pedir}"
            print("-----------------------")
            print(f"Almoxarifado - Recebida solicitação de partes `{msg.payload.decode()}` do tópico `{msg.topic}`\n")

            resultados = str(msg.payload.decode()).split('/')
            fabrica_numero = resultados[1]
            array_partes = ast.literal_eval(resultados[2]) 
            enviar_partes_para_fabrica(client, fabrica_numero, array_partes)
            print("-----------------------")

    client.subscribe(topic_fabrica_solitica_partes)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    time.sleep(1)
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()