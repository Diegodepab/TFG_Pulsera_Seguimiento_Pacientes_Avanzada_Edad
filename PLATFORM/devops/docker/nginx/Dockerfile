FROM node:20.10.0 as build-deps
LABEL maintainer = "Diego De Pablo"

RUN mkdir /platform
COPY frontend/platform/package.json /platform
COPY frontend/platform/package-lock.json /platform
COPY frontend/platform/.npmrc /platform

RUN cd /platform \
    && npm install

COPY frontend/platform/ /platform

RUN cd /platform \
    && npm run build \
    && chown -R node:node /platform


FROM nginx:1.23
LABEL maintainer = "Diego De Pablo"

RUN apt-get update \
 && apt-get -y install wget zlib1g-dev libpcre3-dev libssl-dev build-essential \
 && mkdir /tmp/nginx \
 && cd /tmp/nginx \
 && wget http://nginx.org/download/nginx-1.21.3.tar.gz \
 && wget https://github.com/openresty/headers-more-nginx-module/archive/refs/tags/v0.33.tar.gz \
 && tar xzvf nginx-1.21.3.tar.gz \
 && tar xzvf v0.33.tar.gz \
 && cd nginx-1.21.3 \
 && ./configure --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --modules-path=/usr/lib/nginx/modules --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module --with-cc-opt='-g -O2 -fdebug-prefix-map=/data/builder/debuild/nginx-1.21.3/debian/debuild-base/nginx-1.21.3=. -fstack-protector-strong -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fPIC' --with-ld-opt='-Wl,-z,relro -Wl,-z,now -Wl,--as-needed -pie' --add-dynamic-module=/tmp/nginx/headers-more-nginx-module-0.33 \
 && make -j8 \
 && make install \
 && apt-get -y remove wget zlib1g-dev libpcre3-dev libssl-dev build-essential \
 && apt -y autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build-deps /platform/build/ /usr/share/nginx/platform
