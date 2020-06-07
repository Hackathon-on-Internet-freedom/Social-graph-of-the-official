import argparse
import json
import time

from VKAPI.vkapi import VKAPI


class Rater():
    # Мой автор не хочет заниматься любовью с наследованием, но хочет MVP, почините меня пожалуйста
    def __init__(self, vkapi):
        self.api = vkapi

    def get_friends(self, vkid: int = None):
        return self.api.get_friends(vkid)

    def get_profile_info(self, target_id):
        return self.api.get_profile_info(target_id)

    def rate(self, target_id):
        target_profile = self.get_profile_info(target_id)
        # Используем искусственные задержки, чтобы не вляпаться в ограничение vkapi, учитывать которое пока неготовы
        are_friends = self.api.friend_of(target_id)
        time.sleep(0.5)
        same_last_name = self.api.check_last_names(target_profile)
        time.sleep(0.5)
        are_related = self.api.are_related(target_profile)
        time.sleep(0.5)
        matching_city = self.api.matching_city(target_profile)
        time.sleep(0.5)

        education_report = self.api.matching_education(target_profile)
        if len(education_report["match"]) > 0:
            matching_education = True
        else:
            matching_education = False
        time.sleep(0.5)
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
                 are_related * rateconfig["related"] + \
                 matching_city * rateconfig["city"] + \
                 matching_education * rateconfig["education"] + \
                 matching_military * rateconfig["military"] + \
                 matching_group_subscriptions * rateconfig["groups"] + \
                 matching_user_subscriptions * rateconfig["usersub"]

        print(rating)
        return rating


def parse():
    parser = argparse.ArgumentParser(description='Research vk page.')
    parser.add_argument('id', type=int, help='type a vk id')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    official_id = args.id
    vkapi = VKAPI(official_id,
                  token_location="../VKAPI/token.txt",
                  required_fields_config_location="../VKAPI/reqfields.txt")
    rater = Rater(vkapi)
    friendlist = rater.get_friends()
    result = {}
    for friend in friendlist["items"]:
        result[friend] = rater.rate(friend)
    print(result)


if __name__ == '__main__':
    main()
