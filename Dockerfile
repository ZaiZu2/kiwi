FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]
RUN useradd kiwi
WORKDIR /home/kiwi

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y sqlite3

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY requirements_prod.txt requirements_prod.txt
RUN pip install -r requirements_prod.txt

COPY . .
RUN mkdir -p logs
RUN chown -R kiwi:kiwi .
USER kiwi

EXPOSE 8000
# Listen on all interfaces, not just localhost
CMD ["uvicorn", "app:app", \
    "--host", "0.0.0.0" \
    # "--log-config", "logging_config.json"
    ]