FROM python:3.9.6

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

