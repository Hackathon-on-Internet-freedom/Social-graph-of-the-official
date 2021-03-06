import argparse
import collections
import json
import time
from pprint import pprint

from vkapi import VkApiWrapper


class Rater:
    # Мой автор не хочет заниматься любовью с наследованием, но хочет MVP, почините меня пожалуйста
    def __init__(self, vk_api):
        self.api = vk_api

    def get_friends(self):
        return self.api.friendlist

    def get_profile_info(self, target_id):
        return self.api.get_profile_info(target_id)

    def rate(self, target_profile):
        # Используем искусственные задержки, чтобы не вляпаться в ограничение vkapi, учитывать которое пока неготовы
        are_friends = self.api.friend_of(target_profile["id"])
        time.sleep(0.34)
        same_maiden_name = self.api.check_maiden_names(target_profile)
        same_last_name = self.api.check_last_names(target_profile)
        are_related = self.api.are_related(target_profile)
        matching_city = self.api.matching_city(target_profile)

        education_report = self.api.matching_education(target_profile)
        if len(education_report["match"]) > 0:
            matching_education = True
        else:
            matching_education = False
        military_report = self.api.matching_military(target_profile)
        if len(military_report["match"]) > 0:
            matching_military = True
        else:
            matching_military = False
        time.sleep(0.34)

        same_subscriptions = self.api.get_matching_subscriptions(target_profile["id"])
        if same_subscriptions["groups"]["count"] > 20:  # условное число, будет настраиваться потом
            matching_group_subscriptions = True
        else:
            matching_group_subscriptions = False
        if same_subscriptions["users"]["count"] > 1:  # то же самое
            matching_user_subscriptions = True
        else:
            matching_user_subscriptions = False

        with open("rateconfig.json") as f:
            rateconfig = json.load(f)

        report = {
            "friends": are_friends,
            "same_last_name": same_last_name,
            "same_maiden_name": same_maiden_name,
            "related": are_related,
            "matching_city": matching_city,
            "matching_education": matching_education,
            "matching_military": matching_military,
            "matching_group_subscriptions": matching_group_subscriptions,
            "matching_user_subscriptions": matching_user_subscriptions
        }

        rating = are_friends * rateconfig["friends"] + \
                 same_last_name * rateconfig["last_name"] + \
                 same_maiden_name * rateconfig["maiden_name"] + \
                 are_related * rateconfig["related"] + \
                 matching_city * rateconfig["city"] + \
                 matching_education * rateconfig["education"] + \
                 matching_military * rateconfig["military"] + \
                 matching_group_subscriptions * rateconfig["groups"] + \
                 matching_user_subscriptions * rateconfig["usersub"]

        print(rating)
        return {"rating": rating, "report": report}


def get_token_from_config():
    with open("token.txt") as f:
        return f.read()


def parse():
    _DEFAULT_VK_URL = 'https://vk.com/navalny'  # Алексей Навальный

    parser = argparse.ArgumentParser(description='Research vk page.')
    parser.add_argument('--url', type=str, default=_DEFAULT_VK_URL,
                        help=f'URL of VK profile (ex. {_DEFAULT_VK_URL})')
    parser.add_argument('--vk_token', type=str, help='VK dev token')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    api = VkApiWrapper(args.url, args.vk_token)

    rater = Rater(api)
    result = {}
    for friend in rater.api.friends:
        friend_result = rater.rate(rater.api.friends[friend])
        rating = friend_result["rating"]
        result[(rating, friend[0], friend[1])] = friend_result
    odresult = dict(collections.OrderedDict(reversed(sorted(result.items()))))
    print(odresult)


if __name__ == '__main__':
    main()
