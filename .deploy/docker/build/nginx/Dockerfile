FROM nginx
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d
COPY ./routes.conf /etc/nginx/conf.d