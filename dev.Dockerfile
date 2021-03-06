FROM registry.access.redhat.com/ubi8/ubi:8.1

EXPOSE 5000

RUN yum --disableplugin=subscription-manager --assumeyes install \
        https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    yum --disableplugin=subscription-manager --assumeyes install \
        git \
	gcc \
	python36-devel \
        python36
RUN pip3.6 install --upgrade pip && \
	python3 -m pip install --upgrade setuptools
RUN pip3.6 install \
        flask \
        flask-restful \
	etcd3 \
        pylint
