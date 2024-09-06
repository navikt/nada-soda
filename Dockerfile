FROM python:3.11-slim AS builder

LABEL "org.opencontainers.image.source"="https://github.com/navikt/nada-soda"

ARG USER=soda
ARG UID=1069
ARG USER_HOME_DIR=/home/soda

RUN groupadd -g ${UID} ${USER}

RUN adduser --disabled-password --quiet "${USER}" --uid "${UID}" --gid "${UID}" --home "${USER_HOME_DIR}" && \
    mkdir -p "${USER_HOME_DIR}" && chown -R "${USER}:${USER}" "${USER_HOME_DIR}"

WORKDIR /app

COPY requirements.txt .

RUN python3 -m venv venv --without-pip
RUN pip --python venv/bin/python install -r requirements.txt


FROM gcr.io/distroless/python3-debian12 AS runner

ARG USER=soda
ARG USER_HOME_DIR=/home/soda

COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group
COPY --from=builder ${USER_HOME_DIR} ${USER_HOME_DIR}

COPY --from=builder /app /app       

ENV PYTHONPATH="/app/venv/lib/python3.11/site-packages"
ENV PATH="/app/venv/bin:${PATH}"

ENV SODA_API=http://nada-soda.nada

WORKDIR /app

COPY run.py .

USER ${USER}

ENTRYPOINT ["python3", "run.py"]
