# Custom location for static files. mydomain.com needs to be renamed to your domain
location /static/ {
    alias /usr/share/nginx/html/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";

    # Try to serve the file directly, if not found continue to app
    try_files $uri $uri/ =404;
}