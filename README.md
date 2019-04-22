![Banner example for ScriptTaste](imgs/banner.png)

# ScriptTaste

ScriptTaste is small CLI to evaluate someone's preferences and taste from MyAnimeList.

MyAnimeList is a common online platform for individuals to keep track of the various
anime shows they have watched.
This is usually shown in an "anime-list" which lists in alphabetical order all the shows one has based on various tags such as "Completed", "Watching" or "Dropped", which is efficient for bookkeeping but difficult for quickly evaluating one's general taste and preferences.
ScriptTaste provides a quick way to evaluate a MyAnimeList profile by creating a collage with various areas of shows equal to the amount of time invested in watching a particular show.
A collage is then created to compactify to the best ability all animes
so that the user can get a feel for a user's taste/preferences.

Unfortunately due to the nature of the optimization of rectangular packing which is NP-hard.
Final aspect ratios of the collage are a free variable used during the optimization process.
In the future perhaps an extension could use the initial commit here to approximate an area which can then be used as a constraint for the lower bound of area needed to fit in all posters for a landscape portrait with a defined aspect.

# Example

Below is the example of the well known Anime Youtuber [Gigguk](https://www.youtube.com/channel/UC7dF9qfBMXrSlaaFFDvV_Yg) who has the following [MAL account](https://myanimelist.net/profile/gigguk), deprecated as of Aug 22, 2017 at the time of this writing. Please consider supporting him if you enjoy his work. 

![ScriptTaste Anime Collage of user Gigguk](output/gigguk.png)

# Installation

## Manual installation

Simply clone down the repo and test it out with the `Makefile` to get started. 
Requirements needed are outlined in the `requirments.txt` file and added as a `deps` target in the `Makefile`.
For development [`black`](https://github.com/ambv/black) and [`pylint`](https://github.com/PyCQA/pylint) are used.

# Overview

Output of `make help` is

```
help         Display this message.
run          Generate a collage for the well know YouTuber Gigguk.
test         Run testing suite.
clean        Cleans userdata anime lists in repository. Image and metadata is
             preserved.
deps         Install dependencies.
help         Display this message.
```

Output of `python ScriptTaste.py -h`

```
usage: ScriptTaste.py [-h] [-f] [--rate_limit RATE_LIMIT]
                      [--blur_factor BLUR_FACTOR] [--blur_radius BLUR_RADIUS]
                      username

ScriptTaste: A CLI for quickly surveying a MyAnimeList user's taste. Generates
a collage with picture area of shows proportional to time a user has invested
in watching them. This compact representation helps to quickly assess a user's
taste/preferences. Deadspace resulting from the of full space utilization form
rectangular packing is given a diffuse background to make the end result more
aesthetically pleasing.

positional arguments:
  username              MyAnimeList username to generate time proportional
                        collage from.

optional arguments:
  -h, --help            show this help message and exit
  -f                    Force all data to be refreshed and reconstructed.
  --rate_limit RATE_LIMIT
                        Rate limit to sleep between MAL queries. Must be at
                        least 0.1.
  --blur_factor BLUR_FACTOR
                        Number of times to apply a blur filter to diffuse
                        wasted space.
  --blur_radius BLUR_RADIUS
                        Radius of neighbourhood for use as Gaussian blurring
                        parameter.
```

Directory `tree` structure is as follows.
 
```
.
├── Makefile
├── README.md
├── ScriptTaste.py
├── data
│   ├── anime
│   │   ├── ...
│   ├── images
│   │   ├── ...
│   └── users
│       └── gigguk.json
├── imgs
│   └── banner.png
├── output
│   └── gigguk.png
├── requirements.txt
└── src
    ├── __init__.py
    ├── collage.py
    └── url_utils.py
 ```
 
 As a heads up I have included cached instances of `~500` anime metadata and images to 
 1. Help reduce load off MyAnimeList's Servers.
 2. Help the test example of `make run` execute faster.
 
 The additional memory overhead is about `20Mb` for this. With all dependencies installed `make run` should take a little less than a minute for generating the example in the `README.md`.
