FROM python:3.12-slim

WORKDIR /srv

ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

RUN pip install --no-cache-dir flask pymupdf google-genai

COPY ml.py /srv/

EXPOSE 7777

ENTRYPOINT ["python", "ml.py"]
