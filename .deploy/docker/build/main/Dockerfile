FROM python:3.10
WORKDIR /project
COPY ./.deploy/docker/build/main/requirements.txt /project/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /project/requirements.txt
COPY ./.deploy/docker/build/main/start.sh /project
COPY ./manage.py /project
COPY ./TODO.md /project
COPY ./apps/ /project/apps/
COPY ./demo/ /project/demo/
#RUN python manage.py collectstatic --noinput
