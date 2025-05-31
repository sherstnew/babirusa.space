const babirusaUser = process.env.BABIRUSA_USER;
const babirusaPassword = process.env.BABIRUSA_PASSWORD;

db = db.getSiblingDB('admin').auth(
    babirusaUser,
    babirusaPassword
);
db.createUser({
    user: babirusaUser,
    pwd: babirusaPassword,
    roles: ["readWrite"],
});

db = db.getSiblingDB('babirusa');
db.createCollection('init');
db.createUser({
  user: babirusaUser,
  pwd: babirusaPassword,
  roles: [{ role: 'readWrite', db: 'babirusa' }]
});

db = db.getSiblingDB('babirusa-test');
db.createCollection('init');
db.createUser({
  user: babirusaUser,
  pwd: babirusaPassword,
  roles: [{ role: 'readWrite', db: 'babirusa-test' }]
});

print('Database initialization completed!');