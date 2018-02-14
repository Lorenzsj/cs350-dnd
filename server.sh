#!/bin/bash

cd /opt/drjimbo-game

# Run the actual program.
uwsgi --wsgi-file fcgi/fcgi.py --callable app --socket 127.0.0.1:3030
