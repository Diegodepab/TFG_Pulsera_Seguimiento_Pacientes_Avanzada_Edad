FROM python:3.10.13
LABEL maintainer = "aprendiendo <Diegodepablouma@gmail.com>"

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
RUN pip install --no-cache poetry==2.1.3
RUN poetry config virtualenvs.create false

COPY backend/bracelet-lib /bracelet-lib
COPY backend/api/poetry.lock /code
COPY backend/api/pyproject.toml /code

RUN cd /code \
  && poetry install --no-root

COPY backend/api /code

EXPOSE 8000
WORKDIR /code

CMD [ "gunicorn", \
      "main:app", \
      "--bind", \
      "0.0.0.0:8000", \
      "-k", \
      "uvicorn.workers.UvicornWorker", \
      "--keep-alive", \
      "120", \
      "-w", \
      "2", \
      "--timeout", \
      "300", \
      "--log-level=info", \
      "--log-file", \
      "-", \
      "--access-logfile", \
      "-", \
      "--capture-output" ]
