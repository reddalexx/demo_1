FROM python:3.10
WORKDIR /project
COPY ./.deploy/docker/build/fastapi/requirements.txt /project/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /project/requirements.txt
COPY ./apps/hotels/fastapi/app /project/app
