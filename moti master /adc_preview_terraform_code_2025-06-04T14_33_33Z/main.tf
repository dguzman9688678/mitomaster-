
# This file is autogenerated. Do not edit this file directly.
# Please make changes to the application template instead.

module "agent-frontend" {
  source                        = "github.com/GoogleCloudPlatform/terraform-google-cloud-run//modules/v2?ref=v0.17.4"
  project_id                    = var.agent-frontend_project_id
  location                      = var.agent-frontend_location
  service_name                  = var.agent-frontend_service_name
  containers                    = [{"container_image" = "us-docker.pkg.dev/cloudrun/container/hello", "container_name" = "service-container", "env_vars" = {"agent_backend_SERVICE_ENDPOINT" = module.agent-backend.service_uri}}]
  service_account_project_roles = ["roles/run.invoker"]
  vpc_access = {
    egress = "ALL_TRAFFIC"
    network_interfaces = {
      network    = "default"
      subnetwork = "default"
    }
  }
  cloud_run_deletion_protection = false
  enable_prometheus_sidecar     = true
}
module "agent-backend" {
  source                        = "github.com/GoogleCloudPlatform/terraform-google-cloud-run//modules/v2?ref=v0.17.4"
  project_id                    = "avid-day-459521-r4"
  location                      = "us-west2"
  service_name                  = "agent-backend"
  containers                    = [{"container_image" = "us-docker.pkg.dev/cloudrun/container/hello", "container_name" = "service-container", "env_secret_vars" = {"agent_secrets_SECRET" = module.agent-secrets.env_vars.SECRET}, "env_vars" = {"agent_database_CLOUD_SQL_DATABASE_CONNECTION_NAME" = module.agent-database.instance_connection_name, "agent_database_CLOUD_SQL_DATABASE_HOST" = module.agent-database.instance_first_ip_address, "agent_database_CLOUD_SQL_DATABASE_NAME" = module.agent-database.env_vars.CLOUD_SQL_DATABASE_NAME}}]
  service_account_project_roles = concat(["roles/cloudsql.instanceUser", "roles/cloudsql.client"], ["roles/secretmanager.secretAccessor"])
  vpc_access = {
    egress = "ALL_TRAFFIC"
    network_interfaces = {
      network    = "default"
      subnetwork = "default"
    }
  }
  cloud_run_deletion_protection = false
  enable_prometheus_sidecar     = true
  depends_on                    = [module.project-services-avid-day-459521-r4, module.project-services-billing-project]
}
module "agent-database" {
  source                      = "github.com/terraform-google-modules/terraform-google-sql-db//modules/postgresql?ref=v25.2.2"
  project_id                  = "avid-day-459521-r4"
  name                        = "agent-database"
  edition                     = "ENTERPRISE_PLUS"
  database_version            = "POSTGRES_15"
  availability_type           = "REGIONAL"
  deletion_protection         = false
  database_flags              = [{"name" = "cloudsql.iam_authentication", "value" = "on"}]
  data_cache_enabled          = true
  tier                        = "db-perf-optimized-N-8"
  deletion_protection_enabled = false
  disk_autoresize             = true
  backup_configuration = {
    enabled                        = true
    point_in_time_recovery_enabled = true
  }
  iam_users = [{
    email = module.agent-backend.service_account_id.email
    id    = module.agent-backend.service_account_id.id
    type  = "CLOUD_IAM_SERVICE_ACCOUNT"
  }]
  depends_on = [module.project-services-avid-day-459521-r4, module.project-services-billing-project]
}
module "agent-secrets" {
  source      = "github.com/GoogleCloudPlatform/terraform-google-secret-manager//modules/simple-secret?ref=v0.8.0"
  project_id  = "avid-day-459521-r4"
  name        = "agent-secrets"
  secret_data = "Please provide the secret data here"
  depends_on  = [module.project-services-avid-day-459521-r4, module.project-services-billing-project]
}
module "apphub" {
  source         = "github.com/GoogleCloudPlatform/terraform-google-apphub?ref=v0.3.0"
  project_id     = var.apphub_project_id
  location       = var.apphub_location
  service_uris   = concat([module.agent-frontend.apphub_service_uri], [module.agent-backend.apphub_service_uri], [module.agent-database.apphub_service_uri])
  application_id = var.apphub_application_id
}
module "project-services-avid-day-459521-r4" {
  source                      = "github.com/terraform-google-modules/terraform-google-project-factory//modules/project_services?ref=v17.1.0"
  project_id                  = "avid-day-459521-r4"
  disable_services_on_destroy = false
  activate_apis               = []
}
module "project-services-billing-project" {
  source                      = "github.com/terraform-google-modules/terraform-google-project-factory//modules/project_services?ref=v17.1.0"
  project_id                  = "avid-day-459521-r4"
  disable_services_on_destroy = false
  activate_apis               = ["apphub.googleapis.com", "cloudresourcemanager.googleapis.com"]
}
