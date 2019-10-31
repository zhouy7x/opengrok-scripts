From opengrok/docker:latest

#ENVIRONMENT VARIABLES CONFIGURATION
ENV SRC_ROOT /src
ENV DATA_ROOT /data
ENV OPENGROK_WEBAPP_CONTEXT /
ENV OPENGROK_TOMCAT_BASE /usr/local/tomcat
ENV CATALINA_HOME /usr/local/tomcat
ENV PATH $CATALINA_HOME/bin:$PATH
ENV CATALINA_BASE /usr/local/tomcat
ENV CATALINA_HOME /usr/local/tomcat
ENV CATALINA_TMPDIR /usr/local/tomcat/temp
ENV JRE_HOME /usr
ENV CLASSPATH /usr/local/tomcat/bin/bootstrap.jar:/usr/local/tomcat/bin/tomcat-juli.jar
ENV PORT 9090
ENV FREQ 7d
ENV http_proxy http://child-prc.intel.com:913
ENV https_proxy http://child-prc.intel.com:913
ENV NO_PROXY localhost,127.0.0.1
# add setenv.sh
COPY setenv.sh $CATALINA_BASE/bin/

# Tomcat tuning for HTTP headers
RUN rm -f $CATALINA_BASE/conf/server.xml
COPY server.xml $CATALINA_BASE/conf/

# add our scripts
RUN rm -rf /scripts
ADD scripts/ /scripts
RUN chmod -R +x /scripts

# run
WORKDIR $CATALINA_HOME
EXPOSE $PORT
CMD ["/scripts/autorun.py"]
