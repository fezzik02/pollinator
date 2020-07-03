FROM selenium/standalone-chrome:3.141.59-20200525

USER root
RUN apt-get update && apt-get upgrade -qq && apt-get install python3-pip -qq
COPY requirements.txt /opt/pollinator/
RUN pip3 install -r /opt/pollinator/requirements.txt
COPY entrypoint.sh /entrypoint.sh
WORKDIR /opt/pollinator/src
COPY src /opt/pollinator/src
USER seluser
ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]
