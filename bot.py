import os 
import html2text, json, requests, random
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CF_BLOG_API_BASE = 'https://codeforces.com/api/user.blogEntries?handle='
CF_BLOG_BASE = 'https://codeforces.com/blog/entry/'
CF_USER_BASE = 'https://codeforces.com/profile/'
bot = commands.Bot(command_prefix=';')
VALID_DATE_FORMATS = ['%Y', '%m%Y' , '%d%m%Y']

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(
                f'{bot.user.name} is connected to the guild {guild.name}(id: {guild.id})'
        )
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='guilds',help='Display guilds the bot is present in')
async def guild_list(ctx):
    response = discord.Embed(title='List of guilds bot is present in',colour=discord.Colour.from_rgb(255,165,0))
    for guild in bot.guilds:
        response.add_field(name=f'{guild.name}' , value=f'Guild ID : {guild.id}' , inline=False)
    await ctx.send(embed=response)

@bot.command(name='8ball',help='Shake an 8-ball')
async def eight_ball(ctx):
    options_for_8ball = [
        'Surely, you can count on it to happen',
        'Don\'t count on it',
        'I don\'t think do',
        'No.'
    ]
    response = random.choice(options_for_8ball)
    await ctx.send(response)

@bot.command(name='list',help=f'List upto 5 recent blogs of a given handle in a rating/date range \nUsage : {bot.command_prefix}list <handle> [d>=[dd[mm[yyyy]]]] [d<<[dd[mm[yyyy]]]] [r>=rating] [r<<rating]')
async def user_blogs(ctx, handle, *args):
    obj = json.loads(requests.get(CF_BLOG_API_BASE + handle).text)
    lbr , ubr = -3000, 3000
    lbt , ubt = 0 , 10**10
    parameter_check = True
    for arg in args:
        
        if len(arg) < 3:
            parameter_check = False
            response = get_error_embed('Invalid parameters', 'Please enter valid parameters and try again')
            break
        
        else:
            arg_type , arg_val = arg[:3] , arg[3:]
        
        if arg_type in [ 'd<<' , 'd>=' ]:
            timestamp, err = get_time_stamp(arg_val)
            if timestamp is None:
                parameter_check = False
                response = get_error_embed('Invalid parameters', err)
                break
            else:
                if arg_type == 'd>=':
                    lbt = max(lbt , timestamp)
                else:
                    ubt = min(ubt , timestamp)
        elif arg_type in [ 'r<<' , 'r>=' ]:
            rating, err = get_rating_bound(arg_val)
            if rating is None:
                parameter_check = False
                response = get_error_embed('Invalid parameters', err)
                break
            else:
                if arg_type == 'r>=':
                    lbr = max(lbr , rating)
                else:
                    ubr = min(ubr , rating)
        else:
            parameter_check = False
            response = get_error_embed('Invalid parameters', 'Please enter valid parameters and try again')
            break
            
    if obj['status'] == "OK" and parameter_check is True:
        blog_list = [blog for blog in obj['result'] if lbr <= blog['rating'] and blog['rating'] < ubr and lbt <= blog['creationTimeSeconds'] and blog['creationTimeSeconds'] < ubt ]
        response = get_embed(title=f'{handle}\'s recent blog list:', blog_list=blog_list)
    elif parameter_check is True:
        response = get_error_embed(name='CF API Error', value=f"{obj['comment']}")
    await ctx.send(embed=response)

def parse_date_string(date_string, date_format):
    try:
        return datetime.strptime(date_string , date_format)
    except ValueError:
        return None

def get_time_stamp(date_string):
    for date_format in VALID_DATE_FORMATS:
        datetime_object = parse_date_string(date_string, date_format)
        if datetime_object is not None:
            return int(datetime.timestamp(datetime_object)) , None
    return None,'Invalid date format, please select one of the following : {}'.format(" ".join(VALID_DATE_FORMATS))

def get_rating_bound(rating_string):
    try:
        rating = int(rating_string)
        return rating , None
    except ValueError:
        return None, 'Please enter a valid integer in the parameters'

def get_embed(title='List of blogs', blog_list=[]):
    if not blog_list:
        response = get_error_embed(name='Empty list error', value=f'There are no public blogs with specified parameters')
    else:
        response = discord.Embed(title=title,colour=discord.Colour.from_rgb(0,255,0))
        index = 0
        while(index < min(5 , len(blog_list))):
            blog = blog_list[index]
            blog_url = CF_BLOG_BASE + str(blog['id'])
            blog_title = html2text.html2text(blog['title'])
            index = index + 1
            blog_date = datetime.utcfromtimestamp(blog['creationTimeSeconds'])
            date = '/'.join([str(blog_date.day).zfill(2), str(blog_date.month).zfill(2) , str(blog_date.year%100).zfill(2)])
            response.add_field(name=f"{index}. {blog_title}",value=f"Rating = {blog['rating']} \t\t Date:{date} \t\t [Link]({blog_url})",inline=False)
    return response

def get_error_embed(name='Error',value='Something bad happened'):
    response = discord.Embed(title='Error',colour=discord.Colour.from_rgb(255,0,0))
    response.add_field(name=name, value=value)
    return response

bot.run(TOKEN)
