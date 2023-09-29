# Docker container for fetching recent papers and
# curating them based on user topics.

# https://hub.docker.com/_/python
FROM python:3.11.5-bookworm

WORKDIR /app

RUN pip install openai requests

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY fetch_recent_papers.py /app
COPY curate.py /app

CMD [ "sleep", "infinity" ]