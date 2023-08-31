import random
import time
from paho.mqtt import client as mqtt_client
import threading

running = True
numero_linha = 1

class Linha:
    def __init__(self, identificador, ordem_producao, qtd_partes, qtd_produtos_prontos):
        self.identificador = identificador
        self.ordem_producao = ordem_producao
        self.qtd_partes = qtd_partes
        self.qtd_produtos_prontos = qtd_produtos_prontos
    
    def set_qtd_partes(self, qtd_partes):
        self.qtd_partes = qtd_partes

    def add_qtd_partes(self, qtd_partes):
        self.qtd_partes = self.qtd_partes + qtd_partes
    
    def set_ordem_producao(self, ordem_producao):
        self.ordem_producao = ordem_producao
    
    def add_ordem_producao(self, ordem_producao):
        self.ordem_producao = self.ordem_producao + ordem_producao

    def decrementar_ordem_producao(self):
        self.ordem_producao = self.ordem_producao - 1
    
    def set_qtd_produtos_prontos(self, qtd_produtos_prontos):
        self.qtd_produtos_prontos = qtd_produtos_prontos

    def imprimir(self):
        print("\n----LINHA----")
        print(f"Identificador: {self.identificador}")
        print(f"Qtd Partes: {self.qtd_partes}")
        print(f"Ordem produção: {self.ordem_producao}")
        print(f"Qtd Produtos Prontos: {self.qtd_produtos_prontos}")

linha1 = Linha('linha1', 0, 0, 0)
linha1.imprimir()

broker = 'broker.emqx.io'
port = 1883

# Quantidade de produtos para serem feitos
topic_ordem_producao = "viniciusog-sd-linha1-ordem_producao" # para cada produto, vamos usar uma quantidade de partes

topic_linha_solicita_partes = "viniciusog-sd-linha1-solicitacao-partes"

# * linha faz pub em topico de produtos prontos da fábrica

client_id = f'python-mqtt-{random.randint(0, 1000)}'
print("client_id: " + str(client_id) + "\n")

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def fabricar_produtos(my_client):
    # * depois temos que fazer um while, enquanto peças for zero, pede para a fábrica mais peças
    while running:
        if linha1.ordem_producao > 0:
            print("--Fazendo produto--")
            time.sleep(1)
            print(f"Ordem de produção atual: {linha1.ordem_producao}")
            print("Linha - Produziu 1 produto")
            linha1.decrementar_ordem_producao()
            print("Linha - Decrementou qtd da ordem existente")
            linha1.imprimir()

def loop_verificar_partes(my_client):
    while True:
        time.sleep(1)
        if linha1.qtd_partes == 0:
            soliticar_pecas(my_client)

def soliticar_pecas(my_client):
    print("ok ok ok ok ok ")
    # Passando o número da linha
    msg = f"Linha/{numero_linha}"
    result = my_client.publish(topic_linha_solicita_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Linha - Solicitação peças. `{msg}` enviada ao tópico`{topic_linha_solicita_partes}`")
    else:
        print(f"Linha - Falha solicitação peças. `{msg}` enviada ao tópico`{topic_linha_solicita_partes}`")

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):

        if msg.topic == topic_ordem_producao:
            print(f"Linha - Ordem de produção recebida `{msg.payload.decode()}` do tópico `{msg.topic}`")
            linha1.add_ordem_producao(int(msg.payload.decode()))
            linha1.imprimir()

        # Se partes vieram da fábrica
        elif msg.topic == topic_linha_solicita_partes and not str(msg.payload.decode()).startswith("Linha"):
            print(f"Linha - Partes recebidas `{msg.payload.decode()}` do tópico `{msg.topic}`")
            # Fabrica/Linha/{numero_linha}/{qtd_partes}"
            valores_msg = str(msg.payload.decode()).split('/')
            n_linha = valores_msg[2]
            partesStr = valores_msg[3]

            if int(n_linha) == numero_linha:
                linha1.add_qtd_partes(int(partesStr))
                linha1.imprimir()

    client.subscribe(topic_ordem_producao)
    client.subscribe(topic_linha_solicita_partes)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    thread_fabricar_produtos = threading.Thread(target=fabricar_produtos, args=(client,))
    thread_loop_verificar_partes = threading.Thread(target=loop_verificar_partes, args=(client,))
    # Inicia a thread
    thread_fabricar_produtos.start()
    thread_loop_verificar_partes.start()
    
    client.loop_forever()
    # running = False
    # minha_thread.join()

if __name__ == '__main__':
    run()