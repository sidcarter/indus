#let's create the default availability sets
resource "azurerm_availability_set" "masters_avail_set" {
    name = "${var.masters_avail_set}"
    location = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"

    tags {
        environment = "${var.azure_resource_group}"
    }
}

resource "azurerm_network_interface" "master_nic" {
    count = "${var.masters_count}"
    name = "master-${count.index + 1}-nic"
    location = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"

    ip_configuration {
        name = "master-${count.index + 1}-nic-config"
        subnet_id = "${azurerm_subnet.backend.id}"
        private_ip_address_allocation = "dynamic"
        load_balancer_backend_address_pools_ids = ["${azurerm_lb_backend_address_pool.master_bep.id}"]
        load_balancer_inbound_nat_rules_ids = ["${azurerm_lb_nat_rule.master_nat_rule.id}"]
    }
}

resource "azurerm_managed_disk" "master_data_disk" {
    count = "${var.masters_count}"
    name = "master-${count.index + 1}-datadisk"
    location = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"
    storage_account_type = "Standard_LRS"
    create_option = "Empty"
    disk_size_gb = "511"
}

resource "azurerm_virtual_machine" "master" {
    count = "${var.masters_count}"
    name = "${var.cluster_name}-master-${count.index + 1}"
    location = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"
    network_interface_ids = ["${element(azurerm_network_interface.master_nic.*.id, count.index)}"]
    vm_size               = "Standard_A3"

    storage_image_reference {
        publisher = "${var.default_image["publisher"]}"
        offer = "${var.default_image["offer"]}"
        sku = "${var.default_image["sku"]}"
        version = "${var.default_image["version"]}"
    }

    storage_os_disk {
        name              = "master-${count.index + 1}-osdisk"
        caching           = "ReadWrite"
        create_option     = "FromImage"
        managed_disk_type = "Standard_LRS"
    }

    storage_data_disk {
        name            = "${element(azurerm_managed_disk.master_data_disk.*.name, count.index)}"
        managed_disk_id = "${element(azurerm_managed_disk.master_data_disk.*.id, count.index)}"
        create_option   = "Attach"
        lun             = 1
        disk_size_gb    = "${element(azurerm_managed_disk.master_data_disk.*.disk_size_gb, count.index)}"
    }

    os_profile {
        computer_name  = "${var.cluster_name}-master-${count.index + 1}"
        admin_username = "${var.azure_admin_username}"
        admin_password = "${var.azure_admin_password}"
    }

    os_profile_linux_config {
        disable_password_authentication = false
        ssh_keys {
            path = "/home/${var.azure_admin_username}/.ssh/authorized_keys"
            key_data = "${var.ssh_pub_key}"
        }
    }

    tags {
        orchestrator = "kubernetes"
        environment = "staging"
        type = "master"
    }
}