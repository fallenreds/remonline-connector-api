FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNVUFFERED 1

WORKDIR /backend

COPY requirements.txt /backend/requirements.txt
RUN pip install -r /backend/requirements.txt

COPY . /backend


EXPOSE 8000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

