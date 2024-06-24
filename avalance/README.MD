# Roumerchi

## QuickStart

commands to boostrap environment

    sudo apt-get update

    sudo apt-get install -y get python3-dev python3-venv python3-pip supervison nginx vimlibpq-dev fail2ban

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


## SystemMd files

- /etc/systemd/system/gunicorn.socket
- /etc/systemd/system/gunicorn.service


