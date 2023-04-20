# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from riddle_me_this.user.services import *
import logging
import time

logging.basicConfig(filename='../../record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")


@blueprint.route("/")
@login_required
def members():
    """List members."""
    video_id = get_youtube_video_id('https://www.youtube.com/watch?v=j_QH5wF9XBg&t')
    # w = get_video_info(video_id)
    # k = get_and_load_transcripts(video_id)
    # logging.info(w)
    # logging.info(k)
    # with open('./transcript.txt', 'w') as f:
    #     f.write(k)
    return render_template("users/members.html")


@blueprint.route("/home_logged_in/")
@login_required
def home_logged_in():
    """Home page for logged in users."""
    return render_template("users/home_logged_in.html")



