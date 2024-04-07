from pymongo import MongoClient

# Connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['sound']

# Define the user collection schema
user = {
    'name': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True, 'unique': True},
    'password': {'type': 'string', 'required': True},
    'isAdmin': {'type': 'boolean', 'default': False},
    'sounds': {'type': 'list', 'item_type': 'ObjectId', 'ref': 'Sound'}
}

# Define the sound collection schema
sound = {
    'name': {'type': 'string', 'required': True},
    'description': {'type': 'string', 'required': True},
    'link_sound': {'type': 'string', 'required': True}
}

# Create the user collection
users = db['users']

# Create the sound collection
sounds = db['sounds']
