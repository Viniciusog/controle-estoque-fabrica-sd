FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./teste.py /code/teste.py

# Para conseguir passar variável de ambiente, precisa ser assim:
# docker run -it -e variavel_legal=valor_que_voce_quer_para_a_variavel cont1
ENV variavel_legal=valorlegal1

CMD ["python", "teste.py"]