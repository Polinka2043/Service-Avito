FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y git
COPY . .
ENV FLASK_APP=launcher
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]