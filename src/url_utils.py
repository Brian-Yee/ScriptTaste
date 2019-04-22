#!/usr/bin/env python3
"""
Module dedicated to interfacing with the jikan API.
"""
import os
import json
import time
import urllib.request

USERDIR = "data/users"
IMGDIR = "data/images"
ANIMEDIR = "data/anime"


def fetch_user_animes(jikan, username, force):
    """
    Queries and saves anime-list data associated with MAL username.

    Arguments:
        jikan: ikanpy.jikan.Jikan
            JikanPy API Object.
        username: str
            MyAnimeList username to query for list of episodes watched of anime.
        force: bool
            Forces data to be queried from MyAnimeList even if a cached version exists.

    Returns:
        user_animes: list(dict)
            Metadata regarding MAL anime shows.
    """
    user_fpath = os.path.join(USERDIR, f"{username}.json")
    cache_exists = os.path.exists(user_fpath) and os.path.isfile(user_fpath)

    if force or not cache_exists:
        print(f"Pulling userdata for {username}")
        userdata = jikan.user(username=username, request="animelist")
        user_animes = userdata["anime"]

        print(f"Caching at:\n\t{user_fpath}")
        with open(user_fpath, "w") as fptr:
            json.dump(user_animes, fptr)
    else:
        print(f"Using cached data located at:\n\t{user_fpath}")
        with open(user_fpath, "r") as fptr:
            user_animes = json.load(fptr)

    return user_animes


def fetch_images(user_animes, force, rate_limit):
    """
    Queries and saves images associated with MAL username's watchlist.

    Arguments:
        user_animes: list(dict)
            Metadata regarding MAL anime shows.
        force: bool
            Forces data to be queried from MyAnimeList even if a cached version exists.
        rate_limit: float
            Rate limit to sleep between MAL queries.
    """
    for anime in user_animes:
        img_fpath = os.path.join(IMGDIR, f"{anime['mal_id']}.jpg")
        cache_exists = os.path.exists(img_fpath) and os.path.isfile(img_fpath)
        if force or not cache_exists:
            print(f"Saving image for: {anime['title']}")
            urllib.request.urlretrieve(anime["image_url"], img_fpath)
            time.sleep(rate_limit)
        else:
            print(f"Skipping already cached image for: {anime['title']}")


def fetch_anime_metadata(jikan, user_animes, force, rate_limit):
    """
    Queries and saves anime metadata associated with MAL username.

    Arguments:
        jikan: ikanpy.jikan.Jikan
            JikanPy API Object.
        user_animes: list(dict)
            Metadata regarding MAL anime shows.
        force: bool
            Forces data to be queried from MyAnimeList even if a cached version exists.
        rate_limit: float
            Rate limit to sleep between MAL queries.
    """
    for anime in user_animes:
        metadata_fpath = os.path.join(ANIMEDIR, f"{anime['mal_id']}.json")
        cache_exists = os.path.exists(metadata_fpath) and os.path.isfile(metadata_fpath)
        if force or not cache_exists:
            print(f"Saving metadata for: {anime['title']}")
            anime_metadata = jikan.anime(anime["mal_id"])
            with open(metadata_fpath, "w") as fptr:
                json.dump(anime_metadata, fptr)
            time.sleep(rate_limit)
        else:
            print(f"Skipping already cached metadata for: {anime['title']}")
