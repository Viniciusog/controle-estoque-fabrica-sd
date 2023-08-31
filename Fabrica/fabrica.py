import random
import time
from paho.mqtt import client as mqtt_client
import threading
import ast

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

    def decrementar_estoque_partes(self, array_qtd, numero_linha):
        for i in range(len(self.array_qtd)):
            self.estoque_partes[produtos[numero_linha][i]] -= array_qtd[i]
    
    def incrementar_estoque_partes(self, dicionario_qtd_parte):
        print(f"Incrementando estoque de partes na fábrica {numero_fabrica}")
        for key in dicionario_qtd_parte:
            self.estoque_partes[key] += dicionario_qtd_parte[key]

    def imprimir(self):
        print("-> Fabrica")
        print(f"Qtd Linhas: {self.quantidade_linhas}\nEstoque Produtos Prontos: {self.estoque_produtos_prontos}\nEstoque partes: {self.estoque_partes}\nOrdem de produção:{self.ordem_producao}\n")

# Indica o número das partes que são utilizadas por esse produto

# Considerando que o produto tem 10 partes, 5 do 'kit base' e 5 do 'kit variação'
# Cada número indica a numeração da parte específica.
produtos = [
    [1, 2, 3, 4, 5, 10, 9, 8, 7, 6],
    [1, 2, 3, 4, 5, 15, 14, 13, 12, 11],
    [1, 2, 3, 4, 5, 10, 20, 19, 18, 17],
    [1, 2, 3, 4, 5, 10, 25, 24, 23, 22],
    [1, 2, 3, 4, 5, 10, 30, 29, 28, 27]]

broker = 'broker.emqx.io'
port = 1883
topic_ordem_producao = "viniciusog-sd-ordem-producao"
topic_pub_linhas_ordem_producao = "viniciusog-sd-linha1-ordem_producao"
topic_linha_solicita_partes = "viniciusog-sd-linha-solicitacao-partes"
topic_fabrica_solitica_partes = "viniciusog-sd-fabrica-solicitacao-partes"

client_id = f'python-mqtt-{random.randint(0, 1000)}'
print("client_id: " + str(client_id) + "\n")

fabrica = Fabrica(0,0,[0]*100,0)
numero_fabrica = 1

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

def enviar_qtd_partes(my_client, numero_linha):
    produto_especifico = produtos[numero_linha - 1]
    
    # Quantidade para cada parte das 10 que um produto precisa
    quantidades_cada_parte = []
    for i in range(10):
        quantidades_cada_parte.append(1)

    msg = f"Fabrica/Linha/{numero_linha}/{str(quantidades_cada_parte)}"

    result = my_client.publish(topic_linha_solicita_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Fabrica - Partes enviadas `{msg}` enviada ao tópico `{topic_linha_solicita_partes}`")
        print("Decrementando partes da fábrica....")
        # Decrementa a quantidade de cada parte enviada. Sabemos o número da parte através do número da linha
        # Pois daí temos o array de produtos, que indica quais partes são usadas em cada produto
        fabrica.decrementar_estoque_partes(quantidades_cada_parte, numero_linha)
        fabrica.imprimir()
    else:
        print(f"Fabrica - Falha ao enviar ordem de produção ao tópico {topic_linha_solicita_partes}")

def loop_verificar_partes(my_client):
    while True:
        time.sleep(1)
        # Contém o número identificador de cada parte para o qual vamos precisar pedir ao almoxarifado
        partes_para_pedir = []
        for i in range(len(fabrica.estoque_partes)):
            if fabrica.estoque_partes[i] == 0:
                partes_para_pedir.append(i)
               
        if len(partes_para_pedir) >= 1:        
            solicitar_pecas_ao_almoxarifado(my_client, partes_para_pedir)      

def solicitar_pecas_ao_almoxarifado(my_client, partes_para_pedir):
    msg = f"Fabrica/{numero_fabrica}/{str(partes_para_pedir)}"
    result = my_client.publish(topic_fabrica_solitica_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(result.rc)
        print(f"Fabrica - Solicitação peças ao almoxarifado. `{msg}` enviada ao tópico`{topic_fabrica_solitica_partes}`")
    else:
        print(f"Fabrica - Falha solicitação peças ao almoxarifado. `{msg}` enviada ao tópico`{topic_fabrica_solitica_partes}`")
        print(result.rc)

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
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
            enviar_qtd_partes(client, int(numero_da_linha)) # * tem que decrementar a quantidade de partes da fábrica e depois criar uma thread para ficar ouvindo essa quantidade e eventualmente soliticar ao almoxarifado
            print("-----------------------")
        elif msg.topic == topic_fabrica_solitica_partes and not str(msg.payload.decode()).startswith("Fabrica"):
            # "Almoxarifado/Fabrica/{fabrica_numero}/{my_dicionario_partes}"
            array_resultados = str(msg.payload.decode()).split('/')
            n_fabrica = array_resultados[2]
            dicionario_partes = ast.literal_eval(array_resultados[3])

            if int(n_fabrica) == numero_fabrica:
                fabrica.incrementar_estoque_partes(dicionario_partes)
                fabrica.imprimir()

    client.subscribe(topic_ordem_producao)
    client.subscribe(topic_linha_solicita_partes)
    client.subscribe(topic_fabrica_solitica_partes)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    thread_loop_verificar_partes = threading.Thread(target=loop_verificar_partes, args=(client,))
    thread_loop_verificar_partes.start()
    client.loop_forever()

if __name__ == '__main__':
    run()


