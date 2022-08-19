FROM python:3

ADD plex_rd.py /

ENV TERM=xterm

RUN pip install requests

RUN pip install bs4

RUN pip install regex

RUN pip install six

CMD [ "python", "./plex_rd.py", "-e", "TERM=xterm"]
