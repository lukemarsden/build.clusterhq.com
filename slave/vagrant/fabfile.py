# Copyright Hybrid Logic Ltd.
"""
Configuration for a buildslave to run vagrant on.

.. warning::
    This points at the labs buildserver by default.
"""

from fabric.api import task, sudo, put, env
from twisted.python.filepath import FilePath
from StringIO import StringIO
import yaml

env.user = "root"
# https://github.com/fabric/fabric/issues/60
env.shell = "/bin/bash -c"


def configure_acceptance():
    put(StringIO(yaml.safe_dump({'metadata': {'creator': 'buildbot'}})),
        '/home/buildslave/acceptance.yml')


@task
def install(index, password, master='build.labs.clusterhq.com'):
    """
    Install a buildslave with vagrant installed.
    """
    sudo("apt-get install -y virtualbox virtualbox-dkms buildbot-slave mongodb libffi-dev python-dev python-virtualenv linux-headers-generic linux-headers-`uname -r` libssl-dev")
    sudo("dpkg-reconfigure virtualbox-dkms")
    sudo("if [ ! -e vagrant_1.7.2_x86_64.deb ]; then wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.2_x86_64.deb && dpkg -i vagrant_1.7.2_x86_64.deb; fi")
    sudo("useradd buildslave || true")

    # docker is used to build docker in docker by some buildslaves
    sudo('wget -qO- https://get.docker.com/ | sh')
    sudo("adduser buildslave docker")

    sudo("mkdir -p /home/buildslave/.ssh", user='buildslave')
    sudo("touch /home/buildslave/.ssh/known_hosts", user='buildslave')
    sudo("if [ ! -e /home/buildslave/.ssh/id_rsa_flocker ]; then ssh-keygen -N '' -f /home/buildslave/.ssh/id_rsa_flocker; fi", user='buildslave')

    # do the same as root because hacks
    sudo("mkdir -p /root/.ssh")
    sudo("touch /root/.ssh/known_hosts")
    sudo("cp -a /home/buildslave/.ssh/id_rsa_flocker{,.pub} /root/.ssh/")
    sudo("chown root /root/.ssh/id_rsa_flocker{,.pub}")

    sudo("mkdir -p /home/buildslave/fedora-vagrant")
    sudo("chown -R buildslave /home/buildslave")

    sudo("buildslave create-slave /home/buildslave/fedora-vagrant %(master)s fedora-vagrant-%(index)s %(password)s"
         % {'index': index, 'password': password, 'master': master},
         user='buildslave')
    put(FilePath(__file__).sibling('start').path,
        '/home/buildslave/fedora-vagrant/start', mode=0755)

    sudo("vagrant plugin install vagrant-reload vagrant-vbguest")
    configure_acceptance()

    put(FilePath(__file__).sibling('vagrant-slave.conf').path,
        '/etc/init/vagrant-slave.conf')

    sudo('start vagrant-slave')
