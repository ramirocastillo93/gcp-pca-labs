output "vm_private_ip" {
  value = google_compute_instance.legacy.network_interface[0].network_ip
}

output "vm_public_ip" {
  value = google_compute_instance.legacy.network_interface[0].access_config[0].nat_ip
}

output "cloud_sql_private_ip" {
  value = google_sql_database_instance.new.private_ip_address
}

output "vpc_id" {
  value = google_compute_network.lab.id
}

output "cloud_sql_instance" {
  value = google_sql_database_instance.new.connection_name
}
