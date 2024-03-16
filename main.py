from client.simple_client.simple_client import SimpleClient
from models.identity import Identity

if __name__ == '__main__':
    me: Identity = Identity(name="Amus", key_id_length=2, key_id=0x1312, key_length=4, key=0x1312b00b)

    baophes: Identity = Identity(2, 0x964d, name="Baophes")
    cysalia: Identity = Identity(2, 0xa156, name="Cysalia")

    client = SimpleClient(me, "DIOXANE")
    client.connect()
    client.registerIdentity(baophes)
    client.registerIdentity(cysalia)
