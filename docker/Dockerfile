FROM ubuntu:18.04

MAINTAINER lferiani <l.feriani@lms.mrc.ac.uk>

# add user
RUN adduser --quiet --disabled-password tierpsy_user

# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

# Install Python 3, PyQt5
RUN apt-get update && apt-get install -y python3-pyqt5 python3-pip git

# pre-create the workdir to make it work with github actions
RUN mkdir /EggCounting && chown -R tierpsy_user:tierpsy_user /EggCounting

# switch user
USER tierpsy_user
ENV HOME="/home/tierpsy_user"

# set the working directory in the container
WORKDIR /EggCounting
RUN whoami
RUN ls -lah /
RUN pwd
RUN ls -lah .

# get the source code
RUN git clone https://github.com/Tierpsy/EggCounting.git .
RUN pwd
RUN ls -lah .

# copy the dependencies file to the working directory
COPY docker_requirements.txt ./docker_requirements.txt

# install dependencies
RUN pip3 install -r docker_requirements.txt

# install code
RUN pip3 install .

# add location of command scripts to path
ENV PATH="${PATH}:/home/tierpsy_user/.local/bin"
RUN echo $PATH

# create folder for data sharing
RUN mkdir $HOME/DATA

# launch app
CMD ["count_eggs"]
