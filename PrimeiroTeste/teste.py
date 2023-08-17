import random
import requests

print("Seu número aleatório (1-10): " + str(random.randint(1, 10)))

URL = 'http://www.imdb.com/chart/top'
response = requests.get(URL)
print("\nResponse\n")
print(response.content)

palavra = input("Digite alguma palavra para teste: ")
print("sua palavra: " + str(palavra))