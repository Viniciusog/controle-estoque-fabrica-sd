FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./almoxarifado.py /code/almoxarifado.py

CMD ["python3", "almoxarifado.py"]