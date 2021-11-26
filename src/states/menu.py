class Menu:
    def __init__(self, Requests, log, presences):
        self.Requests = Requests
        self.log = log
        self.presences = presences

    def get_party_members(self, self_puuid, presencesDICT):
        res = []
        for presence in presencesDICT:
            if presence["puuid"] == self_puuid:
                decodedPresence = self.presences.decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    party_id = decodedPresence["partyId"]
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel":
                                                                                     decodedPresence["accountLevel"]}})
        self.log(f"retrieved party members: {res}")
        return res