DOCKER_COMPOSE_FILE="./docker/docker-compose-development.yml"

docker compose -f ${DOCKER_COMPOSE_FILE} stop
docker compose -f ${DOCKER_COMPOSE_FILE} rm --force

docker compose -f ${DOCKER_COMPOSE_FILE} build

docker compose -f ${DOCKER_COMPOSE_FILE} up -d --remove-orphans

docker compose -f ${DOCKER_COMPOSE_FILE} exec aircraft bash
