# Net made easy

This is a quickly cobbled together wrapper around [pyenet](https://github.com/aresch/pyenet), which itself wraps the [ENet](https://github.com/lsalzman/enet) C++ library, enabling reliable network communication over UDP.

The goal here was to make it as easy as possible to spin up multiplayer prototypes in Python without having to think about low-level conventions or scalability. Modeled off of the BGT networking engine, if you know anything about that you shouldn't have a proboem. It has been tested and confirmed to work on Linux, Mac OS, and windows.

## Disclaimer

I would love to think this is fast and robust, but the truth is that I ripped it out of a couple Saturday afternoon projects fueled by coffee and discord laughs a couple years ago, so I can't tell you much more than it works and is extremely easy to use. I also can't speak to the overhead that Python introduces here, though it's probably pretty minimal as I was able to roll my own basic and semi low latency multiplayer voice chat functionality. The obvious things have been done to prevent memory leaks, and we aren't keeping references around for any longer than we feasibly have to.

TL;DR: this is not production ready. Please test, and use it at your own risk. If you do decide to use it, please test thoroughly. Do not sue me.

## Usage

```
git clone https://github.com/cartertemm/simplenet.git
pip install -r requirements.txt
```

There's also a setup.py, making it possible to install into your environment, like so

```
git clone https://github.com/cartertemm/simplenet.git
python setup.py install
```

Check the examples folder for things you can do, and the code for how to do more. It's a relatively small .py file so you can do the ugly and copy it between projects.
## Contributing

Contributions are welcomed and encouraged. Hopefully someone somewhere gets some use out of this thing. If a feature isn't working, complain about it in an issue with the understanding that I don't have endless bandwidth for this code, though I will make every effort to review PRs in a timely manner.

Happy hacking!
