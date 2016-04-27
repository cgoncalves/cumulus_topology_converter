# Created by Topology-Converter v4.0.3
#    using topology data from: visa-ovn.dot
#    NOTE: in order to use this Vagrantfile you will need:
#       -Vagrant(v1.7+) installed: http://www.vagrantup.com/downloads 
#       -Cumulus Plugin for Vagrant installed: $ vagrant plugin install vagrant-cumulus
#       -the "helper_scripts" directory that comes packaged with topology-converter.py 
#       -Virtualbox installed: https://www.virtualbox.org/wiki/Downloads

raise "vagrant-cumulus plugin must be installed, try $ vagrant plugin install vagrant-cumulus" unless Vagrant.has_plugin? "vagrant-cumulus"

Vagrant.configure("2") do |config|
  wbid = 1461787006

  config.vm.provider "virtualbox" do |v|
    v.gui=false

  end

  #Generating Ansible Host File at following location:
  #    ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "./helper_scripts/empty_playbook.yml"
  end


  ##### DEFINE VM for oob-mgmt-server #####
  config.vm.define "oob-mgmt-server" do |device|
    device.vm.hostname = "oob-mgmt-server"
    device.vm.box = "centos/7"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_oob-mgmt-server"
      v.memory = 400
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for eth1 --> oob-mgmt-switch:swp20
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net21", auto_config: false , :mac => "443839000021"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_server_config.sh"



      # Apply the interface re-map

      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000021 eth1"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for oob-mgmt-switch #####
  config.vm.define "oob-mgmt-switch" do |device|
    device.vm.hostname = "oob-mgmt-switch"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_oob-mgmt-switch"
      v.memory = 200
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp20 --> oob-mgmt-server:eth1
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net21", auto_config: false , :mac => "443839000022"
      
      # link for swp10 --> ovn-border-leaf1:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net2", auto_config: false , :mac => "443839000002"
      
      # link for swp11 --> ovn-border-leaf2:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net1", auto_config: false , :mac => "443839000001"
      
      # link for swp8 --> ovn-spine2:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net9", auto_config: false , :mac => "44383900000E"
      
      # link for swp2 --> ovn-node-1.1:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net27", auto_config: false , :mac => "44383900002C"
      
      # link for swp3 --> server1:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net13", auto_config: false , :mac => "443839000015"
      
      # link for swp1 --> ovn-orange-1:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net14", auto_config: false , :mac => "443839000016"
      
      # link for swp6 --> ovn-leaf3:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net4", auto_config: false , :mac => "443839000005"
      
      # link for swp7 --> ovn-spine1:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net17", auto_config: false , :mac => "44383900001A"
      
      # link for swp4 --> ovn-leaf1:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net15", auto_config: false , :mac => "443839000017"
      
      # link for swp5 --> ovn-leaf2:eth0
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net22", auto_config: false , :mac => "443839000023"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc5', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc6', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc7', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc8', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc9', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc10', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc11', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc12', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype5", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype6", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype7", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype8", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype9", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype10", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype11", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype12", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000022 swp20"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000002 swp10"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000001 swp11"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900000E swp8"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900002C swp2"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000015 swp3"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000016 swp1"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000005 swp6"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900001A swp7"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000017 swp4"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000023 swp5"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-border-leaf1 #####
  config.vm.define "ovn-border-leaf1" do |device|
    device.vm.hostname = "ovn-border-leaf1"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-border-leaf1"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp50 --> ovn-spine2:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net7", auto_config: false , :mac => "44383900000A"
      
      # link for swp51 --> ovn-border-leaf2:swp51
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net11", auto_config: false , :mac => "443839000011"
      
      # link for swp52 --> ovn-border-leaf2:swp52
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net18", auto_config: false , :mac => "44383900001B"
      
      # link for swp49 --> ovn-spine1:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net10", auto_config: false , :mac => "44383900000F"
      
      # link for swp1 --> server1:enp0s1
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net5", auto_config: false , :mac => "443839000007"
      
      # link for eth0 --> oob-mgmt-switch:swp10
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net2", auto_config: false , :mac => "A00000000041"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc5', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc6', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc7', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype5", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype6", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype7", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900000A swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000011 swp51"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900001B swp52"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900000F swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000007 swp1"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000041 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-border-leaf2 #####
  config.vm.define "ovn-border-leaf2" do |device|
    device.vm.hostname = "ovn-border-leaf2"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-border-leaf2"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp50 --> ovn-spine1:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net24", auto_config: false , :mac => "443839000026"
      
      # link for swp51 --> ovn-border-leaf1:swp51
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net11", auto_config: false , :mac => "443839000012"
      
      # link for swp52 --> ovn-border-leaf1:swp52
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net18", auto_config: false , :mac => "44383900001C"
      
      # link for swp49 --> ovn-spine2:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net25", auto_config: false , :mac => "443839000028"
      
      # link for swp1 --> server1:enp0s2
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net6", auto_config: false , :mac => "443839000009"
      
      # link for eth0 --> oob-mgmt-switch:swp11
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net1", auto_config: false , :mac => "A00000000042"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc5', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc6', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc7', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype5", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype6", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype7", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000026 swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000012 swp51"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900001C swp52"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000028 swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000009 swp1"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000042 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-spine1 #####
  config.vm.define "ovn-spine1" do |device|
    device.vm.hostname = "ovn-spine1"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-spine1"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp50 --> ovn-border-leaf2:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net24", auto_config: false , :mac => "443839000027"
      
      # link for swp51 --> ovn-leaf1:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net16", auto_config: false , :mac => "443839000019"
      
      # link for swp52 --> ovn-leaf2:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net19", auto_config: false , :mac => "44383900001E"
      
      # link for swp53 --> ovn-leaf3:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net3", auto_config: false , :mac => "443839000004"
      
      # link for swp49 --> ovn-border-leaf1:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net10", auto_config: false , :mac => "443839000010"
      
      # link for eth0 --> oob-mgmt-switch:swp7
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net17", auto_config: false , :mac => "A00000000021"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc5', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc6', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc7', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype5", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype6", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype7", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000027 swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000019 swp51"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900001E swp52"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000004 swp53"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000010 swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000021 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-spine2 #####
  config.vm.define "ovn-spine2" do |device|
    device.vm.hostname = "ovn-spine2"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-spine2"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp50 --> ovn-border-leaf1:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net7", auto_config: false , :mac => "44383900000B"
      
      # link for swp51 --> ovn-leaf1:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net23", auto_config: false , :mac => "443839000025"
      
      # link for swp52 --> ovn-leaf2:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net8", auto_config: false , :mac => "44383900000D"
      
      # link for swp53 --> ovn-leaf3:swp50
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net12", auto_config: false , :mac => "443839000014"
      
      # link for swp49 --> ovn-border-leaf2:swp49
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net25", auto_config: false , :mac => "443839000029"
      
      # link for eth0 --> oob-mgmt-switch:swp8
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net9", auto_config: false , :mac => "A00000000022"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc5', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc6', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc7', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype5", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype6", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype7", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900000B swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000025 swp51"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900000D swp52"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000014 swp53"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000029 swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000022 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-leaf3 #####
  config.vm.define "ovn-leaf3" do |device|
    device.vm.hostname = "ovn-leaf3"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-leaf3"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp49 --> ovn-spine1:swp53
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net3", auto_config: false , :mac => "443839000003"
      
      # link for swp50 --> ovn-spine2:swp53
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net12", auto_config: false , :mac => "443839000013"
      
      # link for eth0 --> oob-mgmt-switch:swp6
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net4", auto_config: false , :mac => "A00000000013"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000003 swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000013 swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000013 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-leaf2 #####
  config.vm.define "ovn-leaf2" do |device|
    device.vm.hostname = "ovn-leaf2"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-leaf2"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp49 --> ovn-spine1:swp52
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net19", auto_config: false , :mac => "44383900001D"
      
      # link for swp50 --> ovn-spine2:swp52
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net8", auto_config: false , :mac => "44383900000C"
      
      # link for eth0 --> oob-mgmt-switch:swp5
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net22", auto_config: false , :mac => "A00000000012"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900001D swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900000C swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000012 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-leaf1 #####
  config.vm.define "ovn-leaf1" do |device|
    device.vm.hostname = "ovn-leaf1"
    device.vm.box = "CumulusCommunity/cumulus-vx"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-leaf1"
      v.memory = 300
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for swp2 --> ovn-node-1.1:enp0s8
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net20", auto_config: false , :mac => "443839000020"
      
      # link for swp49 --> ovn-spine1:swp51
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net16", auto_config: false , :mac => "443839000018"
      
      # link for swp1 --> ovn-orange-1:enp0s8
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net26", auto_config: false , :mac => "44383900002B"
      
      # link for swp50 --> ovn-spine2:swp51
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net23", auto_config: false , :mac => "443839000024"
      
      # link for eth0 --> oob-mgmt-switch:swp4
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net15", auto_config: false , :mac => "A00000000011"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc5', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc6', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype5", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype6", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_switch_config.sh"



      # Apply the interface re-map
        #Disable default remap on Cumulus VX 
      device.vm.provision :shell , inline: "mv /etc/init.d/rename_eth_swp /etc/init.d/rename_eth_swp.old"
      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000020 swp2"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000018 swp49"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900002B swp1"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000024 swp50"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000011 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-node-1.1 #####
  config.vm.define "ovn-node-1.1" do |device|
    device.vm.hostname = "ovn-node-1.1"
    device.vm.box = "centos/7"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-node-1.1"
      v.memory = 512
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for enp0s8 --> ovn-leaf1:swp2
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net20", auto_config: false , :mac => "44383900001F"
      
      # link for eth0 --> oob-mgmt-switch:swp2
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net27", auto_config: false , :mac => "A00000000032"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_server_config.sh"



      # Apply the interface re-map

      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900001F enp0s8"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000032 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for ovn-orange-1 #####
  config.vm.define "ovn-orange-1" do |device|
    device.vm.hostname = "ovn-orange-1"
    device.vm.box = "centos/7"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_ovn-orange-1"
      v.memory = 512
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for enp0s8 --> ovn-leaf1:swp1
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net26", auto_config: false , :mac => "44383900002A"
      
      # link for eth0 --> oob-mgmt-switch:swp1
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net14", auto_config: false , :mac => "A00000000031"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_server_config.sh"



      # Apply the interface re-map

      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 44383900002A enp0s8"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000031 eth0"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end

  ##### DEFINE VM for server1 #####
  config.vm.define "server1" do |device|
    device.vm.hostname = "server1"
    device.vm.box = "centos/7"
    device.vm.provider "virtualbox" do |v|
      v.name = "1461787006_server1"
      v.memory = 512
    end
  config.vm.synced_folder ".", "/vagrant", disabled: true

      # link for eth0 --> oob-mgmt-switch:swp3
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net13", auto_config: false , :mac => "A00000000033"
      
      # link for enp0s2 --> ovn-border-leaf2:swp1
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net6", auto_config: false , :mac => "443839000008"
      
      # link for enp0s1 --> ovn-border-leaf1:swp1
      device.vm.network "private_network", virtualbox__intnet: "{wbid}_net5", auto_config: false , :mac => "443839000006"
      

    device.vm.provider "virtualbox" do |vbox|
      vbox.customize ['modifyvm', :id, '--nicpromisc2', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc3', 'allow-vms']
      vbox.customize ['modifyvm', :id, '--nicpromisc4', 'allow-vms']

      vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype3", "virtio"]
      vbox.customize ["modifyvm", :id, "--nictype4", "virtio"]

    end

      # Run Any Extra Config
      device.vm.provision :shell , path: "./helper_scripts/extra_server_config.sh"



      # Apply the interface re-map

      device.vm.provision "file", source: "./helper_scripts/apply_udev.py", destination: "/home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "chmod 755 /home/vagrant/apply_udev.py"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a A00000000033 eth0"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000008 enp0s2"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -a 443839000006 enp0s1"

      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -vm"
      device.vm.provision :shell , inline: "/home/vagrant/apply_udev.py -s"
      device.vm.provision :shell , inline: "reboot"




  end



end