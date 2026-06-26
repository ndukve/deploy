ARG NGINX_IMAGE=nginx:1.28-alpine@sha256:5b4900b042ccfa8b0a73df622c3a60f2322faeb2be800cbee5aa7b44d241649e

FROM ${NGINX_IMAGE}

RUN apk add --no-cache openssl

COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/docker-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh
COPY docker/scripts/generate-local-cert.sh /usr/local/bin/generate-local-cert.sh

RUN chmod 0755 /usr/local/bin/nginx-entrypoint.sh /usr/local/bin/generate-local-cert.sh

ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
