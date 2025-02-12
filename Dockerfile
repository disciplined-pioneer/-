FROM python:3.12-slim

WORKDIR /bot

COPY requirements.txt .

RUN apt-get -y update
RUN apt-get install -y libgl1-mesa-glx libzbar0 wkhtmltopdf

RUN rm -rf /etc/localtime
RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN echo "Europe/Moscow" > /etc/timezone

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "bot.py"]
