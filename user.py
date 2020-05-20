

list_of_users = []


class User(object):

    def __init__(self, address, priv, pub):
        list_of_users
        self.address = address
        self.priv_key = priv
        self.pub_key = pub
        self.amount = 0
        unique = True
        for i in list_of_users:
            if i.address == address or i.priv_key == priv or i.pub_key == pub:
                print("cannot create this user since an attribute is already taken")
                unique = False
        if unique:
            list_of_users.append(self)

    def get_user_pub(self, address):
        for i in list_of_users:
            if i.address == address:
                return i.pub_key
        return 0


if __name__ == '__main__':

    temp = User(1, 2, 3)
    temp2 = User(2, 3, 4)
    tempPub = temp2.get_user_pub(1)
    print(tempPub)
    for i in list_of_users:
        print(i.__dict__)



