FROM ubuntu:20.04

# for testing
RUN apt-get update && apt-get install --no-install-recommends -y \
  python3 \
  python3-click \
  python3-pip \
  rsyslog \
  iproute2

# for testing
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# for testing
COPY ROOTFS/etc/rsyslog.d/* /etc/rsyslog.d/

COPY . /workdir
WORKDIR /workdir
