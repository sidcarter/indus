#let's create the default availability sets
resource "azurerm_availability_set" "agents_avail_set" {
    name                = "${var.agents_avail_set}"
    location            = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"

    tags {
        environment = "${var.azure_resource_group}"
    }
}

resource "azurerm_network_interface" "agent_nic" {
    count               = "${var.agents_count}"
    name                = "agent-${count.index + 1}-nic"
    location            = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"

    ip_configuration {
        name        = "agent-${count.index + 1}-nic-config"
        subnet_id   = "${azurerm_subnet.backend.id}"
        private_ip_address_allocation = "dynamic"
    }
}

resource "azurerm_managed_disk" "agent_data_disk" {
    count       = "${var.agents_count}"
    name        = "agent-${count.index + 1}-datadisk"
    location    = "${var.azure_region}"
    resource_group_name     = "${azurerm_resource_group.rg.name}"
    storage_account_type    = "Premium_LRS"
    create_option           = "Empty"
    disk_size_gb            = "511"
}

resource "azurerm_virtual_machine" "agent" {
    count                   = "${var.agents_count}"
    name                    = "${var.cluster_name}-agent-${count.index + 1}"
    location                = "${var.azure_region}"
    resource_group_name     = "${azurerm_resource_group.rg.name}"
    availability_set_id     = "${azurerm_availability_set.agents_avail_set.id}"
    network_interface_ids = ["${element(azurerm_network_interface.agent_nic.*.id, count.index)}"]
    vm_size = "Standard_DS12_v2"

    storage_image_reference {
        publisher   = "${var.default_image["publisher"]}"
        offer       = "${var.default_image["offer"]}"
        sku         = "${var.default_image["sku"]}"
        version     = "${var.default_image["version"]}"
    }

    storage_os_disk {
        name              = "agent-${count.index + 1}-osdisk"
        caching           = "ReadWrite"
        create_option     = "FromImage"
        managed_disk_type = "Premium_LRS"
    }

    storage_data_disk {
        name            = "${element(azurerm_managed_disk.agent_data_disk.*.name, count.index)}"
        managed_disk_id = "${element(azurerm_managed_disk.agent_data_disk.*.id, count.index)}"
        create_option   = "Attach"
        lun             = 1
        disk_size_gb    = "${element(azurerm_managed_disk.agent_data_disk.*.disk_size_gb, count.index)}"
    }

    os_profile {
        computer_name  = "${var.cluster_name}-agent-${count.index + 1}"
        admin_username = "${var.azure_admin_username}"
        admin_password = "${var.azure_admin_password}"
    }

    os_profile_linux_config {
        disable_password_authentication = false
        ssh_keys {
            path        = "/home/${var.azure_admin_username}/.ssh/authorized_keys"
            key_data    = "${var.ssh_pub_key}"
        }
    }

    tags {
        orchestrator = "kubernetes"
        environment = "dev"
        type = "agent"
    }
}