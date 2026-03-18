terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "npipe:////./pipe/docker_engine"
}

locals {
  # Lendo o .env e limpando aspas e caracteres de Windows (\r) apenas para o Terraform
  env_raw   = file("${path.module}/../config/.env")
  env_clean = replace(replace(replace(local.env_raw, "\r", ""), "\"", ""), "'", "")
  
  # Criando o mapa de variáveis ignorando espaços em branco
  envs = { for line in split("\n", local.env_clean) : 
            trimspace(split("=", line)[0]) => trimspace(split("=", line)[1]) 
            if length(split("=", line)) == 2 
         }
}

resource "docker_network" "weather_net" {
  name = "weather_network"
}

# 1. BANCO DE DADOS (Postgres 18)
resource "docker_container" "postgres_db" {
  name  = "weather_postgres"
  image = "postgres:18"
  
  networks_advanced {
    name = docker_network.weather_net.name
  }
  
  env = [
    "POSTGRES_USER=${local.envs["user"]}",
    "POSTGRES_PASSWORD=${local.envs["password"]}",
    "POSTGRES_DB=${local.envs["database"]}"
  ]

  # Porta 5432 interna (Airflow) e 5433 externa (pgAdmin/Windows)
  ports {
    internal = 5432
    external = 5434
  }

# Volume configurado para a versão 18
  volumes {
    # MUDANÇA AQUI: Adicione o abspath()
    host_path      = abspath("${path.module}/../postgres_data")
    container_path = "/var/lib/postgresql"
  }
}

# 2. IMAGEM DO DASHBOARD
resource "docker_image" "dashboard_img" {
  name = "weather_dashboard:latest"
  build {
    context    = "${path.module}/.." # Caminho para a raiz do projeto
    dockerfile = "Dockerfile"
  }
}

# 3. CONTAINER DO DASHBOARD (Streamlit)
resource "docker_container" "weather_dashboard" {
  name  = "weather_dashboard"
  image = docker_image.dashboard_img.name

  networks_advanced { 
    name = docker_network.weather_net.name
  }

  # Porta 8501 exclusiva para o painel web
  ports { 
    internal = 8501
    external = 8501
  }

  depends_on = [docker_container.postgres_db]
}