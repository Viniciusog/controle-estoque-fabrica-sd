import random
import time
from paho.mqtt import client as mqtt_client

class Linha:
    def __init__(self, identificador, estoque_partes, estoque_produtos_prontos):
        self.identificador = identificador
        self.estoque_partes = estoque_partes
        self.estoque_produtos_prontos = estoque_produtos_prontos
    
    def set_estoque_partes(self, estoque_partes):
        self.estoque_partes = estoque_partes
    
    def set_estoque_produtos_produtos(self, estoque_produtos_prontos):
        self.estoque_produtos_prontos = estoque_produtos_prontos

class Fabrica:
    # dependendo do tamanho do lote, iremos alocar + ou - linhas de producao
    def __init__(self, quantidade_linhas, estoque_produtos_prontos, estoque_partes, ordem_producao):
        self.quantidade_linhas = quantidade_linhas
        self.linhas = [] # vai conter o identificador para o canal de push e sub de uma determinada linha em específico
        self.estoque_produtos_prontos = estoque_produtos_prontos
        self.estoque_partes = estoque_partes
        self.ordem_producao = ordem_producao
    
    def set_ordem_producao(self, ordem_producao):
        self.ordem_producao = ordem_producao

    def add_ordem_producao(self, ordem_producao):
        self.ordem_producao = self.ordem_producao + ordem_producao
    
    def imprimir(self):
        print("-> Fabrica")
        print(f"Qtd Linhas: {self.quantidade_linhas}\nEstoque Produtos Prontos: {self.estoque_produtos_prontos}\nEstoque partes: {self.estoque_partes}\nOrdem de produção:{self.ordem_producao}\n")

""" class Produto:
    def __init__(self, identificador, quantidade_partes):
        self.identificador = identificador
        self.quantidade_partes = quantidade_partes
        
    def get_quantidade_partes(self):
        return self.quantidade_partes
        
    def get_identificador(self):
        return self.identificador
    
    def set_quantidade_partes(self, qtd_partes):
        self.quantidade_partes = qtd_partes

    def imprimir(self):
        print("-----Produto-----")
        print("Identificador: " 
              + str(self.get_identificador()) + ", Qtd Partes: " 
              + str(self.get_quantidade_partes()) + "\n") """

""" produto = Produto(1, 20)
produto.imprimir()

produto.set_quantidade_partes(30)
produto.imprimir()

produto.set_quantidade_partes(40)
produto.imprimir()
 """

broker = 'broker.emqx.io'
port = 1883
topic_ordem_producao = "viniciusog-sd-ordem-producao"
topic_pub_linhas_ordem_producao = "viniciusog-sd-linha1-ordem_producao"
topic_linha_solicita_partes = "viniciusog-sd-linha1-solicitacao-partes"

client_id = f'python-mqtt-{random.randint(0, 1000)}'
print("client_id: " + str(client_id) + "\n")

fabrica = Fabrica(0,0,0,0)

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

def enviar_nova_ordem_producao_linhas(my_client, msg):
    result = my_client.publish(topic_pub_linhas_ordem_producao, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Fabrica - Ordem de produção `{msg}` enviada ao tópico `{topic_pub_linhas_ordem_producao}`")
    else:
        print(f"Fabrica - Falha ao enviar ordem de produção ao tópico {topic_pub_linhas_ordem_producao}")

def enviar_qtd_partes(my_client, numero_linha, qtd_partes):
    msg = f"Fabrica/Linha/{numero_linha}/{qtd_partes}"

    result = my_client.publish(topic_linha_solicita_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Fabrica - Partes enviadas `{msg}` enviada ao tópico `{topic_linha_solicita_partes}`")
    else:
        print(f"Fabrica - Falha ao enviar ordem de produção ao tópico {topic_linha_solicita_partes}")

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print("ha ha ha ha")
        print(f"\nAqui: {msg.payload.decode()}")

        if msg.topic == topic_ordem_producao:
            print("-----------------------")
            print(f"Fabrica - Recebida ordem de produção `{msg.payload.decode()}` do tópico `{msg.topic}`")
            fabrica.add_ordem_producao(int(msg.payload.decode()))
            fabrica.imprimir()
            # Quando fábrica recebe ordem de produção, deve indicar para as linhas que recebeu.
            enviar_nova_ordem_producao_linhas(client, str(msg.payload.decode()))
            print("-----------------------")
        elif msg.topic == topic_linha_solicita_partes and not str(msg.payload.decode()).startswith("Fabrica"):
            print("-----------------------")
            print(f"Fabrica - Solicitação de partes recebida `{msg.payload.decode()}` do tópico `{msg.topic}`")
            # msg = f"Linha/{numero_linha}"
            numero_da_linha = str(msg.payload.decode()).split("/")[1]
            enviar_qtd_partes(client, numero_da_linha, 50) # * tem que decrementar a quantidade de partes da fábrica e depois criar uma thread para ficar ouvindo essa quantidade e eventualmente soliticar ao almoxarifado
            print("-----------------------")


    client.subscribe(topic_ordem_producao)
    client.subscribe(topic_linha_solicita_partes)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()


