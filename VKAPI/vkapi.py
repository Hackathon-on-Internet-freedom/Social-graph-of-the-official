from pprint import pprint

from vk_api import VkApi


class VKAPI:
    def __init__(self, token_location: str = "token.txt", official_id: int = 129244038):
        self.vkid = official_id
        with open(token_location) as f:
            token = f.read()
        self.api = VkApi(token=token)

    def get_friends(self):
        return self.api.method("friends.get", {"user_id": self.vkid})


def main():
    vkapi = VKAPI()
    reqres = vkapi.get_friends()
    pprint(reqres)


if __name__ == '__main__':
    main()
