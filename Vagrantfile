# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  config.vm.box = "afarshad/qoem-mininet"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "watchtower"
    vb.cpus = 2
    vb.memory = 1024
  end

  # Expose guest API port (default 8080) to host port 80
  config.vm.network "forwarded_port", guest: 8080, host: 80

  config.push.define "atlas" do |push|
    push.app = "afarshad/qoem-mininet"
  end

  config.sshd.forward_agent = true
  config.ssh.forward_x11 = true
  config.ssh.user = "vagrant"
  config.ssh.password = "vagrant"

end
