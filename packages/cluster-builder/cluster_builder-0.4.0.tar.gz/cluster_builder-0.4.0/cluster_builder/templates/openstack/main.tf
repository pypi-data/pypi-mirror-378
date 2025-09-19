# variables.tf
variable "cluster_name" {}
variable "resource_name" {}
variable "k3s_role" {}
variable "master_ip" {
  default = null
}
variable "volume_size" {}
variable "openstack_image_id" {}
variable "openstack_flavor_id" {}
variable "ssh_user" {}
variable "ssh_private_key_path" {}
variable "ssh_key_name" {}
variable "k3s_token" {}
variable "cloud" {}
variable "ha" {
  default = false
}

variable "floating_ip_pool" {}
variable "network_id" {}
variable "use_block_device" {
  default = false
}
variable "security_group_id" {
  default = ""
}
variable "tcp_ports" {
  default = []
}
variable "udp_ports" {
  default = []
}

# main.tf
# Block storage for each node role
resource "openstack_blockstorage_volume_v3" "root_volume" {
  count       = var.use_block_device ? 1 : 0  # Only create the volume if block device is required
  name        = "${var.cluster_name}-${var.resource_name}-volume"
  size        = var.volume_size
  image_id    = var.openstack_image_id
}

# Defining the port to use while instance creation
resource "openstack_networking_port_v2" "port_1" {
  network_id = var.network_id
}

# Security group rules
locals {
  ingress_rules = var.security_group_id == "" ? concat(
    [
    { from = 2379, to = 2380, proto = "tcp", desc = "etcd communication", roles = ["master", "ha"] },
    { from = 6443, to = 6443, proto = "tcp", desc = "K3s API server", roles = ["master", "ha", "worker"] },
    { from = 8472, to = 8472, proto = "udp", desc = "VXLAN for Flannel", roles = ["master", "ha", "worker"] },
    { from = 10250, to = 10250, proto = "tcp", desc = "Kubelet metrics", roles = ["master", "ha", "worker"] },
    { from = 51820, to = 51820, proto = "udp", desc = "Wireguard IPv4", roles = ["master", "ha", "worker"] },
    { from = 51821, to = 51821, proto = "udp", desc = "Wireguard IPv6", roles = ["master", "ha", "worker"] },
    { from = 5001, to = 5001, proto = "tcp", desc = "Embedded registry", roles = ["master", "ha"] },
    { from = 22, to = 22, proto = "tcp", desc = "SSH access", roles = ["master", "ha", "worker"] },
    { from = 80, to = 80, proto = "tcp", desc = "HTTP access", roles = ["master", "ha", "worker"] },
    { from = 443, to = 443, proto = "tcp", desc = "HTTPS access", roles = ["master", "ha", "worker"] },
    { from = 53, to = 53, proto = "udp", desc = "DNS for CoreDNS", roles = ["master", "ha", "worker"] },
    { from = 5432, to = 5432, proto = "tcp", desc = "PostgreSQL access", roles = ["master"] }
  ],
    [
      for port in var.tcp_ports : {
        from = port, to = port, proto = "tcp", desc = "Custom TCP rule for port ${port}", roles = ["master", "ha", "worker"]
      }
    ],
    [
      for port in var.udp_ports : {
        from = port, to = port, proto = "udp", desc = "Custom UDP rule for port ${port}", roles = ["master", "ha", "worker"]
      }
    ]
  ) : []
}

# Security Group Resource
resource "openstack_networking_secgroup_v2" "k3s_sg" {
  count       = var.security_group_id == "" ? 1 : 0  # Only create if no SG ID is provided
  name        = "${var.cluster_name}-${var.resource_name}-sg"
  description = "Security group for ${var.k3s_role} in cluster ${var.cluster_name}"
}

# Security Group Rule Resource
resource "openstack_networking_secgroup_rule_v2" "k3s_sg_rules" {
  # Only create rules if the security group is created (not passed)
  for_each = var.security_group_id == "" ? {
    for idx, rule in local.ingress_rules : 
    "${rule.from}-${rule.to}-${rule.proto}-${rule.desc}" => rule
  } : {}

  security_group_id = openstack_networking_secgroup_v2.k3s_sg[0].id  # Use index 0 since only 1 security group is created when count > 0
  direction         = "ingress"
  ethertype         = "IPv4"
  port_range_min    = each.value.from
  port_range_max    = each.value.to
  protocol          = each.value.proto
  remote_ip_prefix  = "0.0.0.0/0"
  description       = each.value.desc
}


resource "openstack_networking_port_secgroup_associate_v2" "port_2" {
  port_id = openstack_networking_port_v2.port_1.id
  enforce = true
  # Use the provided security group ID if available, otherwise use the generated security group
  security_group_ids = var.security_group_id != "" ? [var.security_group_id] : [openstack_networking_secgroup_v2.k3s_sg[0].id]
}

# Compute instance for each role
resource "openstack_compute_instance_v2" "k3s_node" {
  depends_on = [openstack_networking_port_v2.port_1] 

  name             = "${var.resource_name}"
  flavor_name      = var.openstack_flavor_id
  key_pair         = var.ssh_key_name
 # Only add the image_id if block device is NOT used
  image_id = var.use_block_device ? null : var.openstack_image_id

  # Conditional block_device for boot volume
  dynamic "block_device" {
    for_each = var.use_block_device ? [1] : []  # Include block_device only if use_block_device is true
    content {
      uuid                  = openstack_blockstorage_volume_v3.root_volume[0].id
      source_type           = "volume"
      destination_type      = "volume"
      boot_index            = 0
      delete_on_termination = true
    }
  }

  network {
    port = openstack_networking_port_v2.port_1.id
  }

  tags = [
    "${var.resource_name}",
    "ClusterName=${var.cluster_name}",
    "Role=${var.k3s_role}"
  ]
}

resource "openstack_networking_floatingip_v2" "floatip_1" {
  pool = var.floating_ip_pool
}

resource "openstack_networking_floatingip_associate_v2" "fip_association" {
  floating_ip = openstack_networking_floatingip_v2.floatip_1.address
  port_id     = openstack_networking_port_v2.port_1.id

  depends_on = [
    openstack_compute_instance_v2.k3s_node  # Ensure the instance is created first
  ]
}

# Provisioning via SSH
resource "null_resource" "k3s_provision" {
  depends_on = [openstack_networking_floatingip_v2.floatip_1]

  provisioner "file" {
    content = templatefile("${path.module}/${var.k3s_role}_user_data.sh.tpl", {
      ha           = var.ha,
      k3s_token    = var.k3s_token,
      master_ip    = var.master_ip,
      cluster_name = var.cluster_name,
      public_ip    = openstack_networking_floatingip_v2.floatip_1.address,
      resource_name    = "${var.resource_name}"
    })
    destination = "/tmp/k3s_user_data.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "rm -f ~/.ssh/known_hosts",
      "echo 'Executing remote provisioning script on ${var.k3s_role} node'",
      "chmod +x /tmp/k3s_user_data.sh",
      "sudo /tmp/k3s_user_data.sh"
    ]
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
    host        = openstack_networking_floatingip_v2.floatip_1.address
  }
}

# outputs.tf
output "cluster_name" {
  value = var.cluster_name
}

output "master_ip" {
  value = var.k3s_role == "master" ? openstack_networking_floatingip_v2.floatip_1.address : var.master_ip
}

output "worker_ip" {
  value = var.k3s_role == "worker" ? openstack_networking_floatingip_v2.floatip_1.address : null
}

output "ha_ip" {
  value = var.k3s_role == "ha" ? openstack_networking_floatingip_v2.floatip_1.address : null
}

output "k3s_token" {
  value = var.k3s_token
}

output "instance_power_state" {
  value = openstack_compute_instance_v2.k3s_node.power_state
}

output "resource_name" {
  value = openstack_compute_instance_v2.k3s_node.name
}