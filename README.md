# Raspberry Pi Surveillance Camera
##### Students project, Winter Semester 2016
##### Network Software Systems Laboratory (NSSL), Technion, Israel Institute of Science

The Raspberry Pi surveillance camera is a self-contained surveillance system. It is based entirely on the Raspberry Pi (tested only on the Raspberry Pi 2 model B) and the Pololu Maestro Micro.

Amongst the features the system enables, you can find:
* Intuitive Django-based multiuser web interface
* Streaming video
* Full control on the camera direction via servo control
* Built-in motion detection for the video, and motion-detection based video capture
* Integration with Dropbox API for uploading of captured videos and images

The system integrates the following software packages:
* For the web server:
  * NGINX
  * Django
* General backend:
  * RabbitMQ
* For video and motion detection:
  * UV4L
  * Motion
* For backups and space management:
  * The Dropbox core API
* For task management:
  * Celery

(Installation instructions will be added here in the future)
