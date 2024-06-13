# backend

## How to run it

- Tener instalado docker y docker compose.

- Copiar el .env.example como .env y completar las variables de ambiente

```
cp .env.example .env
```
- Crear el pwfile, el archivo donde se guardaran los usuarios de Mosquitto
```
touch mosquitto/config/pwfile
```

- Generar la DB para mosquitto. Usamos Sqlite3 porque es más facil y es poca data
(Requiere tener instalado Sqlite3, apt install sqlite3)

```
mkdir mosquitto/data
cd mosquitto/data
sqlite3 mosquitto.db
```

Puede tener otro nombre el file de db pero tienen que configurarlo en mosquitto.conf.
Tarda unos segundos pero les debería aparecer el archivo en esa carpeta. Una vez generado
pueden salir de sqlite3

- En el root del proyecto, ejecutar el siguiente comando

```
docker-compose up -d
```

- Una vez levantado (pueden validarlo con docker compose ps), tienen que generar el archivo y los usuarios para
mosquitto. (container-name esta definido en el docker-compose.yml como mqtt5)
```
docker compose exec <container-name> sh

Create new password file and add user and it will prompt for password
mosquitto_passwd -c /mosquitto/config/pwfile user1

Add additional users (remove the -c option) and it will prompt for password
mosquitto_passwd /mosquitto/config/pwfile user2

delete user command format
mosquitto_passwd -D /mosquitto/config/pwfile <user-name-to-delete>
```

- Una vez hecho todo esto pueden validar si está todo corriendo correctamente al ver los logs con `docker compose logs -f`


### Si esta todo OK, deberia estar corriendo en [localhost:8000](http://localhost:8000)

