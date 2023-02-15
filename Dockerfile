#Deriving the latest base image
FROM python:latest

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /opt

#to COPY the remote file at working directory in container
COPY main.py ./opt/
# Now the structure looks like this '/opt/main.py'


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./main.py"]

