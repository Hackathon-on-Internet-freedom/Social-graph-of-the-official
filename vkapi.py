import argparse
from pprint import pprint

import vk_api


class VkApiWrapper:
    def __init__(self,
                 official_id: int = 129244038,
                 token_location: str = "token.txt",
                 required_fields_config_location: str = "req_fields.txt"):
        self.vk_id = official_id
        with open(token_location) as f:
            token = f.read()
        self.api = vk_api.VkApi(token=token)
        with open(required_fields_config_location) as f:
            self.required_fields = f.read().split("\n")
        self.profile_info = self.get_profile_info()

    def get_friends(self, vk_id: int = None):
        if not vk_id:
            vk_id = self.vk_id
        return self.api.method("friends.get", {"user_id": vk_id})

    def friend_of(self, vk_id: int):
        official_friends = self.get_friends()["items"]
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
            required_fields_prepared = ", ".join(self.required_fields)
        else:
            required_fields_prepared = ", ".join(required_fields)
        profile = self.api.method("users.get", {"user_id": vk_id, "fields": required_fields_prepared})
        pprint(profile)
        return profile[0]

    def check_last_names(self, friend_profile: dict):
        profile1 = self.profile_info
        profile2 = friend_profile
        last_name1 = profile1["last_name"]
        last_name2 = profile2["last_name"]
        if len(last_name1) < len(last_name2):
            short_last_name = last_name1
            long_last_name = last_name2
        else:
            short_last_name = last_name2
            long_last_name = last_name1
        return long_last_name.startswith(short_last_name[:-2])

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
        pprint(profile1)
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
        sublist1 = self.get_subscriptions()
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
    _DEFAULT_VK_ID = 129244038  # Алексей Навальный
    _DEFAULT_OTHER_ID = 6  # Николай Дуров
    _DEFAULT_TOKEN_PATH = 'token_example.txt'
    _DEFAULT_REQ_FIELDS_PATH = 'req_fields.txt'

    parser = argparse.ArgumentParser(description='Research vk page.')
    parser.add_argument('--id', type=int, default=_DEFAULT_VK_ID,
                        help=f'ID of a VK profile (ex. {_DEFAULT_VK_ID})')
    parser.add_argument('--other', type=int, default=_DEFAULT_OTHER_ID,
                        help=f'ID of a VK profile (ex. {_DEFAULT_OTHER_ID})')
    parser.add_argument('--token_path', type=str, default=_DEFAULT_TOKEN_PATH,
                        help='path to a txt file with VK dev token')
    parser.add_argument('--req_fields_path', type=str, default=_DEFAULT_REQ_FIELDS_PATH,
                        help='path to a txt file with the list of profile fields to analyze')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    api = VkApiWrapper(args.id, args.token_path, args.req_fields_path)

    req_res = api.get_matching_subscriptions(args.other)
    pprint(req_res)


if __name__ == '__main__':
    main()