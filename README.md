# Toontown Next Website

====
Requirements
 - Use pip to install:

    pip install git+https://github.com/django-nonrel/django@nonrel-1.5
    pip install git+https://github.com/django-nonrel/djangotoolbox
    pip install git+https://github.com/django-nonrel/mongodb-engine

  - MongoDB on localhost
 
====
Running

 1. Start a python smtp server that redirects all emails to stdout:
    `python -m smtpd -n -c DebuggingServer localhost:1025`
 
 2. Run django:
    `python manage.py runserver` (add `0.0.0.0:8000` to allow external access)
