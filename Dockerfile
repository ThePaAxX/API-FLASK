FROM python:3.13
# Ya no es necesario exponer el puerto 5000 ya que se expondra en el 80 con gunicorn
#EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir  --upgrade -r requirements.txt
COPY . . 
# CMD ["flask", "run", "--host", "0.0.0.0", "--reload"]
CMD ['gunicorn', '--bind', '0.0.0.0:80', 'app:create_app()']