FROM python:3.11-slim

FROM cypress/browsers:latest

ENV PATH /home/root/.local/bin:${PATH}

WORKDIR /app

COPY requirements.txt .
RUN  apt-get update && apt-get install -y python3-pip && pip install -r requirements.txt  

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]