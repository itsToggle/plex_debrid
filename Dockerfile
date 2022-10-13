FROM python:3

ADD requirements.txt /

RUN pip install -r requirements.txt

ADD plex_rd.py /

ENV TERM=xterm

CMD [ "python", "./plex_rd.py", "-e", "TERM=xterm"]
