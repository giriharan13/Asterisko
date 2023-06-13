import discord
import requests, json, os, glob, time
from bs4 import BeautifulSoup
from googlesearch import search
from requests_html import HTMLSession
from pytube import YouTube
from discord.ext import commands
from discord import FFmpegPCMAudio
#from discord-components import Button, DiscordComponents
from tabulate import tabulate
import asyncio


tabulate.PRESERVE_WHITESPACE = False
#from discord_slash.utils.manage_components import create_button, create_actionrow
#from discord_slash.model import ButtonStyle
path = str(os.getcwd())+ '\\asterisko'
os.chdir(path)  # changing the current working directory to Asterisko folder next to the py file
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

dict_data = {}
def task_sheet(users, dict_list, Tasks):
    list_summary = [[":red_circle: \t\t\t\t :thumbsdown: " for i in range(len(users))] for j in range(len(Tasks))]
    for i in range(len(users)):
        for j in range(len(dict_list)):
            if users[i] == dict_list[j][0]:
                for k in range(len(Tasks)):
                    ti = Tasks.index((dict_list[j][1])[:-1])
                    if (dict_list[j][1])[-1] == "T":
                        list_summary[ti][i] = ":green_circle: \t\t\t\t :thumbsup: "
                    if (dict_list[j][1])[-1] == "F":
                        list_summary[ti][i] = ":red_circle: \t\t\t\t :thumbsdown: "
    return list_summary


def prettifystr(string):
    n = 0
    for i in range(20):
       string = string.replace(f'[{n}]', '')
       n+=1
    return string


def weather_scrape(city):
    city = city.replace(" ", "+")
    res = requests.get(
        f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8', headers=headers)
    print("Searching...\n")
    soup = BeautifulSoup(res.text, 'html.parser')
    location = soup.select('#wob_loc')[0].getText().strip()
    time = soup.select('#wob_dts')[0].getText().strip()
    info = soup.select('#wob_dc')[0].getText().strip()
    weather = soup.select('#wob_tm')[0].getText().strip()
    weather2 = soup.select('#wob_ttm')[0].getText().strip()
    precip = soup.select('#wob_pp')[0].getText().strip()
    humidity = soup.select('#wob_hm')[0].getText().strip()
    wind = soup.select('#wob_ws')[0].getText().strip()
    wind2 = soup.select('#wob_tws')[0].getText().strip()
    return (('location: '+location), ('Time:'+time), ('Info: '+ info), ('Weather: '+(weather+"°C")+'   '+(weather2+"°F")), ('Precipitation: '+precip), ('Humidity: '+humidity), ('Wind: '+wind+'  '+wind2))


def is_flo(n):
    try:
        n = float(n)
        if isinstance(n, float):
            return True
        else:
            return False
    except ValueError:
        return False


def is_int(n):
    try:
        n = int(n)
        if isinstance(n, int):
            return True
        else:
            return False
    except ValueError:
        return False


def is_float_or_int(n):
    if is_int(n) and is_flo(n):
        return True
    else:
        return False 


def get_nickname():
    s = HTMLSession()
    x = s.get("https://blog.reedsy.com/character-name-generator/mythology/greek-mythology/")
    soup = BeautifulSoup(x.text, 'lxml')
    text = 'You can choose a nickname below: \n'
    text += str((soup.find_all('h3'))[0].text)
    for i in (soup.find_all('h3'))[1:5]:
        text += ', '
        text += str(i.text)
    return text


def download_yt_mp3(name):
    name = name.replace(' ', '+')
    url = 'https://www.youtube.com/results?search_query=' + name
    # s = HTMLSession()
    x = requests.get(url)
    soup = str(BeautifulSoup(x.text, 'lxml'))
    ind = soup.find('videoId')
    print("url found ", 'https://www.youtube.com/watch?v=' + (soup[(soup.find('videoId'))+10: (soup.find('videoId'))+21]))
    yt_url = YouTube('https://www.youtube.com/watch?v=' + (soup[(soup.find('videoId'))+10: (soup.find('videoId'))+21]))
    audio = yt_url.streams.filter(only_audio=True).first()
    file1 = audio.download(output_path=os.getcwd())
    print("file downloaded")
    base, ext = os.path.splitext(file1)
    file2 = base + '.mp3'
    if os.path.exists(file2):
        os.remove(file1)
    if os.path.exists(file1):
        os.rename(file1, file2)
    return str(file2)


intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='*',intents=intents)
#DiscordComponents(client)

@client.event
async def on_ready():
    print(f'we have logged in as {client.user}')


@client.command(pass_context=True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send(f'{client.user} joined the voice channel')
    else:
        await ctx.send("You're not in a voice channel")


@client.command(pass_context=True)
async def play(ctx, *songname):
    song_name = ''
    for i in songname:
        song_name += i
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)  
    if voice and voice.is_playing():
        voice.stop()
    if not voice:
        if not ctx.author.voice:
            await ctx.send("Join a voice channel")
        else:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
    time.sleep(0.5)
    files = glob.glob('*.mp3')
    for f in files:
        print("removing", f)
        os.remove(f)
    if ctx.author.voice:
        mp3 = str(download_yt_mp3(song_name))
        files = glob.glob('*.mp3')
        for f in files:
            await ctx.send("Playing "+ str(f[:-4]))
        source = FFmpegPCMAudio(mp3)
        player = voice.play(source)
    else:
        await ctx.send("You're not in a voice channel")


@client.command(pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    else:
        await ctx.send("No audio is being played right now")


@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Audio is paused")
    else:
        await ctx.send("No audio is being played right now")

    
@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send("Audio is resumed")
    elif voice.is_playing:
        await ctx.send("Audio could not be resumed")
        

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left")
    else:
        await ctx.send("I'm not in there")


l = []
@client.command(pass_context=True)
async def queue(ctx, *args):
    song_name = ''
    for i in args:
        song_name += i
    mp3 = str(download_yt_mp3(song_name))
    l.append(mp3)
    mp3 = mp3[:-4]
    for sym in range(-1, -len(mp3)-1, -1):
        if mp3[sym] == '\\':
            index = sym
            break
    await ctx.send("Queued "+ str(mp3)[sym+1::])


@client.command(pass_context=True)
async def qplay(ctx, args):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)  
    if voice and voice.is_playing():
        voice.stop()
    if not voice:
        if not ctx.author.voice:
            await ctx.send("Join a voice channel")
        else:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            
    if args == 'all':
        if ctx.author.voice:
            a = 0
            while True:
                print("queue loop running")
                upd = len(l)
                if voice.is_playing():
                    await asyncio.sleep(10)
                    if a == upd:
                        await ctx.send("--QUEUE FINISHED--")
                        break
                else:
                    source = FFmpegPCMAudio(l[a])
                    player = voice.play(source)
                    print(a)
                    for sym in range(-1, -len(l[a])-1, -1):
                        if l[a][sym] == '\\':
                            index = sym
                            break
                    i = l[a][sym+1::]
                    await ctx.send("Playing "+ str(i[:-4]))
                    a+=1
                        

@client.command(pass_context=True)
async def displayq(ctx):
    await ctx.send("------MUSIC QUEUE------")
    for i in range(len(l)):
        for sym in range(-1, -len(l[i])-1, -1):
            if l[i][sym] == '\\':
                index = sym
                break
        nam = l[i][sym+1::]
        await ctx.send(str(i+1)+'. '+nam[:-4])


@client.command(pass_context=True)
async def delq(ctx, arg):
    global l
    if arg == 'all':
        await ctx.send("-QUEUE DELETED-")
        l = []
    else:
        arg = int(arg)
        for sym in range(-1, -len(l[arg-1])-1, -1):
            if l[arg-1][sym] == '\\':
                index = sym
                break
        nam = l[arg-1][sym+1::]
        await ctx.send(str(arg)+'. '+nam[:-4]+' deleted')
        del l[arg-1]


@client.command(pass_context=True)
async def calc(ctx, *expression):
    exp = ''
    for i in expression:
        exp += i
    exp1 = ''
    for i in range(len(exp)):
        print(exp[i])
        if exp[i] == '^':
            exp1 += '**'
        if exp[i] == 'x':
            exp1 += '*'
        else:
            if i == 0:
                pass
            else:
                if (exp[i]=='(') and (is_float_or_int(exp[i-1])):
                    exp1 += '*'
            exp1 += exp[i]
            try:
                if (exp[i]==')') and ((is_float_or_int(exp[i+1])) or exp[i+1] == '('):
                    exp1 += '*'
            except IndexError:
                pass
    print("calc", exp1)
    try:
        cal = eval(exp1)
        await ctx.send(cal)
    except:
        await ctx.send("Type a valid expression")

 
@client.command(pass_context=True)
async def q(ctx, *args):
    s = ''
    for i in args:
        s += i
        s += ' '
    s += ' wikipedia'
    result = search(s)
    top_res = None;
    for i in result: # cannot result[0] because its a generator
        top_res = i
        break
    req = (requests.get(top_res)).text
    soup = BeautifulSoup(req , 'lxml')
    info = soup.find_all('p')
    await ctx.send(prettifystr(info[1].text + info[2].text), tts=True)

@client.command(pass_context=True)
async def gif(ctx, *args):
    s = ''
    for i in args:
        s += i
        s += ' '
    website = f'https://giphy.com/search/{s}'
    req = requests.get(website).text
    soup = BeautifulSoup(req, 'lxml')
    jsonscript = soup.find_all('script')[13].string.strip()[123:10349 + 123]
    data = json.loads(jsonscript)
    print(data)
    gifurl = data['images']
    gif = gifurl['original']['mp4']
    chunksize = 256
    r = requests.get(gif, stream=True)
    with open('discordresponse.gif', 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunksize):
            f.write(chunk)
    await ctx.send(' ',file=discord.File(path + '\\discordresponse.gif'))


@client.command(pass_context=True)
async def weather(ctx, *place):
    s = ''
    for i in place:
        s += i
        s += ' '
    city = s+"weather"
    inf = weather_scrape(city)
    city = ''
    for i in inf:
        city+=i
        city+='\n'
    await ctx.send(city, tts=True)


@client.command(pass_context=True)
async def nickname(ctx):
    await ctx.send(get_nickname(), tts=True)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await client.process_commands(message)

@client.command()
async def tftadd(ctx,*args):
     tasks = [x for x in args]
     topic = tasks[0]
     total_tasks = len(tasks)
     task_added = 0
     embed=discord.Embed(title="Tasks For Today(TFT)", url="https://c.tenor.com/FkNMgm4kNrsAAAAC/all-the-best.gif",
                         description=topic, color=discord.Color.green())
     buttons = [create_button(style=ButtonStyle.green,label="DONE"),]
     action_row = create_actionrow(*buttons)
     for i in range(1,total_tasks):
        task_added += 1
        embed.add_field(name=f'task {task_added}', value= tasks[i],inline=False)
     await ctx.send(embed=embed,components=[action_row])



@commands.Cog.listener()
async def on_reaction_add(self,reaction,user):
    if reaction == '👍':
        await channel.send('Please select what task you have completed')
    await channel.send('Congratulations')

    
msg_with_buttons = 0
@client.command()
async def t(ctx, *args):
    global dict_data
    task_string = ""
    for i in args:
        task_string += str(i)
    Tasks = task_string.split(",")
    Users = []
    dict_summary = []
    dict_data[str(Tasks[0])] = {}
    
    embed=discord.Embed(title="Tasks", url="https://c.tenor.com/FkNMgm4kNrsAAAAC/all-the-best.gif",
                         description=Tasks[0], color=discord.Color.green())
    for i in range(1,len(Tasks)):
        embed.add_field(name=f'task {i}', value= Tasks[i],inline=False)
    
    buttons = [
        [Button(style="3", label=i, custom_id=i+"T"),
        Button(style="4", label=i, custom_id=i+"F")] for i in Tasks[1:]]
    
    msg_with_buttons = await ctx.send(embed=embed,components=buttons)
    
    dict_data[Tasks[0]]['Tasks'] = Tasks
    dict_data[Tasks[0]]['msg'] = msg_with_buttons
    dict_data[Tasks[0]]['Users'] = []
    dict_data[Tasks[0]]['dict_summary'] = []
    dict_data[Tasks[0]]['Tasks'] = Tasks[1:]
    
    

@client.command()
async def stats(ctx):
    for args in dict_data.keys():
        head = []
        body = []
        Users = dict_data[args]['Users']
        dict_summary = dict_data[args]['dict_summary']
        Tasks = dict_data[args]['Tasks']
        summary = task_sheet(Users, dict_summary, Tasks)
        head.append(args)
        for i in range(len(Users)):
            head.append(Users[i])
        for i in range(len(Tasks)):
            body.append([])
            body[i].append(Tasks[i])
            for j in range(len(Users)):
                body[i].append(summary[i][j])
        await ctx.send(tabulate(body, headers=head, tablefmt="orgtbl"))
        '''print_string = args
        for i in range(len(Users)):
            print_string += Users[i]
        print_string += "\n"
        for i in range(len(Tasks)):
            print_string += "|"+ "-"*int((len(args)/2)-(0)) + (Tasks[i])+ "-"*int((len(args)/2)-(0))
            for j in range(len(Users)):
                if j == 0:
                    print_string+= "|"+ "-"*int((len(Users[j])/2)-(0)) + str(summary[i][j]) + "-"*int((len(Users[j])/2)-(0)) +"|"
                else:
                    print_string+= "-"*int((len(Users[j])/2)-(0)) + str(summary[i][j]) + "-"*int((len(Users[j])/2)-(0)) +"|
                    "
            print_string += "\n"'''
        #await ctx.send(str(print_string))

def True_False(mess, lis):
    val = False
    for i in lis.keys():
        if mess == lis[i]['msg']:
            val = True
    return val
@client.event
async def on_message(message):
    await client.process_commands(message)
    global dict_data
    global task_completed
    print(dict_data)
    keys = 0
    def check_button(i):
        global keys
        for k in dict_data.keys():
            if i.message == dict_data[k]['msg']:
                au = str(i.author)
                af = str(i.custom_id)
                dict_data[k]['last_author'] = au
                dict_data[k]['last_cusid'] = af
                keys = k
                if str(i.author) not in dict_data[k]['Users']:
                    dict_data[k]['Users'].append(str(i.author))
                dict_data[k]['dict_summary'].append((str(i.author), str(i.custom_id)))
        return True_False(i.message, dict_data)
                
    while True:
        print("interaction")
        interaction = await client.wait_for('button_click', check=check_button)
        await interaction.send(content=f"input accepted", ephemeral=True) #{dict_data[keys]['last_author']} clicked {keys} -- {dict_data[keys]['last_cusid']}



                        
                    
                
        
    

        
    
        


     

client.run('OTI1MDk1Nzc4NDkyNDk3OTcx.YcoIlQ.A9ULyzoPMXCZxbb4ze0LBSL-R3U')
