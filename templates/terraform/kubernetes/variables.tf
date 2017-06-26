variable "subscription_id" {}
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}

variable "azure_region" {}

variable "azure_resource_group" {}
variable "azure_vnet_name" {}

variable "cluster_name" {}
variable "azure_admin_username" {}
variable "azure_admin_password" {}
variable "ssh_pub_key" {}

variable "azure_vnet_address_space" {
    description = "Address space to use"
    default = "10.145.0.0/16"
}

variable "azure_vnet_subnets" {
    description = "Subnets within the Vnet"
    default = {
        "WebSN" = "10.145.0.0/20"
        "BackendSN" = "10.145.16.0/20"
        "DatastoreSN" = "10.145.32.0/20"
    }
}

variable "default_image" {
    description = "AMI Information"
    default = {
        publisher   = "credativ"
        offer       = "Debian"
        sku         = "9"
        version     = "latest"
    }
}

variable "agents_count" {
    default = 3
}

variable "masters_count" {
    default = 3
}

variable "agents_avail_set" {
    default = "ku8ie-agents"
}

variable "masters_avail_set" {
    default = "ku8ie-masters"
}
