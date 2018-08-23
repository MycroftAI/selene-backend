bind = "0.0.0.0:5000"
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
capture_output = True
keyfile = '/etc/ssl/certs/localhost.key'
certfile = '/etc/ssl/certs/localhost.crt'
ca_certs = '/etc/ssl/certs/rootCA.pem'
