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


def configure_acceptance():
    put(StringIO(yaml.safe_dump({'metadata': {'creator': 'buildbot'}})),
        '/home/buildslave/acceptance.yml')


@task
def install(index, password, master='build.labs.clusterhq.com'):
    """
    Install a buildslave with vagrant installed.
    """
    run("apt-get install -y virtualbox virtualbox-dkms buildbot-slave")
    run("wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.2_x86_64.deb && dpkg -i vagrant_1.7.2_x86_64.deb")
    run("useradd buildslave || true")
    sudo("buildslave create-slave /home/buildslave/fedora-vagrant %(master)s fedora-vagrant-%(index)s %(password)s"
         % {'index': index, 'password': password, 'master': master},
         user='buildslave')
    put(FilePath(__file__).sibling('start').path,
        '/home/buildslave/fedora-vagrant/start', mode=0755)

    sudo("vagrant plugin install vagrant-reload vagrant-vbguest",
         user='buildslave')
    configure_acceptance()

    put(FilePath(__file__).sibling('vagrant-slave.conf').path,
        '/etc/init/vagrant-slave.conf')

    run('start vagrant-slave')
