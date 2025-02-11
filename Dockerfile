FROM python:3.11 AS build

WORKDIR /build

COPY . .

RUN python -m pip wheel --wheel-dir wheels .


FROM python:3.11-slim

RUN apt update
RUN apt-get install -y libglib2.0-0 libasound2-dev avahi-utils systemd

WORKDIR /app

COPY --from=build /build/wheels wheels

RUN python -m pip install --find-links wheels nostmack_hub

RUN rm -rf wheels

CMD [ "python", "-u", "-m", "nostmack_hub" ]