FROM debian:11.5
RUN apt-get update

# install the base environment apache2+python+django
RUN apt-get install -y apt-utils 
RUN apt-get install -y vim curl 
RUN apt-get install -y apache2 apache2-utils 
RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev

RUN apt-get install -y python3
RUN rm /usr/bin/python
RUN ln /usr/bin/python3 /usr/bin/python

RUN apt-get install -y libapache2-mod-wsgi-py3
RUN apt-get install -y python3-pip 
RUN pip install --upgrade pip 
RUN pip install django ptvsd 

# install project specific requirements
WORKDIR /var/www/html 
ADD ./requirements.txt /var/www/html 
RUN pip install -r requirements.txt 

# start apache
CMD ["apache2ctl", "-D", "FOREGROUND"]
