FROM python:3.6.5

ARG GITHUB_OAUTH_TOKEN
ARG PORT


ENV CODEROOT=/home/docker/code

#RUN git submodule init
#RUN git submodule update
ADD . $CODEROOT/

RUN apt-get clean \
    && apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install sudo \
    && apt-get -y install build-essential
#RUN mkdir -p ~/.ssh
#RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts 

RUN echo $GITHUB_OAUTH_TOKEN

RUN sed -i "s@git+ssh:\/\/git@git+https:\/\/$GITHUB_OAUTH_TOKEN@" $CODEROOT/requirements.txt

RUN pip install --upgrade pip



RUN pip install -r $CODEROOT/requirements.txt


COPY nginx.conf /etc/nginx
RUN sed -i "s@5380@$PORT@" /etc/nginx/nginx.conf 
RUN chmod +x $CODEROOT/start.sh

WORKDIR $CODEROOT
CMD $CODEROOT/start.sh

#CMD python $CODEROOT/run.py

EXPOSE $PORT 
