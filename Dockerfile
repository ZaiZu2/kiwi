FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]
RUN useradd kiwi
WORKDIR /home/kiwi

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
CMD ["uvicorn", "app:app", \
    # Listen on all interfaces, not just localhost
    "--host", "0.0.0.0", \
    "--log-config", "logging_config.json"]
