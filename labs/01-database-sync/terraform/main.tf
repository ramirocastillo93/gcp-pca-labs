# Enabling GCP APIs so we can use it on the project.
# These are the APIs the project lab needs to run.
# They will be disabled after we run `terraform destroy`.
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "iam.googleapis.com",
    "sqladmin.googleapis.com",
    "servicenetworking.googleapis.com",
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = true
}

# VPC.
resource "google_compute_network" "lab" {
  name                    = "pca-sync-lab-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}

# Subnetwork for the VM.
resource "google_compute_subnetwork" "vm" {
  name          = "pca-sync-lab-subnet"
  ip_cidr_range = "10.50.0.0/24"
  region        = var.region
  network       = google_compute_network.lab.id
}

# Private IP range reservation
resource "google_compute_global_address" "sql_peering" {
  name          = "pca-sync-sql-peering"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  address       = "10.240.0.0"
  prefix_length = 16
  network       = google_compute_network.lab.id
}

# VPC Peering for Google's own network (Cloud SQL) -> VPC (GCE instance)
resource "google_service_networking_connection" "sql" {
  network                 = google_compute_network.lab.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.sql_peering.name]
  depends_on              = [google_project_service.apis]
}

# Cloud SQL instance.
resource "google_sql_database_instance" "new" {
  name             = "pca-sync-new"
  region           = var.region
  database_version = "POSTGRES_18"

  # Disposable lab only. Require a separately reviewed destroy plan.
  deletion_protection = false

  settings {
    edition           = "ENTERPRISE"
    tier              = "db-f1-micro"
    disk_size         = 10
    disk_autoresize   = false
    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.lab.id
    }

    database_flags {
      name  = "cloudsql.logical_decoding"
      value = "on"
    }
  }

  depends_on = [google_service_networking_connection.sql]
}

# Database on Cloud SQL instance
resource "google_sql_database" "lab" {
  name     = "lab"
  instance = google_sql_database_instance.new.name
}


# Creation of service account.
# This SA is going to be used on the GCE instance.
resource "google_service_account" "vm" {
  account_id   = "pca-sync-lab-vm"
  display_name = "PCA sync lab VM"
}

# Firewall rule for Identity-Aware Proxy to connect through SSH.
# The only resource with tag `pca-sync-vm` is the GCE with the "legacy" database.
resource "google_compute_firewall" "ssh_iap" {
  name          = "pca-sync-iap-ssh"
  network       = google_compute_network.lab.name
  source_ranges = ["35.235.240.0/20"]
  target_tags   = ["pca-sync-vm"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

# Firewall rule for the GCE instance to open TCP inbound connections on port `5432` for postgres and `5433` for Cloud SQL
# from three private sources listed on `source_ranges`.
resource "google_compute_firewall" "postgres_private" {
  name          = "pca-sync-private-postgres"
  network       = google_compute_network.lab.name
  source_ranges = ["10.50.0.0/24", "10.240.0.0/16", "10.60.0.0/29"]
  target_tags   = ["pca-sync-vm"]

  allow {
    protocol = "tcp"
    ports    = ["5432", "5433"]
  }
}

# GCE with "legacy" DB
resource "google_compute_instance" "legacy" {
  name         = "pca-sync-legacy"
  machine_type = "e2-micro"
  zone         = var.zone
  tags         = ["pca-sync-vm"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 10
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.vm.id
    network_ip = "10.50.0.10"
    # Outbound access for Debian packages; no public database or SSH ingress.
    access_config {}
  }

  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = templatefile("${path.module}/startup.sh.tftpl", {
    cloud_sql_ip = google_sql_database_instance.new.private_ip_address
  })

  service_account {
    email  = google_service_account.vm.email
    scopes = ["logging-write"]
  }

  depends_on = [google_project_service.apis]
}
