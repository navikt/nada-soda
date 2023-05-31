FROM python:3.10

LABEL "org.opencontainers.image.source"="https://github.com/navikt/nada-soda"

WORKDIR /app

COPY run.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

ENV SODA_API http://nada-soda.nada

CMD ["python", "run.py"]
