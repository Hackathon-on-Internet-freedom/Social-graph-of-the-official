import asyncio

from social_graph.config import Config
from social_graph.vk_api import VK_API


async def main():
    api = VK_API(Config.VK_API_TOKEN)
    user = await api.request_procedure_call(
        Config.VK_API_PROCEDURE_NAME,
        params={'user_id': 'abacabadabacabaeabacabadabacaba'},
    )
    print(user.user_info)
    # Prints:
"""VKUserWithFields(id_=6, first_name='Николай', last_name='Дуров', 
deactivated=None, is_closed=False, can_access_closed=True, 
screen_name='abacabadabacabaeabacabadabacaba', maiden_name=None, 
relatives=None, relation=None, relation_partner=None, home_town=None, 
schools=None, universities=None, military=None, career=None, 
counters={'albums': 2, 'videos': 32, 'audios': 14, 'photos': 21, 
'friends': 292, 'online_friends': 18, 'mutual_friends': 0, 'followers': 54831, 
'subscriptions': 13, 'pages': 141, 'clips_followers': 55123})"""


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
