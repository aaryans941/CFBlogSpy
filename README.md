# CFBlogSpy
A discord bot to browse [Codeforces](https://codeforces.com/) blogs with desired filters, implemented in python, using [Codeforces API](https://codeforces.com/apiHelp).

## How to run:

Firstly, clone into the repository and navigate to it on your machine


Next, open up a terminal (You might want to create and activate a virtual environment for the same):

```
$ pip install -U requirments.txt
```

Now add your [bot token](https://www.writebots.com/discord-bot-token/) to a new file file in the same directory, named `.env`, in the following format:
(Remember to never make your bot token public)

```
DISCORD_TOKEN=<insert-token-here>
```

You can now run the bot.

Note: You may replace `python3.8` with the version you want to use (depending on other compatibilities):

```
$ python3.8 bot.py
```

You should get a message in your terminal saying it has successfully connected to discord (and possibly some guilds) to confirm the sane.

You're all set!

