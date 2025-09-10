FROM python:3.12-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 7860

CMD ["python", "app.py"]