import argparse
import json
from pprint import pprint
import requests

import vk_api


# Корректные примеры: https://vk.com/id129244038, http://vk.com/durov.
def verify_url(url):
    if not url.startswith('https://vk.com/') and not url.startswith('https://vk.com/'):
        return False
    response = requests.get(url)
    if int(response.status_code) != 200:
        return False
    return True


def get_id_from_url(url, token):
    name = url.split('/')[-1]
    try:
        int(name[2:])
        if name[:2] == "id":
            vkid = name[2:]
        else:
            raise ValueError
    except ValueError:
        # используем сырой api, потому что vk_api не умеет в ники
        reqres = requests.get(
            f"https://api.vk.com/method/users.get?user_ids={name}&v=5.107&access_token={token}").content
        vkid = json.loads(reqres)["response"][0]["id"]
    return vkid


class VkApiWrapper:
    _FIELDS_TO_REQUEST = ['home_town',
                          'education',
                          'universities',
                          'schools',
                          'military',
                          'sex',
                          'relatives',
                          'maiden_name']

    def __init__(self, url, token, profile_info=None, friends=None, subscriptions=None):
        self.vk_id = get_id_from_url(url, token)
        self.api = vk_api.VkApi(token=token)
        self.profile_info = profile_info
        if self.profile_info is None:
            self.profile_info = self.get_profile_info()
        self.friends = friends
        if self.friends is None:
            self.friends = self.get_friends()["items"]
        self.subscriptions = subscriptions
        if self.subscriptions is None:
            self.subscriptions = self.get_subscriptions()

    def get_friends(self, vk_id: int = None):
        if not vk_id:
            vk_id = self.vk_id
        return self.api.method("friends.get", {"user_id": vk_id})

    def friend_of(self, vk_id: int):
        official_friends = self.friends
        return vk_id in official_friends

    def get_matching_friends(self, target_id: int):
        official_friends = set(self.get_friends()["items"])
        target_friends = set(self.get_friends(vk_id=target_id)["items"])
        matching_friends = sorted(list(official_friends.intersection(target_friends)))
        return {"count": len(matching_friends), "items": matching_friends}

    def get_profile_info(self, vk_id: int = None, required_fields: list = None):
        if not vk_id:
            vk_id = self.vk_id
        if not required_fields:
            required_fields_prepared = ", ".join(self._FIELDS_TO_REQUEST)
        else:
            required_fields_prepared = ", ".join(required_fields)
        profile = self.api.method("users.get", {"user_id": vk_id, "fields": required_fields_prepared})
        print('Обрабатывается {} {} – https://vk.com/id{}'.format(profile[0]['first_name'],
                                                              profile[0]['last_name'],
                                                              profile[0]['id']))
        return profile[0]

    def _generic_last_name_comparison(self, friend_profile: dict, field: str):
        profile1 = self.profile_info
        profile2 = friend_profile
        last_name1 = profile1.get(field)
        last_name2 = profile2.get(field)
        if last_name1 is not None and last_name2 is not None and last_name1 != "" and last_name2 != "":
            if len(last_name1) < len(last_name2):
                short_last_name = last_name1
                long_last_name = last_name2
            else:
                short_last_name = last_name2
                long_last_name = last_name1
            return long_last_name.startswith(short_last_name[:-2])
        else:
            return False

    def check_last_names(self, friend_profile: dict):
        return self._generic_last_name_comparison(friend_profile, "last_name")

    def check_maiden_names(self, friend_profile: dict):
        return self._generic_last_name_comparison(friend_profile, "maiden_name")

    def matching_city(self, target_profile: dict):
        profile1 = self.profile_info
        profile2 = target_profile
        home_town1 = profile1.get("home_town")
        home_town2 = profile2.get("home_town")
        return home_town1 == home_town2

    def matching_education(self, target_profile: dict):
        profile1 = self.profile_info
        name1 = f"{profile1['first_name']} {profile1['last_name']}"
        profile2 = target_profile
        name2 = f"{profile2['first_name']} {profile2['last_name']}"
        result = {"match": {}, "mismatch": {}}
        for field in ["faculty", "faculty_name", "graduation", "university", "university_name"]:
            field1 = profile1.get(field)
            field2 = profile2.get(field)
            if field1 == field2:
                result["match"][field] = field1
            else:
                try:
                    result["mismatch"][field][name1]
                except KeyError:
                    result["mismatch"][field] = {}
                result["mismatch"][field][name1] = field1
                result["mismatch"][field][name2] = field2
        for field in ["schools", "universities"]:
            result = self._generic_comparison(result, profile1, profile2, field)
        return result

    def matching_military(self, target_profile: dict):
        profile1 = self.profile_info
        profile2 = target_profile
        result = {"match": {}, "mismatch": {}}
        result = self._generic_comparison(result, profile1, profile2, "military")
        return result

    @staticmethod
    def _generic_comparison(result, profile1, profile2, field):
        name1 = f"{profile1['first_name']} {profile1['last_name']}"
        name2 = f"{profile2['first_name']} {profile2['last_name']}"
        list1 = profile1.get(field)
        list2 = profile2.get(field)
        for item1 in list1:
            for item2 in list2:
                allkeys = set(item1.keys()) | set(item2.keys())
                for key in allkeys:
                    curval1 = item1.get(key)
                    curval2 = item2.get(key)
                    if curval1 == curval2:
                        if curval1:  # если None, то зачем сравнивать None с None, нам их совпадение ничего не даёт
                            try:
                                result["match"][field][key]
                            except KeyError:
                                try:
                                    result["match"][field]
                                except KeyError:
                                    result["match"][field] = {}
                                result["match"][field][key] = []
                            result["match"][field][key].append(curval1)
                    else:
                        try:
                            result["mismatch"][field][key][name1]
                        except KeyError:
                            try:
                                result["mismatch"][field][key]
                            except KeyError:
                                try:
                                    result["mismatch"][field]
                                except KeyError:
                                    result["mismatch"][field] = {}
                                result["mismatch"][field][key] = {}
                            result["mismatch"][field][key][name1] = []
                            result["mismatch"][field][key][name2] = []
                        result["mismatch"][field][key][name1].append(curval1)
                        result["mismatch"][field][key][name2].append(curval2)
        return result

    def get_subscriptions(self, vk_id: int = None):
        if not vk_id:
            vk_id = self.vk_id
        try:
            subs_list = self.api.method("users.getSubscriptions", values={"user_id": vk_id})
        except vk_api.exceptions.ApiError:
            subs_list = {"groups": {"items": [], "count": 0}, "users": {"items": [], "count": 0}}
        return subs_list

    def get_matching_subscriptions(self, target_id: int):
        sublist1 = self.subscriptions
        groupset1 = set(sublist1["groups"]["items"])
        userset1 = set(sublist1["users"]["items"])
        sublist2 = self.get_subscriptions(target_id)
        groupset2 = set(sublist2["groups"]["items"])
        userset2 = set(sublist2["users"]["items"])
        matchgroups = groupset1.intersection(groupset2)
        matchusers = sorted(list(userset1.intersection(userset2)))
        result = {
            "groups": {
                "count": len(matchgroups),
                "items": matchgroups
            },
            "users": {
                "count": len(matchusers),
                "items": matchusers
            }
        }
        return result

    def are_related(self, target_profile: dict):
        relations1 = self.profile_info.get("relatives")
        if relations1:
            for relation in relations1:
                if relation["id"] == target_profile["id"]:
                    return True
        relations2 = self.get_profile_info(target_profile["id"]).get("relatives")
        if relations2:
            for relation in relations2:
                if relation["id"] == self.vk_id:
                    return True
        return False


def parse():
    _DEFAULT_VK_URL = 'https://vk.com/navalny'  # Алексей Навальный
    _DEFAULT_OTHER_URL = 'https://vk.com/abacabadabacabaeabacabadabacaba'  # Николай Дуров

    parser = argparse.ArgumentParser(description='Research vk page.')
    parser.add_argument('--vk_token', type=str, help='VK dev token')
    parser.add_argument('--url', type=str, default=_DEFAULT_VK_URL,
                        help=f'URL of a VK profile (ex. {_DEFAULT_VK_URL})')
    parser.add_argument('--other_url', type=str, default=_DEFAULT_OTHER_URL,
                        help=f'URL of another VK profile (ex. {_DEFAULT_OTHER_URL})')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    api = VkApiWrapper(args.url, args.vk_token)

    other_id = get_id_from_url(args.other_url, args.vk_token)
    req_res = api.get_matching_subscriptions(other_id)
    pprint(req_res)


if __name__ == '__main__':
    main()
