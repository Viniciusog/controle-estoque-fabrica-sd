import random
import time
from paho.mqtt import client as mqtt_client
import threading
import ast
from utilsProdutos import produtos
import uuid
from colorama import Fore, Style

numero_fabrica = 1

class Fabrica:
    # dependendo do tamanho do lote, iremos alocar + ou - linhas de producao
    def __init__(self, quantidade_linhas, estoque_produtos_prontos, estoque_partes, ordem_producao):
        self.quantidade_linhas = quantidade_linhas
        self.linhas = [] # vai conter o identificador para o canal de push e sub de uma determinada linha em específico
        self.estoque_produtos_prontos = estoque_produtos_prontos
        self.estoque_partes = estoque_partes
        self.ordem_producao = ordem_producao
        self.qtd_padrao_envio_partes_linha = 6
        self.vermelho = 30 # Nível vermelho se o estoque_partes <= vermelho
        self.amarelo = 40 # Nível amarelo se o vermelho < estoque_partes <= amarelo
    
    def set_ordem_producao(self, ordem_producao):
        self.ordem_producao = ordem_producao

    def add_ordem_producao(self, ordem_producao):
        self.ordem_producao = self.ordem_producao + ordem_producao

    def decrementar_estoque_partes(self, array_qtd, numero_linha):
        est_vermelho = False
        est_amarelo = False 

        for i in range(len(array_qtd)):
            if self.estoque_partes[produtos[numero_linha][i]] >= array_qtd[i]:
                self.estoque_partes[produtos[numero_linha][i]] -= array_qtd[i]

                if self.estoque_partes[produtos[numero_linha][i]] <= self.vermelho:
                    est_vermelho = True
                elif self.estoque_partes[produtos[numero_linha][i]] <= self.amarelo:
                    est_amarelo = True
        
        if est_vermelho:
            print(Fore.RED + f"Fábrica {numero_fabrica} - Nível estoque de partes: Vermelho" + Style.RESET_ALL)
        elif est_amarelo:
            print(Fore.YELLOW + f"Fábrica {numero_fabrica} - Nível estoque de partes: Amarelo" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Fábrica {numero_fabrica} - Nível estoque de partes: Verde" + Style.RESET_ALL)
            
    
    def incrementar_estoque_partes(self, dicionario_qtd_parte):
        est_vermelho = False
        est_amarelo = False

        print(f"Fábrica - Incrementando estoque de partes na fábrica {numero_fabrica}")
        for key in dicionario_qtd_parte:
            self.estoque_partes[key] += dicionario_qtd_parte[key]

            if self.estoque_partes[key] <= self.vermelho:
                est_vermelho = True
            elif self.estoque_partes[key] <= self.amarelo:
                est_amarelo = True

        if est_vermelho:
            print(Fore.RED + f"Fábrica {numero_fabrica} - Nível estoque de partes: Vermelho" + Style.RESET_ALL)
        elif est_amarelo:
            print(Fore.YELLOW + f"Fábrica {numero_fabrica} - Nível estoque de partes: Amarelo" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Fábrica {numero_fabrica} - Nível estoque de partes: Verde" + Style.RESET_ALL)
    
    def incrementar_estoque_produtos_prontos(self):
        print(f"Fábrica - Incrementando estoque de produtos prontos na fábrica {numero_fabrica}")
        self.estoque_produtos_prontos += 1

    def imprimir(self):
        print("------------------------------")
        print("Fábrica - dados atuais:")
        print(f"Estoque produtos prontos: {self.estoque_produtos_prontos}\nEstoque partes: {self.estoque_partes}\nQtd total de ordens de produção solicitadas: {self.ordem_producao}")
        print("------------------------------")

# Indica o número das partes que são utilizadas por esse produto
broker = 'broker.emqx.io'
port = 1883
topic_ordem_producao = "viniciusog-sd-ordem-producao"
topic_linha_solicita_partes = "viniciusog-sd-linha-solicitacao-partes"
topic_fabrica_solitica_partes = "viniciusog-sd-fabrica-solicitacao-partes"
topic_produtos_prontos = "viniciusog-sd-fabrica-produtos-prontos"

client_id = f'python-mqtt-{random.randint(0, 1000)}'
print("client_id: " + str(client_id) + "\n")

fabrica = Fabrica(0,0,[0]*100,0)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao MQTT Broker!")
            print("Fábrica - Carregando informações para serem exibidas...")
        else:
            print("Falha de conexão ao MQTT Broker, código de retorno: %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def enviar_nova_ordem_producao_linhas(my_client, n_produto, qtd_produtos):
    msg = f"Fabrica/{numero_fabrica}/Linha/{n_produto}/{qtd_produtos}"
    result = my_client.publish(topic_ordem_producao, msg)
    status = result[0]
    if status == 0:
        print(f"Fábrica - Ordem de produção `{msg}` enviada ao tópico `{topic_ordem_producao}`")
    else:
        print(f"Fábrica - Falha ao enviar ordem de produção ao tópico {topic_ordem_producao}")

def enviar_qtd_partes(my_client, numero_linha):
    # produto_especifico = produtos[numero_linha - 1]

    # Para cada uma 
    quantidades_cada_parte = []
    for i in range(10):
        quantidades_cada_parte.append(fabrica.qtd_padrao_envio_partes_linha)

    uuid_identificador = uuid.uuid4()

    msg = f"Fabrica/Linha/{numero_linha}/{str(quantidades_cada_parte)}/{str(uuid_identificador)}"

    result = my_client.publish(topic_linha_solicita_partes, msg)
    status = result[0]
    if status == 0:
        print(f"Fábrica - Partes enviadas `{msg}` enviada ao tópico `{topic_linha_solicita_partes}`.")
        print("Fábrica - Decrementando partes.")
        fabrica.decrementar_estoque_partes(quantidades_cada_parte, numero_linha)
        fabrica.imprimir()
    else:
        print(f"Fábrica - Falha ao enviar ordem de produção ao tópico {topic_linha_solicita_partes}")

def loop_verificar_partes(my_client):
    while True:
        time.sleep(4)
        # Contém o número identificador de cada parte para o qual vamos precisar pedir ao almoxarifado
        partes_para_pedir = []
        for i in range(len(fabrica.estoque_partes)):
            if fabrica.estoque_partes[i] <= fabrica.vermelho:
                partes_para_pedir.append(i)
               
        if len(partes_para_pedir) >= 1:        
            solicitar_pecas_ao_almoxarifado(my_client, partes_para_pedir)      

def solicitar_pecas_ao_almoxarifado(my_client, partes_para_pedir):
    msg = f"Fabrica/{numero_fabrica}/{str(partes_para_pedir)}"
    result = my_client.publish(topic_fabrica_solitica_partes, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Fábrica - Solicitação peças ao almoxarifado. `{msg}` enviada ao tópico`{topic_fabrica_solitica_partes}`")
    else:
        print(f"Fábrica - Falha solicitação peças ao almoxarifado. `{msg}` enviada ao tópico`{topic_fabrica_solitica_partes}`")

executou_fabrica_solicitacao_partes = False
executou_linha_solicita_partes = False


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg): 
        if msg.topic == topic_ordem_producao and str(msg.payload.decode()).startswith("OrdemProducao"):
            # OrdemProducao/Fabrica/1/Produto/1/48
            resultados_msg = str(msg.payload.decode()).split('/')
            n_fabrica = int(resultados_msg[2])
            n_produto = int(resultados_msg[4])
            qtd_produtos = int(resultados_msg[5])

            if n_fabrica == numero_fabrica:
                print(f"Fábrica - Recebida ordem de produção `{msg.payload.decode()}` do tópico `{msg.topic}`")
                fabrica.add_ordem_producao(qtd_produtos)
                fabrica.imprimir()
                
                # Quando fábrica recebe ordem de produção, deve indicar para as linhas que recebeu.
                enviar_nova_ordem_producao_linhas(client, n_produto, qtd_produtos)

        elif msg.topic == topic_linha_solicita_partes and not str(msg.payload.decode()).startswith("Fabrica"):                        
            print(f"Fábrica - Solicitação de partes recebida `{msg.payload.decode()}` do tópico `{msg.topic}`")
            # msg = f"Linha/{numero_linha}"
            numero_da_linha = str(msg.payload.decode()).split("/")[1]
            enviar_qtd_partes(client, int(numero_da_linha)) # * tem que decrementar a quantidade de partes da fábrica e depois criar uma thread para ficar ouvindo essa quantidade e eventualmente soliticar ao almoxarifado
        elif msg.topic == topic_fabrica_solitica_partes and not str(msg.payload.decode()).startswith("Fabrica"):            
            # "Almoxarifado/Fabrica/{fabrica_numero}/{my_dicionario_partes}"
            array_resultados = str(msg.payload.decode()).split('/')
            n_fabrica = array_resultados[2]
            dicionario_partes = ast.literal_eval(array_resultados[3])

            if int(n_fabrica) == numero_fabrica:
                global executou_fabrica_solicitacao_partes
                if executou_fabrica_solicitacao_partes == False:    
                    executou_fabrica_solicitacao_partes = True
                    fabrica.incrementar_estoque_partes(dicionario_partes)
                    fabrica.imprimir()
                    executou_fabrica_solicitacao_partes = False
        elif msg.topic == topic_produtos_prontos and str(msg.payload.decode()).startswith("Incrementar"):
            fabrica.incrementar_estoque_produtos_prontos()
            fabrica.imprimir

    client.subscribe(topic_ordem_producao)
    client.subscribe(topic_produtos_prontos)
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