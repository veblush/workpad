FROM adoptopenjdk/openjdk8:debian

RUN apt-get update && apt-get install -y wget patch

COPY build-jar.sh /root/build-jar.sh
RUN cd /root && ./build-jar.sh
