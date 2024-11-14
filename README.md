# backend

## Prerequisitos

- Tener instalado docker y docker compose.
- Tener instalado sqlite3.

## Iniciar backend

- Copiar el .env.example como .env y completar las variables de ambiente

```
cp .env.example .env
```

- Correr el script para generar los archivos de mosquitto

```
./init.sh
```

- En el root del proyecto, ejecutar el siguiente comando

```
docker-compose up -d
```

- Una vez hecho todo esto pueden validar si está todo corriendo correctamente al ver los logs con `docker compose logs -f`

### Si esta todo OK, deberia estar corriendo en [localhost:8000](http://localhost:8000)
