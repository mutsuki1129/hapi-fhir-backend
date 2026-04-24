$env:SPRING_PROFILES_ACTIVE = "dev,auth"
$env:FHIR_JWT_ISSUER_URI = "http://keycloak:8180/realms/fhir"
$env:COMPOSE_PROFILES = "auth"
docker compose -f docker-compose.yml -f docker-compose.auth.yml up -d --remove-orphans
