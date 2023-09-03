import random
import time
from paho.mqtt import client as mqtt_client
import threading #""" 066839* """
import ast
from colorama import Fore, Style

uuid_solicitacao_partes = ""

class Almoxarifado:
    # dependendo do tamanho do lote, iremos alocar + ou - linhas de producao
    def __init__(self, estoque_partes):
        self.estoque_partes = estoque_partes
        self.qtd_padrao_envio_partes_fabrica = 50
        self.vermelho = 50
        self.amarelo = 100

    def decrementar_estoque_partes(self, dicionario_qtd_partes):
        print("Almoxarifado - Decrementando estoque de partes do almoxarifado--")
        
        est_vermelho = False
        est_amarelo = False

        for key in dicionario_qtd_partes:
            self.estoque_partes[key] -= dicionario_qtd_partes[key]

            if self.estoque_partes[key] <= self.vermelho:
                est_vermelho = True
            elif self.estoque_partes[key] <= self.amarelo:
                est_amarelo = True
                
        if est_vermelho:
            print(Fore.RED + f"Almoxarifado - Nível estoque de partes: Vermelho" + Style.RESET_ALL)
        elif est_amarelo:
            print(Fore.YELLOW + f"Almoxarifado - Nível estoque de partes: Amarelo" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Almoxarifado - Nível estoque de partes: Verde" + Style.RESET_ALL)

    def incrementar_estoque_partes(self, dicionario_qtd_partes):
        print("Almoxarifado - Incrementando estoque de partes.")

        est_vermelho = False
        est_amarelo = False

        for key in dicionario_qtd_partes:
            self.estoque_partes[key] += dicionario_qtd_partes[key]

            if self.estoque_partes[key] <= self.vermelho:
                est_vermelho = True
            elif self.estoque_partes[key] <= self.amarelo:
                est_amarelo = True
                
        if est_vermelho:
            print(Fore.RED + f"Almoxarifado - Nível estoque de partes: Vermelho" + Style.RESET_ALL)
        elif est_amarelo:
            print(Fore.YELLOW + f"Almoxarifado - Nível estoque de partes: Amarelo" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Almoxarifado - Nível estoque de partes: Verde" + Style.RESET_ALL)

    
    def imprimir(self):
        print("Almoxarifado - Dados atuais:")
        print(f"Almoxarifado - Estoque partes: {self.estoque_partes}")
        print("------------------------------")


almoxarifado = Almoxarifado([0]*100)
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
            print("Almoxarifado - Carregando informações...")
        else:
            print("Falha ao conectar, código de retorno: %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def enviar_partes_para_fabrica(my_client, fabrica_numero, array_partes):
    my_dicionario_partes = {}
    for i in range(len(array_partes)):
        if (almoxarifado.estoque_partes[array_partes[i]] < almoxarifado.qtd_padrao_envio_partes_fabrica and almoxarifado.estoque_partes[array_partes[i]] > 0):
            my_dicionario_partes[array_partes[i]] = almoxarifado.estoque_partes[array_partes[i]] # Se o que tem no almoxarifado é menor do que 3 unidades, então leva as unidades restantes
        elif almoxarifado.estoque_partes[array_partes[i]] >= almoxarifado.qtd_padrao_envio_partes_fabrica: # Se tiver mais do que 3 unidades, entao leva 3 unidades dessa parte, para a fábrica
            my_dicionario_partes[array_partes[i]] = almoxarifado.qtd_padrao_envio_partes_fabrica

    msg = f"Almoxarifado/Fabrica/{fabrica_numero}/{my_dicionario_partes}"

    result = my_client.publish(topic_fabrica_solitica_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Almoxarifado - Partes enviadas para fábrica `{msg}`, tópico `{topic_fabrica_solitica_partes}`.")
        almoxarifado.decrementar_estoque_partes(my_dicionario_partes)
    else:
        print(f"Almoxarifado - Enviando partes para fábrica `{msg}`, tópico {topic_fabrica_solitica_partes}.")

# Criar uma função thread para que quando o estoque de alguma das partes chegue em zero, solicite partes para os fornecedores. Esses por sua vez vão disponibilizar uma quantidade máxima de partes.
def loop_verificar_estoque_partes(my_client):
    while True:
        time.sleep(1)
        # Contém o número identificador de cada parte para o qual vamos precisar pedir aos fornecedores
        partes_para_pedir = []
        for i in range(len(almoxarifado.estoque_partes)):
            if almoxarifado.estoque_partes[i] <= almoxarifado.vermelho:
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
        print(f"Almoxarifado - Falha solicitação peças ao fornecedor. `{msg}` enviada ao tópico`{topic_almoxarifado_solicita_partes}`.")


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):        
        if msg.topic == topic_fabrica_solitica_partes and not str(msg.payload.decode()).startswith("Almoxarifado"):
            # "Fabrica/{numero_fabrica}/{partes_para_pedir}"
            print(f"Almoxarifado - Recebida solicitação de partes `{msg.payload.decode()}` do tópico `{msg.topic}`\n")
            almoxarifado.imprimir()

            resultados = str(msg.payload.decode()).split('/')
            fabrica_numero = resultados[1]
            array_partes = ast.literal_eval(resultados[2]) 
            enviar_partes_para_fabrica(client, fabrica_numero, array_partes)
            almoxarifado.imprimir()
        # Quando estiver recebendo as peças do fornecedor
        if msg.topic == topic_almoxarifado_solicita_partes and not str(msg.payload.decode()).startswith("Almoxarifado"):
            dados_array = str(msg.payload.decode()).split("/")
            dicionario_partes = ast.literal_eval(dados_array[1])
            uuid_recebido = dados_array[2]
            
            global uuid_solicitacao_partes
            if not uuid_solicitacao_partes == uuid_recebido:
                almoxarifado.incrementar_estoque_partes(dicionario_partes)
                almoxarifado.imprimir()
                uuid_solicitacao_partes = uuid_recebido

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