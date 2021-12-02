FROM noddi89/poetry-base:1.1.11-3.10 as base
ENV PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" 

# We copy our Python requirements here to cache themp
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev


FROM python:3.10.0-slim-bullseye as production

# Venv into image
COPY --from=base $VENV_PATH $VENV_PATH

# Copying in our entrypoint
COPY ./docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY ./discgolfspider /discgolfspider
WORKDIR /

ENTRYPOINT /docker-entrypoint.sh $0 $@
#CMD ["python", "discgolfspider/main.py"]