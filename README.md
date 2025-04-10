# TIME-MANAGEMENT-AGENT

## Lên agent

**Prerequisite**: docker hoặc docker-compose

Nhanh nhất:
```
docker network create timenest
docker-compose up --build
```
Nếu muốn xài dockerfile, đỡ phải create network:
```
cd src/

docker build -t timenest-agent:latest .

docker run -d \
  --name timenest-agent \
  -p 5001:5001 \
  --env-file .env \
  timenest-agent:latest
```
check `localhost:5001/docs` xem hdsd 