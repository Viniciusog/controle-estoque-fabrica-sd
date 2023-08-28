import random
import requests
import sys
import os
import time

valor_da_variavel = os.environ.get('variavel_legal')

if valor_da_variavel:
    print(f'O valor da variável de ambiente é: {valor_da_variavel}')
else:
    print('A variável de ambiente não está definida.')

while True:
    print(f'O valor da variável de ambiente é: {valor_da_variavel}')
    time.sleep(1)
    
if len(sys.argv) < 2:
    print("Uso: python script.py <argumento>")
else:
    argumento = sys.argv[1]
    print("Argumento recebido:", argumento)

# Verificando a parte de parâmetros por container docker

print("Seu número aleatório (1-10): " + str(random.randint(1, 10)))

""" URL = 'http://www.imdb.com/chart/top'
response = requests.get(URL)
print("\nResponse\n")
print(response.content)

palavra = input("Digite alguma palavra para teste: ")
print("sua palavra: " + str(palavra)) """