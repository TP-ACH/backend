db = db.getSiblingDB('admin');
db.auth('root', 'toor');

db = db.getSiblingDB('sensor_data');
db.createUser({
  user: 'fastapi',
  pwd: '1234',
  roles: [
    {
      role: 'readWrite',
      db: 'sensor_data',
    },
  ],
});

db.createCollection('data');