from environs import Env

env = Env()
env.read_env()


class Config:
    DEBUG: bool = env.bool('DEBUG', False)
    VK_API_TOKEN: str = env('VK_API_TOKEN')
    VK_API_PROCEDURE_NAME: str = env('VK_API_PROCEDURE_NAME', '')
    VK_API_VERSION: str = '5.120'
