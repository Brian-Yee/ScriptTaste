#!/usr/bin/env python3
# pylint: disable=pointless-string-statement
"""
ScriptTaste is small CLI to visually evaluate someone's taste in shows from MyAnimeList.

MyAnimeList is a common online platform for individuals to keep track of the various
anime shows they have watched. This is usually shown in an "anime-list" which lists in
alphabetical order all the shows one has based on various tags such as "Completed",
"Watching" or "Dropped", which is efficient for bookkeeping but difficult for quickly
evaluating one's general taste and preferences.

ScriptTaste provides a quick way to evaluate a MyAnimeList profile by creating a collage
with various areas of shows equal to the amount of time invested in watching a
particular show. A collage is then created to compactify to the best ability all animes
so that the user can get a feel for a user's taste/preferences.
"""
import argparse
import jikanpy

import src.url_utils
import src.collage

BOLD, RED, GREEN, END = ("\033[{x}m".format(x=x) for x in (1, 91, 32, 0))


def main(username, force, rate_limit, blur_factor, blur_radius):
    """
    Main function module for ScriptTaste.

    Arguments:
        username:
            MyAnimeList username to query for list of episodes watched of anime.
        force:
            Forces data to be repulled from MyAnimeList even if a cached version exists.
        rate_limit: float
            Rate limit to sleep between MAL queries.
        blur_factor:
            Number of times to apply a blurring operation to diffuse wasted space.
        blur_radius:
            Radius of neighbourhood for use as Gaussian blurring parameter.
    """
    jikan = jikanpy.Jikan()

    try:
        user_animes = src.url_utils.fetch_user_animes(jikan, username, force)
    except jikanpy.exceptions.APIException as err:
        if err.args[0].split(" ", 1)[0] == "400":
            print(RED + "Username not found, was it typed correctly?" + END)
            exit(0)

        raise err

    try:
        src.url_utils.fetch_images(user_animes, force, rate_limit)
        src.url_utils.fetch_anime_metadata(jikan, user_animes, force, rate_limit)
    except jikanpy.exceptions.APIException as err:
        code = err.args[0].split(" ", 1)[0]
        if code == "429":
            print(
                RED
                + "Rate limit exceeded!"
                + "\nNo worries, data up to this point has been cached."
                + "\nSimply wait a bit and try again."
                + END
            )
            exit(0)
        elif code == "400":
            print(
                RED
                + "Failure to connect with API, this behaviour is unexpected."
                + "\nUser may need to debug on their end. If Resolved please"
                + "\nsubmit a PR to help others in the future."
                + END
            )

        raise err

    src.collage.draw(user_animes, username, blur_factor, blur_radius)


def parse_arguments():
    """
    Main CLI for interfacing with ScriptTaste.

    Returns:
        argparse.Namespace
            Argparse namespace containg CLI inputs.

    """
    parser = argparse.ArgumentParser(
        description=(
            "ScriptTaste: A CLI for quickly surveying a MyAnimeList user's taste."
            " Generates a collage with picture area of shows proportional to time a user"
            " has invested in watching them. This compact representation helps to"
            " quickly assess a user's taste/preferences. Deadspace resulting from the"
            " of full space utilization form rectangular packing is given a diffuse"
            " background to make the end result more aesthetically pleasing."
        )
    )

    parser.add_argument(
        "username",
        type=str,
        help="MyAnimeList username to generate time proportional collage from.",
    )

    parser.add_argument(
        "-f",
        dest="force",
        action="store_true",
        help="Force all data to be refreshed and reconstructed.",
    )

    parser.add_argument(
        "--rate_limit",
        default=1,
        type=float,
        dest="rate_limit",
        help="Rate limit to sleep between MAL queries. Must be at least 0.1.",
    )

    parser.add_argument(
        "--blur_factor",
        default=100,
        type=int,
        dest="blur_factor",
        help="Number of times to apply a blur filter to diffuse wasted space.",
    )

    parser.add_argument(
        "--blur_radius",
        default=5,
        type=int,
        dest="blur_radius",
        help="Radius of neighbourhood for use as Gaussian blurring parameter.",
    )

    return parser.parse_args()


def assert_argument_vals(args):
    """
    Various asserts to enforce CLI arguments passed are valid.

    Arguments:
        args: argparse.Namespace
            Argparse namespace containg CLI inputs.
    """
    assert (
        args.rate_limit >= 0.1
    ), "Please play nice and rate limit queries to at least 0.1 seconds."


if __name__ == "__main__":
    """
    CLI for parsing and validating values passed to ScriptTaste.
    """
    ARGS = parse_arguments()

    assert_argument_vals(ARGS)

    main(ARGS.username, ARGS.force, ARGS.rate_limit, ARGS.blur_factor, ARGS.blur_radius)
