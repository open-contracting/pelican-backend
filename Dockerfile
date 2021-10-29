FROM python:3

WORKDIR /workdir

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -r pelican && useradd --no-log-init -r -g pelican pelican

USER pelican:pelican

COPY --chown=pelican:pelican . .

ENTRYPOINT [ "python", "-m"]
