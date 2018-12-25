from .helper import get_config
import os

confpath = os.environ.get("OVERRIDE_CONF", None) or "config_override.yaml"

conf = get_config(overide=confpath)

maildict = {'sender': conf['MAIL_SENDER'], 'sender_alias': conf['MAIL_SENDER_ALIAS'],
            'password': conf['MAIL_PASSWORD'],
            'server': conf['MAIL_SERVER'], 'port': conf['MAIL_PORT']}
