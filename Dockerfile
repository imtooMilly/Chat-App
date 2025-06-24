FROM python:3.11

# changes home env to root
ENV HOME /root

# cd to root
WORKDIR /root

# copy
COPY . .

# install requirements in image
RUN pip3 install -r requirements.txt

# Allows port 8000 to be accessed from out of container
EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait 
RUN chmod +x /wait

# Run app (-u flag forces stdout and stderr to be unbuffered)
CMD /wait && python3 -u server.py