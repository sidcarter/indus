# configuring the load balancer to get the masters

resource "azurerm_public_ip" "master_lb_publicip" {
    name                = "${var.cluster_name}-masters-pip"
    location            = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"
    public_ip_address_allocation = "static"
}

resource "azurerm_lb" "master_lb" {
    name                = "${var.cluster_name}-masters-lb"
    location            = "${var.azure_region}"
    resource_group_name = "${azurerm_resource_group.rg.name}"

    frontend_ip_configuration {
        name                 = "${var.cluster_name}-masters-feip"
        public_ip_address_id = "${azurerm_public_ip.master_lb_publicip.id}"
    }
}

resource "azurerm_lb_backend_address_pool" "master_bep" {
    resource_group_name = "${azurerm_resource_group.rg.name}"
    loadbalancer_id     = "${azurerm_lb.master_lb.id}"
    name                = "${var.cluster_name}-masters-lb-bep"
}

resource "azurerm_lb_nat_rule" "master_nat_rule" {
  resource_group_name            = "${azurerm_resource_group.rg.name}"
  loadbalancer_id                = "${azurerm_lb.master_lb.id}"
  name                           = "SSH Access"
  protocol                       = "Tcp"
  frontend_port                  = 5422
  backend_port                   = 22
  frontend_ip_configuration_name = "${var.cluster_name}-masters-feip"
}