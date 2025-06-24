nginx ile çalıştırmak için ini dosyası oluşturuldu bu ini dosyasının sürekli çalıştırılması için servis oluşturulması gerekiyor. 
/etc/systemd/system/akrandegerlendirme.service:
```ini
[Unit]
Description=uWSGI instance to serve akran_degerlendirme
After=network.target

[Service]
User=sametatabasch
Group=www-data
WorkingDirectory=/home/sametatabasch/www/grafik.gencbilisim.net/public_html
Environment="PATH=/home/sametatabasch/www/grafik.gencbilisim.net/public_html/"
ExecStart=uwsgi --ini /home/sametatabasch/www/grafik.gencbilisim.net/public_html/akran_degerlendirme.ini

[Install]
WantedBy=multi-user.target

sonrasında 
sudo systemctl daemon-reload
sudo systemctl start akran_degerlendirme.service
sudo systemctl enable akran_degerlendirme.service
```

nginx yapılandırması da :
```
# 1. www.grafik.gencbilisim.net adresini yönlendirme
server {
    listen 80;
    listen [::]:80;
    server_name www.grafik.gencbilisim.net;

    return 301 http://grafik.gencbilisim.net$request_uri;
}

# grafik.gencbilisim.net - Only HTTP configuration for initial Certbot setup


server {
    server_name grafik.gencbilisim.net;

    index index.php;
    
    root /home/sametatabasch/www/grafik.gencbilisim.net/public_html/;
    
    # Security Headers for Protection (recommended)
    add_header X-XSS-Protection "1; mode=block" always;
   # add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none';" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; prefix=/" always;

    ### Logs
    access_log /var/log/nginx/grafik.gencbilisim.net-access.log;
    # if the log files become too large, you may use the following format. $loggable is defined in conf.d/common.conf
    # access_log /var/log/nginx/grafik.gencbilisim.net-access.log combined buffer=64k flush=5m if=$loggable;

    # ideally use it along with fail2ban
    error_log /var/log/nginx/grafik.gencbilisim.net-error.log;
    # use the following pattern only for debugging - server support needed
    # error_log /var/log/nginx/grafik.gencbilisim.net-error.log debug;



    include "globals/restrictions.conf";
    include "globals/assets.conf";

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/home/sametatabasch/www/grafik.gencbilisim.net/public_html/akran_degerlendirme.sock;
    }

    # Statik dosyaları servis et
    location /static/ {
        alias /home/sametatabasch/www/grafik.gencbilisim.net/public_html/static/;
        autoindex off;
    }

    # (Opsiyonel) Medya dosyaları için
    location /media/ {
        alias /home/sametatabasch/www/grafik.gencbilisim.net/public_html/media/;
        autoindex off;
    }

    location ~* \.(jpg|jpeg|gif|css|png|js|ico|html)$ {
        expires 30d;
        log_not_found off;
        add_header Cache-Control "public, max-age=2592000";
    }

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Expect-CT "enforce, max-age=30";

    location = /robots.txt {
        allow all;
        log_not_found off;
    }

    location ~* wp-config.php {
        deny all;
    }

    listen [::]:443 ssl; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/grafik.gencbilisim.net/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/grafik.gencbilisim.net/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}


server {
    if ($host = grafik.gencbilisim.net) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    listen [::]:80;
    server_name grafik.gencbilisim.net;
    return 404; # managed by Certbot


}
```