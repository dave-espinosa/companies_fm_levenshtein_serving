FROM python:3.9-slim
WORKDIR /code
RUN apt-get update
RUN apt-get -y install gcc
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN python -m nltk.downloader stopwords
COPY ./src /code/src
COPY ./data /code/data
EXPOSE 8080
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]