# Roumerchi

## Start
commands to boostrap environment

    sudo apt-get update

    sudo apt-get install -y get python3.9-dev python3.9-venv python3-pip supervison nginx vimlibpq-dev

    git clone https://github.com/razingash/roumerchi
    cd roumerchi
    
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements/prod.txt

    while read file; do
        export "$file"
        done < .env

run app locally

    python manage.py runsevrer

run app  using docker

    docker compose up

- django http://127.0.0.1:8001/roumerchi/
- nginx http://localhost:80/roumerchi/


## Conf files

- /etc/systemd/system/gunicorn.socket
- /etc/systemd/system/gunicorn.service
- /etc/supervisor/conf.d/
- /etc/nginx/sites-available/default
- /etc/nginx/nginx.conf

## Google cloud installation
briefly - create a Vm instance and change its IP address to static

### Adding/updating environment variables
    while IFS= read -r line; do
        export "$line"
        done < .env


### configuration for supervisor
#### path - /etc/supervisor/conf.d/

    [program:avalance]
    command=/home/roumerchi/venv/bin/gunicorn --bind=127.0.0.1:8000 avalance.wsgi:application --timeout 60
    autostart=true
    autorestart=true
    directory=/home/roumerchi/roumerchi/avalance
    stderr_logfile=/var/log/avalance/err.log
    stdout_logfile=/var/log/avalance/out.log

### nginx commands
    reload: systemctl reload nginx

### supervisor commands
    update: supervisorctl update
    restart: supervisorctl restart avalance
