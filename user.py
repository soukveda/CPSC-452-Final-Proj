class User():

    user_count = 0

    def __init__(self, priv, pub):
        type(self).user_count += 1
        self.user = type(self).user_count 
        self.priv_key = priv
        self.pub_key = pub