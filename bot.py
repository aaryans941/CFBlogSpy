import os, json, requests, discord, random
from dotenv import load_dotenv
from discord.ext import commands
from utils import tag_matches, parse_date_string, get_time_stamp, get_rating_bound, get_blog_embed, get_error_embed  
from constants import CF_BLOG_API_BASE, CF_USER_INFO_BASE
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=';')
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

@bot.command(name='list',help=f'List upto 5 recent blogs of a given handle in a rating/date range',
                usage='handle [d>=[dd[mm[yyyy]]]] [d<<[dd[mm[yyyy]]]] [r>=rating] [r<<rating] [+tags...]')
async def user_blogs(ctx, handle, *args):
    obj = json.loads(requests.get(CF_BLOG_API_BASE + handle).text)
    usr = json.loads(requests.get(CF_USER_INFO_BASE + handle).text)
    lbr , ubr = -3000, 3000
    lbt , ubt = 0 , 10**10
    tags = []
    parameter_check = True

    for arg in args:
        
        if len(arg) >= 3 and arg[:3] in [ 'd<<' , 'd>=' ]:
            arg_type, arg_val = arg[:3], arg[3:]
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
       
        elif len(arg) >= 3 and arg[:3] in [ 'r<<' , 'r>=' ]:
            arg_type, arg_val = arg[:3], arg[3:]
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
       
        elif arg[:1] == '+':
            arg_val = arg[1:]
            tags.append(arg_val)
       
        else:
            parameter_check = False
            response = get_error_embed('Invalid parameters', 'Please enter valid parameters and try again')
            break
            
    if obj['status'] == "OK" and parameter_check is True:
        blog_list = [blog for blog in obj['result'] 
                if lbr <= blog['rating'] and blog['rating'] < ubr 
                and lbt <= blog['creationTimeSeconds'] and blog['creationTimeSeconds'] < ubt 
                and tag_matches(blog , tags)]
        response = get_blog_embed(title=f'{handle}\'s recent blog list:', blog_list=blog_list)
        user_info = usr['result'][0]    
        user_image_url = 'https:' + user_info['titlePhoto']
        response.set_thumbnail(url=user_image_url)
    elif parameter_check is True:
        response = get_error_embed(name='CF API Error', value=f"{obj['comment']}")
    await ctx.send(embed=response)

@bot.command(name='gimme', help='Displays a random problem of a given tag within a rating range.', usage='tag [lower [upper]]')
async def user_contest(ctx, tag, *args):
    tag = tag.replace('-', '%20')
    url = f'{CF_PROBLEM_TAGS}{tag}'
    obj = requests.get(url)
    data = json.loads(obj.text)
    if data['status'] == "FAILED":
        await ctx.send(f'{data["comment"]}')
        return
    elif len(data['result']['problems']) == 0:
        await ctx.send(f'{tag} is not a valid tag on Codeforces.')
        return

    rat_lb, rat_ub = 0, 5000
    var = 0
    for arg in args :
        if var == 2 :
            await ctx.send('There should be at most two integers specifying the rating range.')
            return
        if utils.isValidInteger(arg) == False :
            await ctx.send('The rating range should be in integer format only.')
            return
        arg = utils.isValidInteger(arg)
        var = var + 1
        if var == 1 :
            rat_lb = max(rat_lb, arg)
        if var == 2 :
            rat_ub = min(rat_ub, arg)

    problems = []
    for prob in data['result']['problems'] :
        if 'rating' not in prob:
            continue
        else :
            if prob['rating'] >= rat_lb and prob['rating'] <= rat_ub :
                problems.append(prob)

    if len(problems) == 0 :
        await ctx.send('No problem fit within your given rating range.')
        return

    rand_prob = random.choice(problems)

    url = f'https://codeforces.com/api/contest.standings?contestId={rand_prob["contestId"]}&from=1&count=1&showUnofficial=true'
    obj = requests.get(url)
    data = json.loads(obj.text)
    name = data['result']['contest']['name']
    url = f'https://codeforces.com/contest/{rand_prob["contestId"]}/problem/{rand_prob["index"]}'

    embed = discord.Embed(description=f'[{rand_prob["contestId"]}{rand_prob["index"]}. {rand_prob["name"]}]({url})', color=0x000000)
    embed.add_field(name=f'{name}', value=f'Rating : {rand_prob["rating"]}', inline=False)   
    await ctx.channel.send(embed=embed)

bot.run(TOKEN)
