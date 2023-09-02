import random
import time
from paho.mqtt import client as mqtt_client
import threading
import ast
from colorama import Fore, Style

running = True
numero_linha = 1
executou_linha_solicita_partes = False 
uuid_solicitacao_partes = ""

class Linha:
    def __init__(self, identificador, ordem_producao, array_partes, qtd_produtos_prontos):
        self.identificador = identificador
        self.ordem_producao = ordem_producao
        self.array_partes = array_partes
        self.qtd_produtos_prontos = qtd_produtos_prontos
        self.vermelho = 3 # Se estoque_de_partes <= 3
        self.amarelo = 5 # Se 3 < estoque_de_partes <= 5
        # verde vai ser se 5 < estoque_de_partes 
    
    def set_array_partes(self, array_partes):
        self.array_partes = array_partes

    def add_array_partes(self, incremento_array_partes):
        est_vermelho = False
        est_amarelo = False

        for i in range(len(self.array_partes)):
            self.array_partes[i] = self.array_partes[i] + incremento_array_partes[i]
            
            if self.array_partes[i] <= self.vermelho:
                est_vermelho = True
            elif self.array_partes[i] <= self.amarelo:
                est_amarelo = True
        
        if est_vermelho:
            print(Fore.RED + f"Linha {numero_linha} - Nível estoque de partes: Vermelho" + Style.RESET_ALL)
        elif est_amarelo:
            print(Fore.YELLOW + f"Linha {numero_linha} - Nível estoque de partes: Amarelo" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Linha {numero_linha} - Nível estoque de partes: Verde" + Style.RESET_ALL)
    
    def set_ordem_producao(self, ordem_producao):
        self.ordem_producao = ordem_producao
    
    def add_ordem_producao(self, ordem_producao):
        self.ordem_producao = self.ordem_producao + ordem_producao

    def decrementar_ordem_producao(self):
        self.ordem_producao = self.ordem_producao - 1
    
    def incrementar_qtd_produtos_prontos(self):
        self.qtd_produtos_prontos += 1
    
    def set_qtd_produtos_prontos(self, qtd_produtos_prontos):
        self.qtd_produtos_prontos = qtd_produtos_prontos

    def decrementar_partes_array(self):
        est_vermelho = False
        est_amarelo = False

        for i in range(len(self.array_partes)):
            self.array_partes[i] -= 1

            if self.array_partes[i] <= self.vermelho:
                est_vermelho = True
            elif self.array_partes[i] <= self.amarelo:
                est_amarelo = True
        
        if est_vermelho:
            print(Fore.RED + f"Linha {numero_linha} - Nível estoque de partes: Vermelho" + Style.RESET_ALL)
        elif est_amarelo:
            print(Fore.YELLOW + f"Linha {numero_linha} - Nível estoque de partes: Amarelo" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Linha {numero_linha} - Nível estoque de partes: Verde" + Style.RESET_ALL)



    def imprimir(self):
        print("..............................")
        print("Linha - dados atuais:")
        print(f"Linha - Qtd partes: {self.array_partes}")
        print(f"Linha - Qtd atual de ordens de produção: {self.ordem_producao}")
        print(f"Linha - Qtd de produtos prontos: {self.qtd_produtos_prontos}")
        print("..............................")

linha = Linha(0, 0, [0,0,0,0,0,0,0,0,0,0], 0)

broker = 'broker.emqx.io'
port = 1883

# Quantidade de produtos para serem feitos
topic_ordem_producao = "viniciusog-sd-ordem-producao" # para cada produto, vamos usar uma quantidade de partes
topic_produtos_prontos = "viniciusog-sd-fabrica-produtos-prontos"

topic_linha_solicita_partes = "viniciusog-sd-linha-solicitacao-partes"

# * linha faz pub em topico de produtos prontos da fábrica

client_id = f'python-mqtt-{random.randint(0, 1000)}'
print("client_id: " + str(client_id) + "\n")

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao MQTT Broker!")
            print("Linha - Carregando informações para serem exibidas...")
        else:
            print("Falha ao conectar no MQTT Broker. Código de retorno: %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def possui_partes_suficientes():
    for i in range(len(linha.array_partes)):
        if linha.array_partes[i] <= linha.vermelho:
            return False
    return True

def fabricar_produtos(my_client):
    # * depois temos que fazer um while, enquanto peças for zero, pede para a fábrica mais peças
    while True:
        if linha.ordem_producao > 0 and possui_partes_suficientes():
            print("Linha - Fazendo produto.")
            time.sleep(1)
            print(f"Linha - Total atual de ordens de produção existentes: {linha.ordem_producao}")
            print("Linha - Produziu 1 produto")
            linha.decrementar_ordem_producao()
            print("Linha - Decrementou qtd da ordem existente")
            linha.decrementar_partes_array()
            print("Linha - Decrementou quantidade de partes")
            linha.incrementar_qtd_produtos_prontos()
            incrementar_produtos_prontos_fabrica(my_client)
            print("Linha - Incrementou quantidade de produtos feitos")
            linha.imprimir()
            print("------------------------------")

def incrementar_produtos_prontos_fabrica(my_client):
    msg = f"Incrementar/{numero_linha}"
    result = my_client.publish(topic_produtos_prontos, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Linha - Incrementar qtd produtos prontos na fábrica. `{msg}` enviada ao tópico`{topic_produtos_prontos}`")
    else:
        print(f"Linha - Falha - Incrementar qtd produtos prontos na fábrica. `{msg}` enviada ao tópico`{topic_produtos_prontos}`")

def loop_verificar_partes(my_client):
    while True:
        time.sleep(5)
        # Se tiver alguma parte sendo 0, então solicita para a fábrica
        for i in range(len(linha.array_partes)):
            if linha.array_partes[i] <= linha.vermelho:
                solicitar_pecas(my_client)
                break    

def solicitar_pecas(my_client):
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

        if msg.topic == topic_ordem_producao and str(msg.payload.decode()).startswith("Fabrica"):
            # Fabrica/{numero_fabrica}/Linha/{n_produto}/{qtd_produtos}
            resultados_msg = str(msg.payload.decode()).split('/')
            n_fabrica = int(resultados_msg[1])
            n_linha = int(resultados_msg[3])
            qtd_produtos = int(resultados_msg[4])

            if n_linha == numero_linha:
                print(f"Linha - Ordem de produção recebida `{msg.payload.decode()}` do tópico `{msg.topic}`")
                linha.add_ordem_producao(qtd_produtos)
                linha.imprimir()

        elif msg.topic == topic_linha_solicita_partes and not str(msg.payload.decode()).startswith("Linha"):
            # Fabrica/Linha/{numero_linha}/[1,2,3,4,5,10,9,8,7,6]"
            valores_msg = str(msg.payload.decode()).split('/')
            n_linha = valores_msg[2]
            array_quantidade_partes = ast.literal_eval(valores_msg[3])
            uuid_recebido_solicitacao_partes = valores_msg[4]
            
            global uuid_solicitacao_partes

            # Se o uuid recebido é diferente do anterior
            if int(n_linha) == numero_linha and not uuid_recebido_solicitacao_partes == uuid_solicitacao_partes:
                print(f"Linha - Partes recebidas `{msg.payload.decode()}` do tópico `{msg.topic}`")
                linha.add_array_partes(array_quantidade_partes)
                linha.imprimir()
                uuid_solicitacao_partes = uuid_recebido_solicitacao_partes

    client.subscribe(topic_ordem_producao)
    client.subscribe(topic_linha_solicita_partes)
    client.on_message = on_message

def run():
    global numero_linha
    numero_linha = int(input("Insira o número da linha: "))
    linha.identificador = numero_linha

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