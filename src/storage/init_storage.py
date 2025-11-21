from b2sdk.v2 import *

from protectapp import settings


def init_remote_storage() -> B2Api | dict:
    if is_backblaze():
        config = settings.STORAGE_CONFIG['backblaze']
        info = InMemoryAccountInfo()
        b2_api = B2Api(info, cache=AuthInfoCache(info))
        application_key_id = config['application_key_id']
        application_key = config['application_key']
        b2_api.authorize_account("production", application_key_id, application_key)
        return b2_api

    raise Exception('Storage provider is not defined')


def is_backblaze():
    return settings.STORAGE_TYPE == 'backblaze'
