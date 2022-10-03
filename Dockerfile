FROM python:3

ADD plex_rd.py /
ADD requirements.txt /

ENV TERM=xterm

RUN pip install -r requirements.txt

CMD [ "python", "./plex_rd.py", "-e", "TERM=xterm"]
