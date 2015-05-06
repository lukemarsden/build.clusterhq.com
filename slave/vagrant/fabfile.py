# Copyright Hybrid Logic Ltd.
"""
Configuration for a buildslave to run vagrant on.

.. warning::
    This points at the labs buildserver by default.
"""

from fabric.api import run, task, sudo, put, env
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
    run("apt-get install -y virtualbox virtualbox-dkms buildbot-slave mongodb libffi-dev python-dev python-virtualenv linux-headers-generic linux-headers-`uname -r`")
    run("dpkg-reconfigure virtualbox-dkms")
    run("if [ ! -e vagrant_1.7.2_x86_64.deb ]; then wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.2_x86_64.deb && dpkg -i vagrant_1.7.2_x86_64.deb; fi")
    run("useradd buildslave || true")
    run("mkdir -p /home/buildslave/fedora-vagrant")
    run("chown -R buildslave /home/buildslave")

    sudo("buildslave create-slave /home/buildslave/fedora-vagrant %(master)s fedora-vagrant-%(index)s %(password)s"
         % {'index': index, 'password': password, 'master': master},
         user='buildslave')
    put(FilePath(__file__).sibling('start').path,
        '/home/buildslave/fedora-vagrant/start', mode=0755)

    sudo("vagrant plugin install vagrant-reload vagrant-vbguest")
    configure_acceptance()

    put(FilePath(__file__).sibling('vagrant-slave.conf').path,
        '/etc/init/vagrant-slave.conf')

    run('start vagrant-slave')
