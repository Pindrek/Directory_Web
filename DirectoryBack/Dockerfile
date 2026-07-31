FROM python:3.14-slim
WORKDIR /back

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "DirectoryBack.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]