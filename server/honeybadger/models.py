from honeybadger import db, bcrypt
import binascii
import datetime
import uuid

def stringify_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")

'''
import honeybadger
honeybadger.dropdb()
honeybadger.initdb()
#from honeybadger import bcrypt
#import binascii
#u = honeybadger.models.User(username='user', password_hash=bcrypt.generate_password_hash(binascii.hexlify('password')), email='tjt1980@gmail.com')
#honeybadger.db.session.add(u)
#honeybadger.db.session.commit()
t = honeybadger.models.Target(name='target1', guid='aedc4c63-8d13-4a22-81c5-d52d32293867', owner=1)
honeybadger.db.session.add(t)
honeybadger.db.session.commit()
b = honeybadger.models.Beacon(target_guid='aedc4c63-8d13-4a22-81c5-d52d32293867', agent='agent1', ip='1.2.3.4', port='80', useragent='Mac OS X', comment='this is a comment.', lat='38.2531419', lng='-85.7564855', acc='5')
honeybadger.db.session.add(b)
honeybadger.db.session.commit()
b = honeybadger.models.Beacon(target_guid='aedc4c63-8d13-4a22-81c5-d52d32293867', agent='agent1', ip='5.6.7.8', port='80', useragent='Mac OS X', comment='this is a comment.', lat='34.855117', lng='-82.114192', acc='1')
honeybadger.db.session.add(b)
honeybadger.db.session.commit()
'''

class Beacon(db.Model):
    __tablename__ = 'beacons'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    target_guid = db.Column(db.String, db.ForeignKey('targets.guid'), nullable=False)
    agent = db.Column(db.String)
    ip = db.Column(db.String)
    port = db.Column(db.String)
    useragent = db.Column(db.String)
    comment = db.Column(db.String)
    lat = db.Column(db.String)
    lng = db.Column(db.String)
    acc = db.Column(db.String)

    @property
    def serialized(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'time': stringify_datetime(self.time),
            'target': self.target.name,
            'agent': self.agent,
            'ip': self.ip,
            'port': self.port,
            'useragent': self.useragent,
            'comment': self.comment,
            'lat': self.lat,
            'lng': self.lng,
            'acc': self.acc,
        }

    def __repr__(self):
        return "<Beacon '{}'>".format(self.target.name)

class Target(db.Model):
    __tablename__ = 'targets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    guid = db.Column(db.String, default=lambda: str(uuid.uuid4()))
    owner = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    beacons = db.relationship('Beacon', backref='target', lazy='dynamic')

    @property
    def beacon_count(self):
        return len(self.beacons.all())

    def __repr__(self):
        return "<Target '{}'>".format(self.name)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    email = db.Column(db.String)
    targets = db.relationship('Target', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(binascii.hexlify(password))

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, binascii.hexlify(password))

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)
