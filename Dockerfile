#Deriving the latest base image
FROM python:latest

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /opt

#to COPY the remote file at working directory in container
COPY main.py ./opt/
<<<<<<< HEAD
# Now the structure looks like this '/usr/app/src/test.py'
=======
# Now the structure looks like this '/opt/main.py'
>>>>>>> nginx access log parsing using python


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

<<<<<<< HEAD
CMD [ "python", "./main.py"]
=======
CMD [ "python", "./main.py"]

>>>>>>> nginx access log parsing using python
