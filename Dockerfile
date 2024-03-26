FROM python:3.12

LABEL "org.opencontainers.image.source"="https://github.com/navikt/nada-soda"

ARG USER=soda
ARG UID=1069
ARG USER_HOME_DIR=/home/soda

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY run.py .

ENV SODA_API http://nada-soda.nada

RUN groupadd -g ${UID} ${USER}

RUN adduser --disabled-password --quiet "${USER}" --uid "${UID}" --gid "${UID}" --home "${USER_HOME_DIR}" && \
    mkdir -p "${USER_HOME_DIR}" && chown -R "${USER}:${USER}" "${USER_HOME_DIR}"

USER ${USER}

CMD ["python", "run.py"]
