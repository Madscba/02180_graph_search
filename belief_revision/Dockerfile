from python:3.8

COPY Pipfile Pipfile.lock /app/
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system --deploy

COPY *.py /app/

ENTRYPOINT [ "python", "-u" ]
CMD ["cli.py"]
