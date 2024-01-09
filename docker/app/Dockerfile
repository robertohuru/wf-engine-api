FROM python:3.8
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python3-dev gcc libc-dev

# Create data directory some permissions
RUN mkdir -p /home/data \
    && chmod 777 -R /home/data \
    && chown -R www-data /home/data

# Create an app directory
WORKDIR /home/app

RUN pip install --upgrade pip
RUN pip install gunicorn

ADD ./requirements.txt /home/app/
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin


RUN apt-get update && apt-get install -y libqt5gui5
RUN apt-get update && apt-get install -y python3-pyqt5.qtwebengine
RUN apt-get update && apt-get install libqt5concurrent5
RUN pip install pyqt5
RUN apt-get install libgdal-dev -y
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install GDAL==$(ogrinfo --version | cut -d' ' -f2 | cut -d',' -f1)

ADD ./ /home/app/
ADD ./docker /home/app/docker

RUN pip install /home/app/docker/app/ilwis-1.0.20230929-cp38-cp38-linux_x86_64.whl

RUN chmod +x /home/app/docker/app/server-entrypoint.sh
RUN chmod +x /home/app/docker/app/worker-entrypoint.sh
