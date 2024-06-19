class ConfigStrategy:
    def get_chat_id_gruppo(self):
        raise NotImplementedError("Subclasses must implement get_chat_id_gruppo")

    def get_chat_id_vetrina(self):
        raise NotImplementedError("Subclasses must implement get_chat_id_vetrina")

    def get_chat_id_feedback(self):
        raise NotImplementedError("Subclasses must implement get_chat_id_feedback")

    def get_chat_id_zio(self):
        raise NotImplementedError("Subclasses must implement get_chat_id_zio")

    def get_chat_id_aste(self):
        raise NotImplementedError("Subclasses must implement get_chat_id_aste")
    
    def get_chat_id_noleggi(self):
        raise NotImplementedError("Subclasses must implement get_chat_id_noleggi")

class ProdConfig(ConfigStrategy):
    def get_chat_id_gruppo(self):
        return -1001397315169

    def get_chat_id_vetrina(self):
        return -1001872734100

    def get_chat_id_feedback(self):
        return -1001956565384

    def get_chat_id_zio(self):
        return [-1001611895993, -1001979086464]

    def get_chat_id_aste(self):
        return -1001880758375
    
    def get_chat_id_noleggi(self):
        return -1001644892959

class TestConfig(ConfigStrategy):
    def get_chat_id_gruppo(self):
        return -1001721979634

    def get_chat_id_vetrina(self):
        return -1001996668260

    def get_chat_id_feedback(self):
        return -1001996668260

    def get_chat_id_zio(self):
        return [-1001996668260, -1001996668260]

    def get_chat_id_aste(self):
        return -1001668231373

    def get_chat_id_noleggi(self):
        return -1001644892959
