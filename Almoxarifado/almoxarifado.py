import random
import time
from paho.mqtt import client as mqtt_client
import threading #""" 066839* """
import ast

class Almoxarifado:
    # dependendo do tamanho do lote, iremos alocar + ou - linhas de producao
    def __init__(self, estoque_partes):
        self.estoque_partes = estoque_partes

    def decrementar_estoque_partes(self, dicionario_qtd_partes):
        print("--Decrementando estoque de partes do almoxarifado--")
        for key in dicionario_qtd_partes:
            self.estoque_partes[key] -= dicionario_qtd_partes[key]

    def incrementar_estoque_partes(self, dicionario_qtd_partes):
        print("--Incrementando estoque de partes do almoxarifado--")
        for key in dicionario_qtd_partes:
            self.estoque_partes[key] += dicionario_qtd_partes[key]
    
    def imprimir(self):
        print("\n-> Amoxarifado")
        print(f"Estoque partes: {self.estoque_partes}")


almoxarifado = Almoxarifado([50]*100)
topic_fabrica_solitica_partes = "viniciusog-sd-fabrica-solicitacao-partes"
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

def enviar_partes_para_fabrica(my_client, fabrica_numero, array_partes):
    my_dicionario_partes = {}
    for i in range(len(array_partes)):
        if (almoxarifado.estoque_partes[array_partes[i]] < 3 and almoxarifado.estoque_partes[array_partes[i]] > 0):
            my_dicionario_partes[array_partes[i]] = almoxarifado.estoque_partes[array_partes[i]] # Se o que tem no almoxarifado é menor do que 3 unidades, então leva as unidades restantes
        elif almoxarifado.estoque_partes[array_partes[i]] >= 3: # Se tiver mais do que 3 unidades, entao leva 3 unidades dessa parte, para a fábrica
            my_dicionario_partes[array_partes[i]] = 3

    msg = f"Almoxarifado/Fabrica/{fabrica_numero}/{my_dicionario_partes}"

    result = my_client.publish(topic_fabrica_solitica_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Almoxarifado - Partes enviadas para fábrica `{msg}`, tópico `{topic_fabrica_solitica_partes}`")
        almoxarifado.decrementar_estoque_partes(my_dicionario_partes)
    else:
        print(f"Almoxarifado - Enviando partes para fábrica `{msg}`, tópico {topic_fabrica_solitica_partes}")

# Criar uma função thread para que quando o estoque de alguma das partes chegue em zero, solicite partes para os fornecedores. Esses por sua vez vão disponibilizar uma quantidade máxima de partes.
def loop_verificar_estoque_partes(my_client):
    while True:
        time.sleep(1)
        # Contém o número identificador de cada parte para o qual vamos precisar pedir aos fornecedores
        partes_para_pedir = []
        for i in range(len(almoxarifado.estoque_partes)):
            if almoxarifado.estoque_partes[i] == 0:
                partes_para_pedir.append(i)
               
        if len(partes_para_pedir) >= 1:        
            solicitar_partes_ao_fornecedor(my_client, partes_para_pedir) 

def solicitar_partes_ao_fornecedor(my_client, partes_para_pedir):
    msg = f"Almoxarifado/{str(partes_para_pedir)}"
    result = my_client.publish(topic_almoxarifado_solicita_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Almoxarifado - Solicitação peças ao fornecedor. `{msg}` enviada ao tópico`{topic_almoxarifado_solicita_partes}`")
    else:
        print(f"Fabrica - Falha solicitação peças ao fornecedor. `{msg}` enviada ao tópico`{topic_almoxarifado_solicita_partes}`")


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):        
        if msg.topic == topic_fabrica_solitica_partes and not str(msg.payload.decode()).startswith("Almoxarifado"):
            # "Fabrica/{numero_fabrica}/{partes_para_pedir}"
            print("-----------------------")
            print(f"Almoxarifado - Recebida solicitação de partes `{msg.payload.decode()}` do tópico `{msg.topic}`\n")
            almoxarifado.imprimir()

            resultados = str(msg.payload.decode()).split('/')
            fabrica_numero = resultados[1]
            array_partes = ast.literal_eval(resultados[2]) 
            enviar_partes_para_fabrica(client, fabrica_numero, array_partes)
            almoxarifado.imprimir()
            print("-----------------------")
        # Quando estiver recebendo as peças do fornecedor
        if msg.topic == topic_almoxarifado_solicita_partes and not str(msg.payload.decode()).startswith("Almoxarifado"):
            dicionario_partes = ast.literal_eval(str(msg.payload.decode()).split("/")[1])
            # print("dicionario partes - almoxarifado")
            # print(dicionario_partes)

            almoxarifado.incrementar_estoque_partes(dicionario_partes)
            almoxarifado.imprimir()

    client.subscribe(topic_fabrica_solitica_partes)
    client.subscribe(topic_almoxarifado_solicita_partes)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    time.sleep(1)
    thread_loop_verificar_estoque_partes = threading.Thread(target=loop_verificar_estoque_partes, args=(client,))
    thread_loop_verificar_estoque_partes.start()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()