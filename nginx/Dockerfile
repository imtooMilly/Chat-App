FROM nginx

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./cert.pem /etc/nginx/cert.pem
COPY ./private.key /etc/nginx/private.key

# Expose ports
EXPOSE 80
EXPOSE 443

# CMD ["nginx", "-g", "daemon off;"]