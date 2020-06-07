from pprint import pprint

import vk_api


class VKAPI:
    def __init__(self,
                 official_id: int = 129244038,
                 token_location: str = "token.txt",
                 required_fields_config_location: str = "reqfields.txt"):
        self.vkid = official_id
        with open(token_location) as f:
            token = f.read()
        self.api = vk_api.VkApi(token=token)
        with open(required_fields_config_location) as f:
            self.required_fields = f.read().split("\n")
        self.profile_info = self.get_profile_info()

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

    def get_profile_info(self, vkid: int = None, required_fields: list = None):
        if not vkid:
            vkid = self.vkid
        if not required_fields:
            required_fields_prepared = ", ".join(self.required_fields)
        else:
            required_fields_prepared = ", ".join(required_fields)
        profile = self.api.method("users.get", {"user_id": vkid, "fields": required_fields_prepared})
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
        return (long_last_name.startswith(short_last_name[:-2]))

    def matching_city(self, target_profile: dict):
        profile1 = self.profile_info
        profile2 = target_profile
        home_town1 = profile1.get("home_town")
        home_town2 = profile2.get("home_town")
        return (home_town1 == home_town2)

    def matching_education(self, target_profile: dict):
        profile1 = self.profile_info
        name1 = f"{profile1['first_name']} {profile1['last_name']}"
        profile2 = target_profile
        name2 = f"{profile2['first_name']} {profile2['last_name']}"
        result = {"match": {}, "mismatch": {}}
        for field in ["faculty", "faculty_name", "graduation", "university", "university_name"]:
            field1 = profile1[field]
            field2 = profile2[field]
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
        list1 = profile1[field]
        list2 = profile2[field]
        for item1 in list1:
            for item2 in list2:
                allkeys = set(item1.keys()) | set(item2.keys())
                for key in allkeys:
                    curval1 = item1.get(key)
                    curval2 = item2.get(key)
                    if (curval1 == curval2):
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

    def get_subscriptions(self, vkid: int = None):
        if not vkid:
            vkid = self.vkid
        try:
            subs_list = self.api.method("users.getSubscriptions", values={"user_id": vkid})
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
                if relation["id"] == self.vkid:
                    return True
        return False


def main():
    vkapi = VKAPI()
    reqres = vkapi.get_matching_subscriptions(512036336)
    pprint(reqres)


if __name__ == '__main__':
    main()
