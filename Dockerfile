FROM python:3

WORKDIR /app

Add . /app
RUN pip install -r requirements.txt

EXPOSE 8082

CMD ["python", "./app.py"]