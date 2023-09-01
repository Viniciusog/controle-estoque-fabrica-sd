import random
import time
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
topic_ordem_producao = "viniciusog-sd-ordem-producao"
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

# ! Temos que fazer algo como OrdemProducao/Fabrica/1/Produto/1/48
def enviar_ordem_producao(client):
    while True:
        numero_fabrica = input("Insira o número da fábrica: ")
        numero_produto = input("Insira o número da versão do produto: ")
        tamanho_ordem_producao = input(f"Insira o tamanho da ordem de produção para o produto {numero_produto}: ")
        msg = f"OrdemProducao/Fabrica/{numero_fabrica}/Produto/{numero_produto}/{tamanho_ordem_producao}"

        result = client.publish(topic_ordem_producao, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Ordem de produção `{msg}` enviada ao tópico `{topic_ordem_producao}`")
        else:
            print(f"Falha ao enviar ordem de produção ao tópico {topic_ordem_producao}")

def run():
    client = connect_mqtt()
    time.sleep(1)
    client.loop_start()
    enviar_ordem_producao(client)
    client.loop_stop()

if __name__ == '__main__':
    run()
