#!/bin/bash

### Sources:
# http://blog.mattwoodward.com/2013/01/setting-up-django-on-raspberry-pi.html
# http://www.hackedexistence.com/project/raspi/django-on-raspberry-pi.html

sudo su

if [ -z "$rpisetup_stage" ]; then
	export rpisetup_stage=0
fi

## Install needed packages
if [ "$rpisetup_stage" -eq "0" ]; then 
	echo -e "\e[34mInstalling packages...\e[39m"
	sudo apt-get install -y python-dev python-setuptools nginx supervisor
	sudo easy_install pip
	sudo pip install virtualenv virtualenvwrapper
	sudo echo "source /usr/local/bin/virtualenvwrapper.sh" >> /etc/bash.bashrc
	export rpisetup_stage=1
	echo "Please log out and log back in, then run setup again."
fi

## Make new django project called "rpisurvcam" under virtual env "rpiproj"
echo -e "\e[34mConfiguring new django project...\e[39m"
mkvirtualenv rpiproj
pip install django docutils gunicorn pika
django-admin.py startproject rpisurvcam

## Configure the django project
echo -e "\e[34mCopying django application settings...\e[39m"
USER_HOME=$(eval echo ~${SUDO_USER})
cp setup_files/settings.py $USER_HOME/rpisurvcam/rpisurvcam/
cp setup_files/urls.py $USER_HOME/rpisurvcam/rpisurvcam/
cp setup_files/gunicorn.conf /etc/supervisor/conf.d/
cp -r setup_files/survcam $USER_HOME/rpisurvcam/
sudo chown pi:pi $USER_HOME/rpisurvcam/
sudo chown pi:pi $USER_HOME/rpisurvcam/rpisurvcam.db

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

## You should get somthing like: "gunicorn     RUNNING     pid 11547 ..."
if [[ `sudo supervisorctl status` != *"RUNNING"* ]]; then
	echo -e "\e[91mPossible issue with gunicorn installation. see /var/log/supervisor/gunicorn_err.log\e[39m"
	exit
fi

## Create directories for web server and relate to rpisurvcam settings
echo -e "\e[34mCopying django application settings...\e[39m"
sudo mkdir /var/www /var/www/static /var/www/media
sudo chown -R pi:www-data /var/www
sudo cp -r setup_files/static/* /var/www/static/

python $USER_HOME/rpisurvcam/manage.py collectstatic <<< "yes"

echo -e "\e[34mConfiguring nginx web server...\e[39m"
## Setup Nginx - tell nginx that gunicorn is available as an upstream server at 127.0.0.1:8000
sudo cp setup_files/rpisurvcam /etc/nginx/sites-available/

## Create entry point for the project website on the nginx web server, removing the default one
cd /etc/nginx/sites-enabled
sudo ln -s ../sites-available/rpisurvcam
sudo rm default
cd $USER_HOME
sudo service nginx restart

### Not sure if we need to do this, as we already copied the app's directory:
## Create new application under the rpisurvcam project (called survcam)
# python $USER_HOME/rpisurvcam/manage.py startapp survcam
# cp -r setup_files/survcam $USER_HOME/rpisurvcam/

## Do data migrations
echo -e "\e[34mCreating database tables for survcam's application models...\e[39m"
python $USER_HOME/rpisurvcam/manage.py migrate

## Create an admin for django
echo -e "\e[34mCreating an admin for django...\e[39m"
python $USER_HOME/rpisurvcam/manage.py createsuperuser


## Continue from Django tutorial (https://docs.djangoproject.com/en/1.9/intro/tutorial01/)
## You can always kill nginx and start the development server using (with your ip):
#	sudo service nginx stop
#	sudo python manage.py runserver 132.68.60.145:80


