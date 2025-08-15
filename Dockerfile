FROM python:3.11

ENV PYCHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY mysite .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]