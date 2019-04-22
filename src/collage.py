#!/usr/bin/env python3
"""
Module devoted to the artistic rendering/visualization of images.
"""
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFilter
import rpack

from src.url_utils import IMGDIR, ANIMEDIR

OUTPUTDIR = "output"


def parse_duration(duration):
    """
    Parses duration field from MyAnimeList.

    Arguments:
        duration: str
            Duration as written for an anime property on MyAnimeList.

    Returns:
        time: int
            Time to watch in minutes
    """
    time = 0
    for scale, unit in ((60, "hr"), (1, "min")):
        substring = re.search(r"(\d+) {unit}".format(unit=unit), duration)
        if substring:
            time += scale * int(substring.group(1))

    return time


def read_time_poster_data(user_animes):
    """
    Pairs time invested with poster for a list of animes.

    Arguments:
        user_animes: list(dict)
            Metadata regarding MAL anime shows.

    Returns:
        time_posters: tuple(int, PIL.Image)
            Time in minutes for a given anime paired with corresponding poster.
    """
    time_invested = []
    for anime in user_animes:
        if anime["watched_episodes"] == 0:
            continue

        fpath = os.path.join(ANIMEDIR, str(anime["mal_id"])) + ".json"
        try:
            with open(fpath, "r") as fptr:
                metadata = json.load(fptr)
        except FileNotFoundError:
            print(f"Skipping due to unfound metadata file for: {anime['title']}")
            continue

        fpath = os.path.join(IMGDIR, str(anime["mal_id"])) + ".jpg"
        try:
            img = Image.open(fpath)
        except FileNotFoundError:
            print(f"Skipping due to unfound image file for: {anime['title']}")
            continue

        duration_in_minutes = parse_duration(metadata["duration"])
        total_time = duration_in_minutes * int(anime["watched_episodes"])

        time_invested.append((total_time, img))

    return time_invested


def normalize_posters(time_posters):
    """
    Normalizes time poster data.

    Time is normalized by the maximum time observed. Posters are normalized to the
    maximum amount of area observed. Note ratios are not guaranteed to be constant
    for posters.

    Note when a rectangle area is scaled by a factor 'a' the side lengths must be
    scaled as

        a(hw) = (t h)(t w) => t = sqrt(a)

    where t is the length each size is rescaled by. Thus to resize an image by an area
    scaler while maintaining the aspect ratio one must resize based on the square root
    of the area scalar of one side and derive the rest from that quantity.

    Arguments:
        time_posters: tuple(int, PIL.Image)
            Time in minutes for a given anime paired with corresponding poster.

    Returns:
        norm_time_posters: tuple(float, PIL.Image)
            Normalized instances of time and area for time and posters respectively.
    """

    # time_posters = sorted(time_posters, key=lambda x: x[0], reverse=True)
    max_time = max(x for x, _ in time_posters)
    max_area = max(x.size[0] * x.size[1] for _, x in time_posters)

    normalized_posters = []
    for time, img in time_posters:
        area_norm_ratio = max_area / (img.size[0] * img.size[1])
        time_norm_ratio = time / max_time
        ratio = area_norm_ratio * time_norm_ratio

        img = resize_width_w_constant_aspect(ratio, img)

        if img:
            normalized_posters.append(img)

    return normalized_posters


def resize_width_w_constant_aspect(ratio, img):
    """
    Resizes an image by a change of width while maintaining aspect ratio.

    Arguments:
        ratio: float
            Ratio to resize width by
        img: PIL.Image
            Image to be resized

    Returns:
        img: PIL.Image | None
            Resized Image or None if integer resolution is to small to create a finite
            area.
    """
    width = np.sqrt(ratio) * img.size[0]
    height = width * img.size[0] / img.size[1]

    if height >= 1 and width >= 1:
        return img.resize(map(int, (height, width)), Image.ANTIALIAS)

    return None


def arrange_images(normalized_posters, blur_factor, blur_radius):
    """
    Arranges images to create a collage.

    Arguments:
        norm_time_posters: tuple(float, PIL.Image)
            Normalized instances of time and area for time and posters respectively.
        blur_factor:
            Number of times to apply a blurring operation to diffuse wasted space.
        blur_radius:
            Radius of neighbourhood for use as Gaussian blurring parameter.

    Returns:
        collage: np.array
            A collage of images heuristically packed together.
    """

    # as a greedy heuristic sort by size first to minimize wasted area
    normalized_posters = sorted(
        normalized_posters, key=lambda x: x.size[0] * x.size[1], reverse=True
    )
    sizes = [x.size for x in normalized_posters]
    positions = rpack.pack(sizes)

    max_width = max(a[0] + b[0] for a, b in zip(positions, sizes))
    max_height = max(a[1] + b[1] for a, b in zip(positions, sizes))
    collage = np.full([max_height + 1, max_width + 1, 3], 255, dtype=np.uint8)
    deadspace = np.full_like(collage, True)

    # place images
    for (x, y), img in zip(positions, normalized_posters):
        dx, dy = img.size
        collage[y : y + dy, x : x + dx] = img
        deadspace[y : y + dy, x : x + dx] = False

    # identify all deadspace which looks harsh on the eyes
    deadspace = np.where(deadspace)

    # diffuse deadspace to get a softer background
    gaussian_blur = ImageFilter.GaussianBlur(radius=blur_radius)
    for _ in range(blur_factor):
        blurred = Image.fromarray(collage).filter(gaussian_blur)
        collage[deadspace] = np.array(blurred)[deadspace]

    return collage


def draw(user_animes, username, blur_factor, blur_radius):
    """
    Draws a collage of posters proportional in size to time spent thus far watching.

    Arguments:
        user_animes: list(dict)
            Metadata regarding MAL anime shows.
        username:
            MyAnimeList username to query for list of episodes watched of anime.
        blur_factor:
            Number of times to apply a blurring operation to diffuse wasted space.
        blur_radius:
            Radius of neighbourhood for use as Gaussian blurring parameter.
    """
    time_posters = read_time_poster_data(user_animes)
    normalized_posters = normalize_posters(time_posters)

    print("Generating final image this may take a while.")
    img = arrange_images(normalized_posters, blur_factor, blur_radius)

    fpath = os.path.join(OUTPUTDIR, username + ".png")
    plt.imsave(fpath, img)
