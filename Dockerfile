# syntax=docker/dockerfile:1

FROM python:3.8

ENV TZ="Europe/Berlin"

WORKDIR /python-docker

COPY reqs.txt reqs.txt
COPY templates/ templates/
RUN pip3 install -r reqs.txt

COPY . .

ENTRYPOINT [ "python3" ]

CMD [ "lweb.py"]