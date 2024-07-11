db.createUser({
  user: process.env.MONGO_INITDB_USER,
  pwd: process.env.MONGO_INITDB_PASSWORD,
  roles: [{
    role: 'readWriteAnyDatabase',
    db: 'admin'
  }]
});
