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

resource "docker_container" "postgres_db" {
  name  = "weather_postgres"
  image = "postgres:15"
  networks_advanced { name = docker_network.weather_net.name }
  env = [
    "POSTGRES_USER=${local.envs["user"]}",
    "POSTGRES_PASSWORD=${local.envs["password"]}",
    "POSTGRES_DB=${local.envs["database"]}"
  ]
}

resource "docker_container" "weather_dashboard" {
  name  = "weather_dashboard"
  image = "weather_dashboard:latest" # Você precisará dar um 'docker build' antes
  networks_advanced { name = docker_network.weather_net.name }
  
  ports {
    internal = 8501
    external = 8501
  }
}