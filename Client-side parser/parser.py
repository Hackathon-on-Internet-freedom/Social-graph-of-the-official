
import argparse

parser = argparse.ArgumentParser(description='Research vk page.')
parser.add_argument('url', type=str, help='type a vk page, like vk.com/id111222333 or vk.com/durov')
args = parser.parse_args()
vk_url = args.url


def pase():
    print(vk_url)
pase()
