FROM python:3.9-alpine3.18

### Install linux packages
RUN apk update && apk --no-cache add python3-dev \
  libpq-dev \
  gcc \
  musl-dev

## Install python libraries
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app
COPY . .

CMD ["python", "main.py", "", "", ""]
