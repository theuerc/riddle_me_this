# -*- coding: utf-8 -*-
"""User views."""
import json
import logging
import os

import pandas as pd
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_login import login_required

from riddle_me_this.user.services import *  # noqa
from riddle_me_this.user.visualizations import *  # noqa

logging.basicConfig(
    filename="../../record.log",
    level=logging.DEBUG,
    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",  # noqa: F541
)

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")


@blueprint.route("/")
@login_required
def members():
    """
    Render the members page.

    Returns:
        A rendered members page.
    """
    return render_template("users/members.html")


@blueprint.route("/home_logged_in/", methods=["GET", "POST"])
@login_required
def home_logged_in():
    """
    Render the logged-in home page and handle the form submission for urls.

    Returns:
        A rendered home page or redirects to the video details page.
    """
    logging.info("Hello from from the logged in home page!")
    video_link = None
    session["id_submitted"] = None

    if request.method == "POST":
        try:
            video_link = request.form["link"]
            video_id = get_youtube_video_id(video_link)  # noqa
        except Exception as e:  # noqa
            logging.error(e)
            flash("Please enter a valid YouTube link", "danger")
            return redirect(url_for("user.home_logged_in"))
        session["id_submitted"] = video_id
        return redirect(url_for("user.video_details"))

    return render_template("users/home_logged_in.html", video_link=video_link)


@blueprint.route("/video_details/", methods=["GET", "POST"])
@login_required
def video_details():
    """
    Render the video details page and handle the form submission for queries.

    Returns:
        A rendered video details page or redirects to the home_logged_in page.
    """
    if not (video_id := session.get("id_submitted")):
        return redirect(url_for("user.home_logged_in"))
    query = None
    answer = None
    search_text = None
    search_results = None
    video_info, text, image, clust, co_graph, time_stamps = process_video_details(
        video_id
    )

    if request.method == "POST":
        logging.info("POST request received")
        try:
            query = request.form["input_text"]
            answer = get_response(text, query)  # noqa
        except Exception as e:  # noqa
            logging.error(e)
        try:
            search_text = request.form["search_text"]
            if search_text:
                search_results = time_stamps[
                    time_stamps["text"].str.contains(
                        search_text, case=False, regex=True
                    )
                ].copy()
                search_results = search_results.to_html(
                    index=False,
                    header=True,
                    escape=False,
                    classes="table table-striped table-hover",
                    justify="left",
                )
                if request.is_xhr:
                    return jsonify(
                        {"search_results": render_template_string(search_results)}
                    )
                else:
                    return render_template(
                        "users/video_details.html",
                        video_info=video_info,
                        transcript=text,
                        query=query,
                        answer=answer,
                        image=image,
                        co_graph=co_graph,
                        clust=clust,
                        time_stamps=time_stamps,
                        search_results=search_results,
                    )
        except Exception as e:  # noqa
            logging.error(e)

    time_stamps = time_stamps.to_html(
        index=False,
        header=True,
        escape=False,
        classes="table table-striped table-hover",
        justify="left",
    )

    return render_template(
        "users/video_details.html",
        video_info=video_info,
        transcript=text,
        query=query,
        answer=answer,
        image=image,
        co_graph=co_graph,
        clust=clust,
        time_stamps=time_stamps,
        search_results=search_results,
    )


def seconds_to_youtube_time(seconds):
    """
    Convert seconds to YouTube timestamp format.

    Args:
        seconds (int): The number of seconds.

    Returns:
        str: The YouTube timestamp string in the format '&t=1h3m30s'.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    youtube_time = "&t="
    if hours > 0:
        youtube_time += f"{hours}h"
    if minutes > 0:
        youtube_time += f"{minutes}m"
    if seconds > 0:
        youtube_time += f"{seconds}s"

    return youtube_time


def create_hyperlink(video_id, start_time, index):
    """
    Create a hyperlink using the YouTube video ID, start time, and an index.

    Args:
        video_id (str): The YouTube video ID.
        start_time (float): The start time in seconds.
        index (int): The index to be used as the link text.

    Returns:
        str: The HTML hyperlink string.
    """
    youtube_time = seconds_to_youtube_time(start_time)
    return f'<a href="https://www.youtube.com/watch?v={video_id}{youtube_time}">{index}</a>'


def process_video_details(video_id):
    """
    Process video details using the given video ID.

    Args:
        video_id (str): The YouTube video ID.

    Returns:
        tuple: A tuple containing video information, transcript, image URL,
        cluster graph, and co-occurrence graph.
    """
    clust = None
    video_info = get_video_info(video_id)  # noqa
    transcript_info = get_and_load_transcripts(video_id, text=False)  # noqa
    text = transcript_info.text
    time_stamps = transcript_info.json_string

    # This is commented out because "include" in Jinja 2 isn't working correctly

    # file = f"/app/riddle_me_this/templates/users/video_networks/{video_id}entity_cluster_graph.html"
    # if not os.path.exists(file):
    #     cluster_visualizer = EntityClusterVisualizer()
    #     cluster_visualizer.run(text, file_name=file)
    # clust = f"/users/video_networks/{video_id}entity_cluster_graph.html"

    file = f"/app/riddle_me_this/templates/users/video_networks/{video_id}co_occurrence_graph.html"
    if not os.path.exists(file):
        co_occurrence_visualizer = CoOccurrenceVisualizer()  # noqa
        co_occurrence_visualizer.run(text, file_name=file)
    co_graph = f"/users/video_networks/{video_id}co_occurrence_graph.html"

    video_info = pd.DataFrame(
        {
            "title": (info := video_info).snippet_title,
            "channel": info.snippet_channel_title,
            "description": info.snippet_description,
            "published": info.snippet_published_at,
            "views": info.statistics_view_count,
            "likes": info.statistics_like_count,
            "comment_count": info.statistics_comment_count,
            "license": info.status_license,
        },
        index=[0],
    ).T.to_html(
        index=True,
        header=False,
        classes="table table-striped table-hover",
        justify="left",
    )
    transcript = pd.DataFrame({"transcript_text": text}, index=[0]).to_html(
        index=False,
        header=True,
        classes="table table-striped table-hover",
        justify="left",
    )
    time_stamps = pd.json_normalize(json.loads(time_stamps))[["text", "start"]]
    time_stamps["start"] = time_stamps["start"].apply(
        lambda x: create_hyperlink(
            video_id,
            x,
            time_stamps.index.get_loc(time_stamps.index[time_stamps["start"] == x][0])
            + 1,  # noqa
        )
    )
    time_stamps = time_stamps.rename(columns={"start": "link"})
    image = info.snippet_thumbnails_maxres_url
    return video_info, transcript, image, clust, co_graph, time_stamps
