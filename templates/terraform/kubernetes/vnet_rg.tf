# Configure the Microsoft Azure Provider
provider "azurerm" {
  subscription_id = "${var.subscription_id}"
  client_id       = "${var.client_id}"
  client_secret   = "${var.client_secret}"
  tenant_id       = "${var.tenant_id}"
}

# Create a resource group
resource "azurerm_resource_group" "rg" {
  name     = "${var.azure_resource_group}"
  location = "East US 2"
}

resource "azurerm_virtual_network" "vnet" {
  name                = "${var.azure_vnet_name}"
  address_space       = ["10.145.0.0/16"]
  location            = "East US 2"
  resource_group_name = "${azurerm_resource_group.rg.name}"
}

resource "azurerm_subnet" "backend" {
    name                 = "backend_subnet"
    resource_group_name  = "${azurerm_resource_group.rg.name}"
    virtual_network_name = "${azurerm_virtual_network.vnet.name}"
    address_prefix       = "10.145.0.0/20"
    network_security_group_id = "${azurerm_network_security_group.primary_nsg.id}"
}

# Create security groups
resource "azurerm_network_security_group" "primary_nsg" {
    name = "primary_nsg"
    location = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"

    security_rule {
        name = "allow_inbound_ssh"
        priority = 100
        direction = "Inbound"
        access = "Allow"
        protocol = "Tcp"
        source_port_range = "*"
        destination_port_range = "22"
        source_address_prefix = "*"
        destination_address_prefix = "*"
    }

    security_rule {
        name = "allow_http_outbound"
        priority = 110
        direction = "Outbound"
        access = "Allow"
        protocol = "Tcp"
        source_port_range = "*"
        destination_port_range = "80"
        source_address_prefix = "*"
        destination_address_prefix = "*"
    }

    security_rule {
        name = "allow_https_outbound"
        priority = 120
        direction = "Outbound"
        access = "Allow"
        protocol = "Tcp"
        source_port_range = "*"
        destination_port_range = "443"
        source_address_prefix = "*"
        destination_address_prefix = "*"
    }
}
