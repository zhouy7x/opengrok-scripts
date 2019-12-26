FROM debian:stable-slim as fetcher

# TODO copy just the 'distribution' directory, not all source code
COPY ./ /opengrok-source
WORKDIR /opengrok-source

# update the system
ENV http_proxy http://10.239.4.80:913
ENV https_proxy http://10.239.4.80:913
RUN apt-get update

# find most recent package file
RUN cp `ls -t distribution/target/*.tar.gz | head -n1 |awk '{printf("%s",$0)}'` /opengrok.tar.gz

FROM tomcat:9-jre8
LABEL maintainer="zhouy7x@gmail.com"

# prepare OpenGrok binaries and directories
COPY --from=fetcher opengrok.tar.gz /opengrok.tar.gz
RUN mkdir -p /opengrok /opengrok/etc /opengrok/data /opengrok/src && \
    tar -zxvf /opengrok.tar.gz -C /opengrok --strip-components 1 && \
    rm -f /opengrok.tar.gz

# install dependencies and Python tools
ENV http_proxy http://10.239.4.80:913
ENV https_proxy http://10.239.4.80:913
RUN apt-get update && apt-get install -y git subversion mercurial unzip inotify-tools python python3 python3-pip python3-venv cron locales procps && \
    python3 -m pip install /opengrok/tools/opengrok-tools*

# compile and install universal-ctags
RUN apt-get install -y pkg-config autoconf build-essential && git clone https://github.com/universal-ctags/ctags /root/ctags && \
    cd /root/ctags && ./autogen.sh && ./configure && make && make install && \
    apt-get remove -y autoconf build-essential && apt-get -y autoremove && apt-get -y autoclean && \
    cd /root && rm -rf /root/ctags

# environment variables
ENV SRC_ROOT /opengrok/src
ENV DATA_ROOT /opengrok/data
ENV OPENGROK_WEBAPP_CONTEXT /
ENV OPENGROK_TOMCAT_BASE /usr/local/tomcat
ENV CATALINA_HOME /usr/local/tomcat
ENV CATALINA_BASE /usr/local/tomcat
ENV CATALINA_TMPDIR /usr/local/tomcat/temp
ENV PATH /depot_tools:$CATALINA_HOME/bin:$PATH
ENV JRE_HOME /usr
ENV CLASSPATH /usr/local/tomcat/bin/bootstrap.jar:/usr/local/tomcat/bin/tomcat-juli.jar
ENV PORT 8080
ENV http_proxy http://10.239.4.80:913
ENV https_proxy http://10.239.4.80:913
ENV NO_AUTH_BOTO_CONFIG /opengrok/.boto
ENV MIRROR 1
ENV DEBIAN_FRONTEND noninteractive

# set the locale
RUN locale-gen en_US.UTF-8

# clone depot_tools
RUN cd / && git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git && update_depot_tools

# custom deployment to / with redirect from /source
RUN rm -rf /usr/local/tomcat/webapps/* && \
    opengrok-deploy -c /opengrok/etc/configuration.xml \
        /opengrok/lib/source.war /usr/local/tomcat/webapps/ROOT.war && \
    mkdir "/usr/local/tomcat/webapps/source" && \
    echo '<% response.sendRedirect("/"); %>' > "/usr/local/tomcat/webapps/source/index.jsp"

# disable all file logging
ADD logging.properties /usr/local/tomcat/conf/logging.properties
RUN sed -i -e 's/Valve/Disabled/' /usr/local/tomcat/conf/server.xml

# add setenv.sh
COPY setenv.sh $CATALINA_BASE/bin/
COPY .boto /opengrok/.boto

# add crontab config file
COPY root /var/spool/cron/crontabs/root

# add our scripts
ADD scripts/ /scripts
RUN chmod -R +x /scripts

# run
WORKDIR $CATALINA_HOME
EXPOSE $PORT
CMD ["/scripts/start.sh"]

