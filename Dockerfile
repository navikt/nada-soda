FROM python:3.10

ARG USER=soda
ARG UID=1070
ARG USER_HOME_DIR=/home/soda

WORKDIR /app

COPY run.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

ENV SODA_API http://nada-soda.nada

RUN adduser --disabled-password --quiet "${USER}" --uid "${UID}" --gid "1070" --home "${USER_HOME_DIR}" && \
    mkdir -p "${USER_HOME_DIR}" && chown -R "${USER}:0" "${USER_HOME_DIR}"

USER ${USER}

CMD ["python", "run.py"]
