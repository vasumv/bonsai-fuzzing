FROM ubuntu:latest

RUN mkdir /home/bonsai-fuzzing-artifact
ENV HOME /home/bonsai-fuzzing-artifact
ENV JQF_DIR=/home/bonsai-fuzzing-artifact/jqf/

WORKDIR $HOME
COPY /jqf/ ./jqf/
COPY /picireny/ ./picireny/
COPY /picire/ ./picire/
COPY /bonsai-fuzzing/ ./bonsai-fuzzing/
COPY /pre-baked/ ./pre-baked/
COPY requirements.txt ./requirements.txt
COPY chocopy-2.2-ref.jar ./bonsai-fuzzing/

# Installing Python
RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

# Installing Git
RUN apt-get install -y git

# Installing Picire and Picireny
RUN cd $HOME/picire && python3 setup.py install
RUN cd $HOME/picireny && python3 setup.py install


# Installing Java 8 and Maven
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install openjdk-8-jdk
RUN apt-get install -y maven

# Installing ChocoPy Reference
RUN cd $HOME/bonsai-fuzzing && mvn install:install-file -Dfile=chocopy-2.2-ref.jar -DgroupId=chocopy -DartifactId=chocopy -Dversion=2.2 -Dpackaging=jar

# Installing JQF
RUN cd $HOME/jqf && mvn install -Dmaven.test.skip=True

# Build Bonsai and set CLASSPATH
RUN cd $HOME/bonsai-fuzzing && mvn clean package -Dmaven.test.skip=True && bash ./scripts/classpath.sh

