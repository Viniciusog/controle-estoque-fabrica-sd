FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ordemProducao.py /code/ordemProducao.py

CMD ["python3", "ordemProducao.py"]