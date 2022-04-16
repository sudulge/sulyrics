# with discord.py

import discord
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import random
# import openpyxl
#import asyncio
#import time
import os
#import youtube_dl


client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    game = discord.Game(";help")
    await client.change_presence(status = discord.Status.online, activity=game)
    await client.get_channel(731547490347909120).send("이 몸 등 장 !") #혁수's 연구실



@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == 797414606104559616:
        await client.get_channel(723894009856131132).send(f"{payload.member.display_name} 이(가) 히드라에 {payload.emoji} 로 반응")


@client.event
async def on_message(message):
    if message.author == client.user:
        return


    if "⣿⣿⠛⠋⠉⠉⢻⣿⣿⣿⣿⡇⡀⠘⣿⣿⣿⣷⣿⣿⣿⠛⠻⢿⣿⣿⣿⣿⣷⣦" in message.content:
        #now = time.localtime()
        #await client.get_channel(731547490347909120).send("%s  %04d/%02d/%02d %02d:%02d:%02d \n %s" % (message.author, message.content, now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        await message.delete()

    if "⠄⠄⠄⠄⠄⠄⠄⣠⣴⣶⣿⣿⡿⠶⠄⠄⠄⠄⠐⠒⠒⠲⠶⢄⠄⠄⠄⠄⠄⠄" in message.content:
        #now = time.localtime()
        #await client.get_channel(731547490347909120).send("%s  %04d/%02d/%02d %02d:%02d:%02d \n %s" % (message.author, message.content, now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        await message.delete()

    if '됬' in message.content or '됫' in message.content:
        await message.channel.send("됬이 아니라 됐")

    if message.content.endswith("되"):
        await message.channel.send("되가 아니라 돼")

    if message.content.endswith("되요"):
        await message.channel.send("되요가 아니라 돼요")

    if '됌' in message.content:
        await message.channel.send("됌이 아니라 됨")

    if message.content.startswith(';hello'):
         await message.channel.send('Hello!')

    if message.content.startswith(";채널메시지"):
        channel = message.content[7:25]
        msg = message.content[26:]
        await client.get_channel(int(channel)).send(msg)

    if message.content.startswith("으악이"):
        await message.channel.send("게임채널으악이\n %s" % "https://bit.ly/32aEaRZ")

    if message.content.startswith(";정보"):
        date = datetime.utcfromtimestamp(((int(message.author.id) >> 22) + 1420070400000) / 1000)
        embed = discord.Embed(title="Sulyrics", color=0xf5a9a9)
        embed.add_field(name="이름", value="수리릭", inline=True)
        embed.add_field(name="서버닉네임", value="sulyrics", inline=True)
        embed.add_field(name="생일", value="2020년 7월 12일", inline=True)
        embed.add_field(name="아이디", value="731538324170342461", inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/731547490347909120/731743063571169320/asdf.png")
        await message.channel.send(embed=embed)

    if message.content.startswith(";자기소개"):
        date = datetime.utcfromtimestamp(((int(message.author.id) >> 22) + 1420070400000) / 1000)
        embed = discord.Embed(title="", color=0xf5a9a9)
        embed.add_field(name="이름", value=message.author.name, inline=True)
        embed.add_field(name="서버닉네임", value=message.author.display_name, inline=True)
        embed.add_field(name="가입일", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=True)
        embed.add_field(name="아이디", value=message.author.id, inline=True)
        embed.set_thumbnail(url=message.author.avatar_url)
        await message.channel.send(embed=embed)

    if message.content.startswith(";전적"):
        name = message.content[4:]
        link = "https://www.op.gg/summoner/userName=%s" % name
        await message.channel.purge(limit=1)
        await message.channel.send(link)

    if message.content.startswith(";멀티서치"):
        ps___ = message.content.replace("님이 로비에 참가하셨습니다.", '%2C')
        ps__ = ps___.replace('\n', '')
        ps_ = ps__.replace(';멀티서치', '')
        ps = ps_.replace(' ', '+')
        link = "https://www.op.gg/multi/query=%s" % ps
        await message.channel.purge(limit=1)
        await message.channel.send(link)

    if message.content.startswith(";오늘의 라인"):
        lane = ["탑","미드","원딜","서폿","정글"]
        await message.channel.send("오늘의 라인은 "+"```%s```" %lane[random.randint(0,4)])

    if message.content.startswith(";오피지지") or message.content.startswith(";옵지"):
        await message.channel.send("https://www.op.gg/")
        
    if message.content.startswith(";핑"):
        await message.channel.send(client.latency)

    if message.content.startswith(";dm"):
        author = message.mentions[0]
        #msg = message.content.split(" ")[2]
        msg = message.content[27:]
        await author.send(msg)
        print(message.author.display_name + ' dm')

    if message.content.startswith(';호출'):
        print(message.content)
        author = message.mentions[0]
        msg = "``%s``님이 ``%s``에서 당신을 찾습니다. \nhttps://discordapp.com/channels/%s/%s/%s" \
              %(message.author.display_name, message.channel.name, message.guild.id, message.channel.id, message.id)
        for i in range(10):
            await author.send(msg)

    if '<@' in message.content and message.mentions[0].id == 310691116049629184:
        await message.channel.send("공부하는중")


###########채팅로그관련#########################################################

    kickword = ["느금마", "ㄴㄱㅁ", "니애미", "어미", "애미", "너검", "니엄", "ㄴㅇㅁ", "링포섹"]
    for i in kickword:
        if i in message.content:
            print(f"{message.author.display_name}: {message.content}")
            await message.channel.send(f"{message.author.display_name}: {message.content}")
            await message.delete()
            user = message.guild.get_member(int(message.author.id))


    if message.channel.id == 731547490347909120 and not message.author.id == 310691116049629184:
        author = message.author.display_name
        content = message.content
        await message.delete()
        print("연구실 " + author +" "+ content)

    if message.channel.id == 797414606104559616 or message.channel.id == 723893987861332030:
        author = message.author.display_name
        content = message.content
        await client.get_channel(731547490347909120).send("히드라 %s %s" %(author,content))

    if message.content.startswith(";연구실청소") and message.author.id == 310691116049629184:
        if len(message.content) == 6:
            limit = None
        else:
            limit = int(message.content[7:])
        await message.channel.purge(limit = limit, check=lambda msg: not msg.pinned)

    if message.content.startswith(";고정"):
        message.id = message.content[4:]
        await message.pin()

    if message.content.startswith(";삭제"):
        await message.delete()
        message.id = message.content[4:]
        await message.delete()

#############################################################################

############급식#############################################################
    if message.content.startswith(';') and "급식" in message.content:
        KST = datetime.now(timezone('Asia/Seoul'))    # heroku 서버가 미국이기 때문에 서울 시간대로 변경
        today_date = f"{KST.month}월 {KST.day}일"
        lunchlist = '오늘의 급식은?'    # Local variable 'lunchlist' might be referenced before assignment 오류 방지용

        school_query = message.content.replace(';', '')
        html = requests.get(f'https://search.naver.com/search.naver?query={school_query}')
        soup = BeautifulSoup(html.text, 'html.parser')
        school_name = soup.find('span', {'class': 'main_title'}).text
        lunchboxs = soup.findAll('li', {'class': 'menu_info'})

        for lunchbox in lunchboxs:
            if today_date in str(lunchbox('strong')):
                lunchlist = lunchbox.find('ul').text
                break
            else:
                pass

        lunchlist = lunchlist.replace(" ", "\n")
        deletelist = '01234567890./-Jlm'
        for i in deletelist:
            lunchlist = lunchlist.replace(i,'')

        embed = discord.Embed(title=f"{school_name} {today_date} 중식", color=0xf5a9a9)
        embed.add_field(name="​", value=f"{lunchlist}", inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/769489028357160990.png?v=1")
        await message.channel.send(embed=embed)
############################################################################

############음악봇###########################################################

    # if message.content.startswith(";입장"):
    #     await message.author.voice.channel.connect()
    #     await message.channel.send("ㅎㅇ")
    #
    # if message.content.startswith(";퇴장"):
    #     for vc in client.voice_clients:
    #         if vc.guild == message.guild:
    #             voice = vc
    #
    #     await voice.disconnect()
    #     await message.channel.send("ㅂㅂ")
    #
    # if message.content.startswith(";재생"):
    #     for vc in client.voice_clients:
    #         if vc.guild == message.guild:
    #             voice = vc
    #
    #     url = message.content.split(" ")[1]
    #     option = {'format': 'bestaudio/best', 'postprocessors': [{'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio', 'preferredquality': '320',}], 'outtmpl' : "file/" + url.split('=')[1] + '.mp3'}
    #
    #     with youtube_dl.YoutubeDL(option) as ydl:
    #         ydl.download([url])
    #         info = ydl.extract_info(url, download=False)
    #         title = info["title"]
    #
    #     voice.play(discord.FFmpegPCMAudio("file/" + url.split('=')[1] + ".mp3"))
    #     await message.channel.send(f"{title}을 재생합니다")



############날씨#############################################################
    # if message.content.startswith(';') and "날씨" in message.content:
    #     location = message.content.split(" ")[0]
    #     location = location.replace(';','')
    #     html = requests.get('https://search.naver.com/search.naver?query=%s날씨' %location)
    #     soup = BeautifulSoup(html.text, 'html.parser')
    #     weatherbox = soup.find('div', {'class':'weather_box'})
    #     find_address = weatherbox.find('span', {'class':'btn_select'}).text
    #     find_currenttemp = weatherbox.find('span', {'class':'todaytemp'}).text
    #     detailbox = weatherbox.findAll('dd')
    #     find_dust = detailbox[0].find('span', {'class': 'num'}).text
    #     find_ultra_dust = detailbox[1].find('span', {'class': 'num'}).text
    #
    #
    #     await message.channel.send('위치: '+find_address)
    #     await message.channel.send('현재온도: '+find_currenttemp+'˚C')
    #     await message.channel.send('현재 미세먼지: ' + find_dust)
    #     await message.channel.send('현재 초미세먼지: ' + find_ultra_dust)
##########################################################################

############오늘의 운세###################################################
    if message.content.startswith(';오늘의 운세'):
        birth = message.content.split(" ")[2]

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        driver = webdriver.Chrome('C:\chromedriver\chromedriver.exe', options=options)

        driver.implicitly_wait(5)

        driver.get(
            'https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=%EC%98%A4%EB%8A%98%EC%9D%98+%EC%9A%B4%EC%84%B8')

        birthbox = driver.find_element_by_xpath('//*[@id="srch_txt"]')
        birthbox.clear()
        birthbox.send_keys(birth)

        driver.implicitly_wait(5)
        driver.find_element_by_xpath('//*[@id="fortune_birthCondition"]/div[1]/fieldset/input').click()

        mainfortune = driver.find_element_by_xpath('//*[@id="fortune_birthResult"]/dl[1]/dd/strong')
        detailfortune = driver.find_element_by_xpath('//*[@id="fortune_birthResult"]/dl[1]/dd/p')

        embed = discord.Embed(title = message.author.display_name +'님의 운세', color=0xf5a9a9)
        embed.add_field(name=mainfortune.text, value=detailfortune.text, inline=False)

        driver.find_element_by_xpath('//*[@id="fortune_birthResult"]/ul[2]/li[5]/a/div').click()
        studyfortune = driver.find_element_by_xpath('//*[@id="fortune_birthResult"]/dl[1]/dd/p')

        embed.add_field(name="학업, 성적운", value=studyfortune.text, inline=False)
        await message.channel.send(embed=embed)

##########################################################################

##########################################################################
#미니게임#
##########################################################################

#######################가위바위보#########################################
    # win = "젠장.. 네 녀석의 승리다"
    # lose = "나약한 녀석.. 나의 승리다"
    # draw = "흥...네 녀석.. 『이 몸』과 비길 수 있는 실력이라니.....꽤나 하는군.."
    #
    # def rsp(author_id, result):  # a = message.author.id     b = 승패 1 = 승 2 = 패 3 = 무
    #     file = openpyxl.load_workbook("봇가위바위보전적.xlsx")
    #     sheet = file.active
    #     i = 2
    #     while True:
    #         if sheet["A" + str(i)].value == str(author_id):
    #             sheet["C" + str(i)].value = sheet["C" + str(i)].value + 1
    #             if result == 1:
    #                 sheet["D" + str(i)].value = sheet["D" + str(i)].value + 1
    #             elif result == 2:
    #                 sheet["E" + str(i)].value = sheet["E" + str(i)].value + 1
    #             elif result == 3:
    #                 sheet["F" + str(i)].value = sheet["F" + str(i)].value + 1
    #             file.save("봇가위바위보전적.xlsx")
    #             break
    #         if sheet["A" + str(i)].value == None:
    #             sheet["A" + str(i)].value = str(author_id)
    #             sheet["C" + str(i)].value = 1
    #             sheet["D" + str(i)].value = 0
    #             sheet["E" + str(i)].value = 0
    #             sheet["F" + str(i)].value = 0
    #             if result == 1:
    #                 sheet["D" + str(i)].value = 1
    #             elif result == 2:
    #                 sheet["E" + str(i)].value = 1
    #             elif result == 3:
    #                 sheet["F" + str(i)].value = 1
    #             file.save("봇가위바위보전적.xlsx")
    #             break
    #         i += 1
    #
    # if message.content.startswith(";가위바위보"):
    #     result = 0
    #     bc = random.randint(1, 3)
    #     botchoice = 0
    #     if bc == 1:
    #         botchoice = "가위 :v:"
    #     elif bc == 2:
    #         botchoice = "바위 :fist:"
    #     elif bc == 3:
    #         botchoice = "보 :hand_splayed: "
    #     pc = message.content[7:]
    #     playerchoice = 0
    #     if pc == '가위':
    #         playerchoice = pc + ' :v:'
    #     elif pc == '바위':
    #         playerchoice = pc + ' :fist:'
    #     elif pc == '보':
    #         playerchoice = pc + ' :hand_splayed:'
    #
    #     winembed = discord.Embed(title="가위바위보", color=0x1bfc01)
    #     winembed.add_field(name=message.author.display_name, value=playerchoice, inline=False)
    #     winembed.add_field(name="sulyrics", value=botchoice, inline=False)
    #     winembed.add_field(name=win, value='한번 더 하자..')
    #     # await message.channel.send(embed=winembed)
    #
    #     loseembed = discord.Embed(title="가위바위보", color=0xfd0004)
    #     loseembed.add_field(name=message.author.display_name, value=playerchoice, inline=False)
    #     loseembed.add_field(name="sulyrics", value=botchoice, inline=False)
    #     loseembed.add_field(name=lose, value='넌 나한테 안돼')
    #     # await message.channel.send(embed=loseembed)
    #
    #     drawembed = discord.Embed(title="가위바위보", color=0x014DFC)
    #     drawembed.add_field(name=message.author.display_name, value=playerchoice, inline=False)
    #     drawembed.add_field(name="sulyrics", value=botchoice, inline=False)
    #     drawembed.add_field(name=draw, value='다음을 기약하지')
    #     # await message.channel.send(embed=drawembed)
    #
    #     if bc == 1:  #가위
    #         if message.content[7:] == "가위":
    #             await message.channel.send(embed=drawembed)
    #             author_id = message.author.id
    #             result = 3
    #             rsp(author_id, result)
    #         elif message.content[7:] == "바위":
    #             await message.channel.send(embed=winembed)
    #             author_id = message.author.id
    #             result = 1
    #             rsp(author_id, result)
    #         elif message.content[7:] == "보":
    #             await message.channel.send(embed=loseembed)
    #             author_id = message.author.id
    #             result = 2
    #             rsp(author_id, result)
    #     elif bc == 2:  #바위
    #         if message.content[7:] == "가위":
    #             await message.channel.send(embed=loseembed)
    #             author_id = message.author.id
    #             result = 2
    #             rsp(author_id, result)
    #         elif message.content[7:] == "바위":
    #             await message.channel.send(embed=drawembed)
    #             author_id = message.author.id
    #             result = 3
    #             rsp(author_id, result)
    #         elif message.content[7:] == "보":
    #             await message.channel.send(embed=winembed)
    #             author_id = message.author.id
    #             result = 1
    #             rsp(author_id, result)
    #     elif bc == 3:  #보
    #         if message.content[7:] == "가위":
    #             await message.channel.send(embed=winembed)
    #             author_id = message.author.id
    #             result = 1
    #             rsp(author_id, result)
    #         elif message.content[7:] == "바위":
    #             await message.channel.send(embed=loseembed)
    #             author_id = message.author.id
    #             result = 2
    #             rsp(author_id, result)
    #         elif message.content[7:] == "보":
    #             await message.channel.send(embed=drawembed)
    #             author_id = message.author.id
    #             result = 3
    #             rsp(author_id, result)
    #
    # if message.content.startswith(";가위바위보 전적"):
    #     file = openpyxl.load_workbook("봇가위바위보전적.xlsx")
    #     sheet = file.active
    #     i = 2
    #     while True:
    #         if sheet["A" + str(i)].value == str(message.author.id):
    #             howmanygame = sheet["C" + str(i)].value
    #             howmanywin = sheet["D" + str(i)].value
    #             howmanylose = sheet["E" + str(i)].value
    #             howmanydraw = sheet["F" + str(i)].value
    #             break
    #         if sheet["A" + str(i)].value == None:
    #             await message.channel.send("전적이 없습니다. 먼저 가위바위보를 플레이 해주세요")
    #             break
    #         i += 1
    #     await message.channel.send("%s님의 가위바위보 전적은 %s전 %s승 %s패 %s무 입니다." %(message.author.display_name,howmanygame,howmanywin,howmanylose,howmanydraw))
    #
    # if message.content.startswith(";가위바위보 전적 초기화"):
    #     file = openpyxl.load_workbook("봇가위바위보전적.xlsx")
    #     sheet = file.active
    #     i = 2
    #     while True:
    #         if sheet["A" + str(i)].value == str(message.author.id):
    #             sheet["C" + str(i)].value = 0
    #             sheet["D" + str(i)].value = 0
    #             sheet["E" + str(i)].value = 0
    #             sheet["F" + str(i)].value = 0
    #             file.save("봇가위바위보전적.xlsx")
    #             break
    #         if sheet["A" + str(i)].value == None:
    #             await message.channel.send("전적이 없습니다. 먼저 가위바위보를 플레이 해주세요")
    #             break
    #         i += 1
    #     await message.channel.send("초기화를 완료했습니다.")

#################################################################################

###############룰렛##############################################################

    if message.content.startswith(";룰렛"):
        if len(message.content) > 3:
            start = int(message.content.split(" ")[1])
            end = int(message.content.split(" ")[2])
        else:
            start = 1
            end = 10
        pick = random.randint(start, end)
        await message.channel.send(pick)

#################################################################################

###############투표##############################################################
    if message.content.startswith(";투표"):
        name='투표'
        if len(message.content) > 3:
            name = message.content[3:]
        vote = await message.channel.send("%s           게시자:%s" %(name, message.author.display_name))
        await vote.add_reaction('👍')
        await vote.add_reaction('👎')
#################################################################################

###############헬프##############################################################
    if message.content.startswith(";help"):
        helpembed = discord.Embed(title="**sulyrics**의 명령어 목록입니다.", color=0xf5a9a9)
        helpembed.add_field(name="명령어\n", value="`;hello` `;정보` `;자기소개` `;쌉소리청소 숫자` `;핑` `;help`\n\n"
                                              "`;p 노래이름` `;재생 노래이름`\n\n"
                                              "`;전적 롤닉네임` `;멀티서치 픽창복붙`\n\n"
                                              "`;dm 유저아이디 보낼말` `;채널메시지 채널아이디 보낼말`", inline=False)
        helpembed.add_field(name="⠀", value="⠀", inline=False)
        helpembed.add_field(name="미니게임", value="`;봇가위바위보 가위/바위/보` `;봇가위바위보 전적` `;봇가위바위보 전적 초기화`\n\n"
                                               "`;룰렛`", inline=False)
        helpembed.add_field(name="⠀", value="⠀", inline=False)
        helpembed.add_field(name="그 외 반응하는 말들", value="됬  되  되요  됌  ㅇㅈ  ㄹㅇ  ㅋㅋㄹ  "
                                                      "지건  배고파  야발  리븐누나  아리누나  "
                                                      "가능  불가능  으악이  @")

        mention = '<@%s>' %message.author.id
        await message.channel.send("%s 개인 DM으로 도움말을 전송 하였습니다." %mention)
        await message.author.send(embed=helpembed)





#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀<<공백#

bot_token = os.environ["BOT_TOKEN"]
client.run(bot_token)
