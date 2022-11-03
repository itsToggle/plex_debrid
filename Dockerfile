FROM python:3

ADD . / ./

RUN pip install -r requirements.txt

ENV TERM=xterm

CMD [ "python", "./main.py --config-dir config", "-e", "TERM=xterm"]
