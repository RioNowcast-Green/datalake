para ativar a venv: source .venv/bin/activate

para rodar o docker
-- docker build --no-cache
-- docker compose down -v  
-- docker compose up -d
-- docker compose up
-- docker exec -it datalake_postgres psql -U datalake_service -d datalake -c "CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';"
