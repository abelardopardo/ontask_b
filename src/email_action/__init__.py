from __future__ import print_function

import hashlib
import base64
from Crypto import Random
from Crypto.Cipher import AES

import django.conf

default_app_config = 'email_action.apps.EmailActionConfig'


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * \
                   chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class HandlerBasic(object):

    """
    Expected class name when deriving from this abstract class
    """
    expected_class_name = "Handler"

    """
    Name of the context to differentiate events from multiple experiences. Make
    sure your name is unique as it will not be checked at run-time
    """
    context_name = 'YOUR CONTEXT NAME HERE'

    # A pair (low, high) to restrict the indicator version to consider
    version_range = None

    def __init__(self):
        self.render_dict = {
            'template': '',
            'template_sk': '',
            'template_sr': '',
            'data_capture_url': django.conf.settings.EVENT_RECORD_URL,
            'data_capture_method': 'POST',
            'data_capture_subject_name': 'leco_subject_field',
            'data_capture_verb_name': 'leco_verb_field',
            'data_capture_object_name': 'leco_object_field',
            'data_capture_context_name': 'leco_context_field',
            'data_capture_context': 'YOUR CONTEXT NAME HERE',
            'page_title': '',
            'user_id': '',
            'no_data': True,
            'show_suggestions': False,
            'dboard_title': '',
            'suggestion_title': 'Your Learning Strategy'
        }

    def get_version(self, data_dict=None):
        """
        :param data_dict: Optional dictionary with categories

        :return: Returns one of the possible categories.
        """
        del data_dict

        return 0

    def update_render_dict(self, username, version=None):
        """
        Performs some last minute updates in the render dictionary before
        being used.
        param: username Some auxiliary parameter that may be needed
        :return:
        """
        pass
