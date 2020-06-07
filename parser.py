import argparse
import json
import time

from vkapi import VkApiWrapper


class Rater:
    # Мой автор не хочет заниматься любовью с наследованием, но хочет MVP, почините меня пожалуйста
    def __init__(self, vk_api):
        self.api = vk_api

    def get_friends(self, vk_id: int = None):
        return self.api.get_friends(vk_id)

    def get_profile_info(self, target_id):
        return self.api.get_profile_info(target_id)

    def rate(self, target_id):
        target_profile = self.get_profile_info(target_id)
        # Используем искусственные задержки, чтобы не вляпаться в ограничение vkapi, учитывать которое пока неготовы
        are_friends = self.api.friend_of(target_id)
        time.sleep(0.5)
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
        time.sleep(0.5)

        same_subscriptions = self.api.get_matching_subscriptions(target_id)
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
        return rating


def parse():
    _DEFAULT_VK_URL = 'https://vk.com/id129244038'  # Алексей Навальный
    _DEFAULT_REQ_FIELDS_PATH = 'req_fields.txt'

    parser = argparse.ArgumentParser(description='Research vk page.')
    parser.add_argument('--url', type=int, default=_DEFAULT_VK_URL,
                        help=f'URL of VK profile (ex. {_DEFAULT_VK_URL})')
    parser.add_argument('--vk_token', type=str, help='VK dev token')
    parser.add_argument('--req_fields_path', type=str, default=_DEFAULT_REQ_FIELDS_PATH,
                        help='path to a txt file with the list of profile fields to analyze')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    api = VkApiWrapper(args.url, args.vk_token, args.req_fields_path)

    rater = Rater(api)
    friends_list = rater.get_friends()
    result = {}
    for friend in friends_list["items"]:
        result[friend] = rater.rate(friend)
    print(result)


if __name__ == '__main__':
    main()
