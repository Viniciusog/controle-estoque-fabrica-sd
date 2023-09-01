# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# pip freeze > requirements.txt

# python3 -m venv venv

# esquerda é a porta no container do docker e direita é a porta no nosso pc mesmo
# estamos mapeando a porta 80 do container para a nossa porta 80 do pc
# docker run -p 80:80 fastapi-teste
# ou
# docker run -it para executar o container em modo interativo

# Abrir um terminal dentro do WORKDIR do container definido no Dockerfile
# docker exec -it id_do_container /bin/sh

FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]