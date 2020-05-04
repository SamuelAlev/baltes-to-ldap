FROM python:3.8.2-slim

# Add GCC/G++ dependencies
RUN apt-get update \
  && apt-get install gcc g++ python-dev libldap2-dev libsasl2-dev libssl-dev -y \
  && apt-get clean


# install FreeTDS and dependencies
RUN apt-get install unixodbc -y \
  && apt-get install unixodbc-dev -y \
  && apt-get install freetds-dev -y \
  && apt-get install freetds-bin -y \
  && apt-get install tdsodbc -y \
  && apt-get install --reinstall build-essential -y \
  && apt-get clean

# populate "ocbcinst.ini"
RUN echo "[FreeTDS]\n\
  Description = FreeTDS unixODBC Driver\n\
  Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
  Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --user -r requirements.txt

# Copy file to Docker folder
COPY . /app

CMD ["python", "/app/main.py"]