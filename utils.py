import html2text, discord, requests
from constants import VALID_DATE_FORMATS, CF_BLOG_BASE, CF_USER_BASE
from datetime import datetime

def tag_matches(blog, query_tags):
    #If every query tag is a substring of any problem tag
    for query_tag in query_tags:
        curmatch = [tag for tag in blog['tags'] if query_tag in tag]
        if not curmatch:
            return False
    return True

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

def get_blog_embed(title='List of blogs', blog_list=[]):
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
