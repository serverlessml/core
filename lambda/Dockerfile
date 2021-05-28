FROM python:3.8-slim AS base

LABEL maintener="Dmitry Kisler"
LABEL email="admin@dkisler.com"
LABEL web="www.serverlessml.org"

WORKDIR /

COPY . .

RUN pip install pip==20.3 --upgrade \
    && pip install --target / awslambdaric \
    && pip install -r requirements.txt --no-cache-dir \
    && rm -rf requirements.txt \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "main.run" ]
