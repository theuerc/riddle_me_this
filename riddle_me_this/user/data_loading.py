"""Loads the data from services.py and stores it in the database."""

import json
import re

import pandas as pd
import torch

from riddle_me_this.user.models import Video, Transcript


def split_text(text, chunks_size=2000):
    """
    Splits the input text into smaller chunks of maximum length `chunks_size`.

    Parameters:
    -----------
    text : str
        The text to be split.
    chunks_size : int, optional
        The maximum length of each chunk. Default is 2000.

    Returns:
    --------
    texts : list of str
        The list of smaller text chunks.
    """
    texts = []
    while len(text.split()) > chunks_size:
        texts.append(" ".join(text.split()[:chunks_size]))
        text = " ".join(text.split()[chunks_size:])
    texts.append(text) if text else None
    return texts


def add_punctuation(text):
    """
    Adds punctuation a string using the silero_te model.

    Parameters:
    -----------
    text : str
        The text to which punctuation needs to be added.

    Returns:
    --------
    text_with_punctuation : str
        The input text with added punctuation.
    """
    torch.backends.quantized.engine = 'qnnpack'
    model, example_texts, languages, punct, apply_te = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                      model='silero_te', trust_repo=True)
    return apply_te(text, lan='en').replace('[UNK]', '').replace('NK]', '')


def load_transcripts(video_id, transcripts):
    """
    Loads the transcripts of a video into the database.

    Parameters:
    -----------
    video_id : str
        The ID of the video.
    transcripts : list of dict
        A list of dictionaries, where each dictionary contains the transcript of a part of the video.

    Returns:
    --------
    None
    """
    df = pd.DataFrame((k := transcripts), index=range(len(k)))
    df['text'] = df['transcript'].apply(lambda x: ' '.join([i['text'] for i in x]))
    df['video_id'] = video_id
    df = df[df['text'].str.strip() != ""]
    df.loc[df['is_generated'], 'text'] = df[df['is_generated']].apply(
        lambda row: add_punctuation(re.sub(r'[^a-zA-Z0-9\s]+', 'X', row['text'])), axis=1)

    for index, row in df.iterrows():
        video_id = row['video_id']
        json_string = row['transcript']
        text = row['text']
        language_code = row['language_code']
        is_generated = row['is_generated']

        Transcript.create(
            video_id=video_id,
            json_string=json.dumps(row['transcript']),
            text=text,
            language_code=language_code,
            is_generated=is_generated,
        )


def load_video_info(data):
    """
    Loads the video information into the database.

    Parameters:
    -----------
    data : dict
        A dictionary containing the video information.

    Returns:
    --------
    None
    """
    Video.create(
        video_id=data['items'][0]['id'],
        snippet_published_at=pd.to_datetime(data['items'][0]['snippet']['publishedAt']),
        snippet_channel_id=data['items'][0]['snippet']['channelId'],
        snippet_title=data['items'][0]['snippet']['title'],
        snippet_description=data['items'][0]['snippet']['description'],
        snippet_channel_title=data['items'][0]['snippet']['channelTitle'],
        snippet_category_id=data['items'][0]['snippet']['categoryId'],
        snippet_thumbnails_maxres_url=data['items'][0]['snippet']['thumbnails']['maxres']['url'],
        content_details_definition=data['items'][0]['contentDetails']['definition'],
        content_details_licensed_content=data['items'][0]['contentDetails']['licensedContent'],
        status_upload_status=data['items'][0]['status']['uploadStatus'],
        status_privacy_status=data['items'][0]['status']['privacyStatus'],
        status_license=data['items'][0]['status']['license'],
        status_public_stats_viewable=data['items'][0]['status']['publicStatsViewable'],
        status_made_for_kids=data['items'][0]['status']['madeForKids'],
        statistics_view_count=data['items'][0]['statistics']['viewCount'],
        statistics_like_count=data['items'][0]['statistics']['likeCount'],
        statistics_favorite_count=data['items'][0]['statistics']['favoriteCount'],
        statistics_comment_count=data['items'][0]['statistics']['commentCount']
    )
