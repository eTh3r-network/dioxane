from identity_provider.identity_provider import IdentityProvider
from models.identity import Identity


class SimpleKeyProvider(IdentityProvider):
    @staticmethod
    def getIdentity(identity: str) -> Identity:
        return Identity(name=identity,
                        key_length=4,
                        key=int(f"0x1312{identity}"),
                        key_id_length=2,
                        key_id=int(f"0x{identity}"))


baba: Identity = SimpleKeyProvider.getIdentity("baba")
fefe: Identity = SimpleKeyProvider.getIdentity("fefe")