# -*- coding: utf-8 -*-
""" Utility Functions """
import os
import json
import dotenv

dotenv.load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_google_credentials():
    """ Get Google Credentials """
    if GOOGLE_APPLICATION_CREDENTIALS:
        with open(GOOGLE_APPLICATION_CREDENTIALS) as f:
            return json.load(f)
    return None



