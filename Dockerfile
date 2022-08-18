FROM nginx:1.23-alpine

# Make a self-signed SSL certificate
# RUN mkdir /cert
WORKDIR /cert
COPY ./nginx/openssl.conf .
RUN apk add openssl
RUN openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -config openssl.conf \
    -keyout /cert/ssl.key -out /cert/ssl.crt

# Copy custom config (SSL, CORS, ?)
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf


# Copy in the needed data
WORKDIR /usr/share/nginx/html
COPY ./data .

# Remove default index.html
RUN rm index.html
