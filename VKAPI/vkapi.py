from pprint import pprint

from vk_api import VkApi


class VKAPI:
    def __init__(self, token_location: str = "token.txt", official_id: int = 129244038):
        self.vkid = official_id
        with open(token_location) as f:
            token = f.read()
        self.api = VkApi(token=token)

    def get_friends(self, vkid: int = None):
        if not vkid:
            vkid = self.vkid
        return self.api.method("friends.get", {"user_id": vkid})

    def friend_of(self, vkid: int):
        official_friends = self.get_friends()["items"]
        return (vkid in official_friends)

    def get_matching_friends(self, target_id: int):
        official_friends = set(self.get_friends()["items"])
        target_friends = set(self.get_friends(vkid=target_id)["items"])
        matching_friends = sorted(list(official_friends.intersection(target_friends)))
        return {"count": len(matching_friends), "items": matching_friends}


def main():
    vkapi = VKAPI(official_id=512036336)
    reqres = vkapi.friend_of(22357297)
    print(reqres)
    reqres = vkapi.get_matching_friends(22357297)
    pprint(reqres)


if __name__ == '__main__':
    main()
