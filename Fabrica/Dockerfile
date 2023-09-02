FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./fabrica.py /code/fabrica.py
COPY ./utilsProdutos.py /code/utilsProdutos.py

CMD ["python3", "fabrica.py"]