resource "google_compute_instance" "mysql_instance" {
  name         = "mysql-server"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Ephemeral public IP
    }
  }

  metadata_startup_script = "apt-get update && apt-get install -y mariadb-server && sed -i 's/127.0.0.1/0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf && systemctl restart mariadb && mysql -e \"CREATE DATABASE IF NOT EXISTS tensrgrid; CREATE USER IF NOT EXISTS 'tensr_user'@'%' IDENTIFIED BY '72zwbn&@ZWBN'; GRANT ALL PRIVILEGES ON tensrgrid.* TO 'tensr_user'@'%'; FLUSH PRIVILEGES;\""

  tags = ["mysql-server"]
}

resource "google_compute_firewall" "allow_mysql" {
  name    = "allow-mysql-traffic"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["3306"]
  }

  source_ranges = ["0.0.0.0/0"] # Allow from all public IPs as requested
  target_tags   = ["mysql-server"]
}

output "instance_public_ip" {
  value = google_compute_instance.mysql_instance.network_interface[0].access_config[0].nat_ip
}
