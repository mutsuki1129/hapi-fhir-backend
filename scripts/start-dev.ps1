$env:SPRING_PROFILES_ACTIVE = "dev"
$env:COMPOSE_PROFILES = ""
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --remove-orphans
