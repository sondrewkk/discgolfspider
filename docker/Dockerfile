FROM python:3.11.8 as req-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11.8-slim

WORKDIR /discgolfspider
ENV PYTHONPATH "${PYTHONPATH}:/discgolfspider"

COPY --from=req-stage /tmp/requirements.txt /discgolfspider/requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libxml2-dev libxslt-dev python3-dev libffi-dev libssl-dev\
    && rm -rf /var/lib/apt/lists/* \
    && pip install cryptography \
    && pip install --no-cache-dir --upgrade -r /discgolfspider/requirements.txt \
    && apt-get purge -y --auto-remove gcc build-essential libxml2-dev libxslt-dev python3-dev libffi-dev libssl-dev 

COPY ./discgolfspider /discgolfspider/discgolfspider
COPY ./scrapy.cfg /discgolfspider/scrapy.cfg

CMD ["python", "discgolfspider/main.py"]