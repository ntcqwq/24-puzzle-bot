import random, string, re, datetime, config
from random import sample
from telegram.ext import Dispatcher,CommandHandler, MessageHandler, Filters, Updater
from telegram import BotCommand, PhotoSize

games = {}
LifetimeStats = config.CONFIG['LifetimeStats']

def help():
    return r"""欢迎来到 Noah 的 24 点游戏! 
    
您的目标是尝试去使用四个数字来算出 24。
每张牌都必须使用一次，但不能重复使用。
请记住, 您只能使用 加，减，乘，除，和括号 （请不要用不必要的括号）。 

祝你们好运!

如果还有更多问题，查看 https://github.com/SSnipro/24gamebot/blob/master/README.md"""

def correctAnswers(func):
    return func['correct']

def errors(func):
    return func['error']

def times(func):
    return func['ct']

def set_games_cards(chatid,cards,uid,fname):
    games[chatid] = {}
    games[chatid]['cards'] = cards
    games[chatid]['time'] = datetime.datetime.now()
    games[chatid]['users'] = {}
    games[chatid]['users'][uid] = {
            'fname':fname,
            'correct':{
                'count':0,
                'answer':[]
            },
            'error':0
        }
    games[chatid]['totalanswers'] = []

def check_user(uid,chatid,first_name):
    if not chatid in games:
        games[chatid] = {}
        games[chatid]['users'] = {}
    if not uid in games[chatid]['users']:
        games[chatid]['users'][uid] = {
            'fname':first_name,
                'correct':{
                    'count':0,
                    'answer':[]
                },
                'error':0 
        }

def check_lifetime_stats(uid,first_name):
    if not uid in LifetimeStats:
        LifetimeStats[uid] = {
            'fname':first_name,
            'correct':0,
            'error':0
        }

def sort_leaderboards(chatid,UID,FNAME,title,WLB,uids):

    Leaderboard = ""
    Title = ""
    Placement = 1 
    PlayerStatus = []

    check_user(UID,chatid,FNAME)
    
    if WLB == "QLB" or WLB == "LTLB":
        for uid in uids:
            if WLB == "QLB":
                PlayerStatus.append({
                    'uid': uid,
                    'correct': games[chatid]['users'][uid]['correct']['count'],
                    'error': games[chatid]['users'][uid]['error'],
                    'fname': games[chatid]['users'][uid]['fname']
                    })
            elif WLB == "LTLB":
                check_lifetime_stats(UID,FNAME)
                PlayerStatus.append({
                    'uid': uid,
                    'correct': LifetimeStats[uid]['correct'],
                    'error': LifetimeStats[uid]['error'],
                    'fname': LifetimeStats[uid]['fname']
                    })

        PlayerStatus.sort(key=errors,reverse=False)
        PlayerStatus.sort(key=correctAnswers,reverse=True)

    elif WLB == "QCAT":
        for uid in uids:
            for answer in games[chatid]['users'][uid]['correct']['answer']:
                time = answer[1] - games[chatid]['time']
                time = str(time)[:-7]
                PlayerStatus.append({
                        'ct': float(time.replace(":","")),
                        'time':time,
                        'uid':uid,
                        'answer':answer[0],
                        'fname':games[chatid]['users'][uid]['fname']
                    })
            PlayerStatus.sort(key=times,reverse=False)

    for EachPlayer in PlayerStatus:  
        if Placement != 1 and Placement != 2 and Placement != 3:
            if WLB == "QLB" or WLB == "LTLB":
                Leaderboard += f"「{Placement}𝘁𝗵 𝗽𝗹𝗮𝗰𝗲」 ✨ {EachPlayer['fname']} | ✅ {EachPlayer['correct']} 次正确 ❌ {EachPlayer['error']} 次错误\n"
            elif WLB == "QCAT":
                Leaderboard += f"「{Placement}𝘁𝗵 𝗮𝗻𝘀𝘄𝗲𝗿」{EachPlayer['fname']}  ✔︎  {EachPlayer['answer']} ⏱ ({EachPlayer['time']})\n"
        else:
            for Num in range(1,4):
                if Placement == Num:
                    Title = title[Num-1]
            if WLB == "QLB" or WLB == "LTLB":
                Leaderboard += f"「{Title}」 ✨ {EachPlayer['fname']} | ✅ {EachPlayer['correct']} 次正确 ❌ {EachPlayer['error']} 次错误\n"
            elif WLB == "QCAT":
                Leaderboard += f"「{Title}」{EachPlayer['fname']}  ✔︎  {EachPlayer['answer']} ⏱ ({EachPlayer['time']})\n"
        Placement += 1
    return Leaderboard 
    
def detective_system(answer,cards):
    Cheat = False
    Numbers = list(dict.fromkeys(re.findall(r'\d+', answer)))

    modsAnswer = answer.replace("+","_").replace("-","_").replace("*","_").replace("/","_")
    numberCount = modsAnswer.split("_")

    modbAnswer = answer.replace("(","_").replace(")","_")
    bracketCount = modbAnswer.split("_")

    if not len(numberCount) == 4:
        Cheat = True
    for number in Numbers:
        if not int(number) in cards:
            Cheat = True
    for every in range(1,10):
        if f"({every})" in answer:
            Cheat = True
    if ("(((" in answer or ")))" in answer) or ("((" in answer and "))" in answer) or len(bracketCount) >= 6:
        Cheat = True
    try:
        if answer.endswith(')') and answer.startswith('('):
            if eval(answer.lstrip('(').rstrip(')')) == eval(answer):
                Cheat = True
    except SyntaxError:
        pass
    return Cheat

def start(update,context): 
    uid = str(update.effective_user.id)
    fname = str(update.effective_user.first_name)
    chatid = update.effective_chat.id
    cards = random.choices(range(1,10),k=4) 
    update.effective_message.reply_text(f" {help()} 四个数字分别是：") 
    context.bot.send_message(chatid, text=f"{cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}")
    context.bot.send_photo(chatid, photo=open('/Users/Snipro/work/24gamebot/Images/re.png', 'rb'), caption= "⚠️ 温馨提示：请把 Telegram 自动表情给关掉！")
    set_games_cards(chatid,cards,uid,fname)


def question(update,context):
    first_name = update.effective_user.first_name
    uid = str(update.effective_user.id)
    chatid = update.effective_chat.id

    try:
        check_user(uid,chatid,first_name)
        update.effective_message.reply_text(f"""当前卡牌：{games[chatid]['cards']}
--------------------
目前的正确答案：

{sort_leaderboards(chatid,uid,first_name,["🥇 𝗚𝗼𝗹𝗱","🥈 𝗦𝗶𝗹𝘃𝗲𝗿","🥉 𝗕𝗿𝗼𝗻𝘇𝗲"],"QCAT",games[chatid]['users'])}
--------------------
个人排行榜：

{sort_leaderboards(chatid,uid,first_name,["🏆 𝗖𝗵𝗮𝗺𝗽𝗶𝗼𝗻","🎖 𝗪𝗶𝗻𝗻𝗲𝗿","🏅 𝗩𝗶𝗰𝘁𝗼𝗿"],"QLB",games[chatid]['users'])}
""")
    except KeyError:
        update.effective_message.reply_text("目前没有被开启的游戏。/gamestart24 来开启一个游戏。")

def end(update,context):
    update.effective_message.reply_text("游戏结束。/gamestart24 来开启一个游戏。")
    del games[update.effective_chat.id]

def rules(update,context):
    update.message.reply_text(help())

def List_Lifetime_Stats(update,context):
    uid = str(update.effective_user.id)
    first_name = update.effective_user.first_name
    
    update.message.reply_text(sort_leaderboards(update.effective_chat.id,uid,first_name,["🏆 𝗖𝗵𝗮𝗺𝗽𝗶𝗼𝗻","🎖 𝗪𝗶𝗻𝗻𝗲𝗿","🏅 𝗩𝗶𝗰𝘁𝗼𝗿"],"LTLB",LifetimeStats))

def proc_text(update,context):
    first_name = update.effective_user.first_name
    chatid = update.effective_chat.id
    uid = str(update.effective_user.id)    
    msg = ""
    answer = update.message.text.replace(".","").replace("（","(").replace("）",")").replace(" ","").replace("x","*").replace("[","(").replace("]",")").replace("×","*").replace("÷","/")
    if answer[0].isdigit() or answer[0] == "(":
        try: 
            cards = games[chatid]['cards']
            check_user(uid,chatid,first_name)
            check_lifetime_stats(uid,first_name)
            if not answer in games[chatid]['totalanswers']:
                try:
                    if detective_system(answer,cards) == False:
                        if int(eval(answer)) == 24:
                            msg = f"{first_name} 答对啦！" 
                            games[chatid]['users'][uid]['correct']['count'] += 1
                            LifetimeStats[uid]['correct'] += 1
                            games[chatid]['users'][uid]['correct']['answer'].append([answer,datetime.datetime.now()])
                            games[chatid]['totalanswers'].append(answer)
                        else:  
                            msg = f"{first_name} 答错啦！"
                            games[chatid]['users'][uid]['error'] += 1
                            LifetimeStats[uid]['error'] += 1
                    else:
                        games[chatid]['users'][uid]['error'] += 1
                        LifetimeStats[uid]['error'] += 1
                        msg = f"请使用我给你的那几个数字并且不要使用不必要的括号！需有查看更多规则，请查看 /gamerules ."                                                                                                                    
                except:
                    msg = f"{first_name} 答错啦！您的目标是尝试去使用 {games[chatid]['cards']} 来算出 24.\n请记住, 您只能使用 +, -, *, / 和 (). "
                    games[chatid]['users'][uid]['error'] += 1
                    LifetimeStats[uid]['error'] += 1
            else:
                msg = f"{first_name}, 某某人已经说出来您的答案啦！"
        except KeyError:
            msg = "目前没有被开启的游戏。/gamestart24 来开启一个游戏。"
        update.effective_message.reply_text(msg)
    config.save_config()

def add_handler(dp:Dispatcher):
    dp.add_handler(CommandHandler('gamestart24', start))
    dp.add_handler(CommandHandler('gameq', question))
    dp.add_handler(CommandHandler('gameend24', end))
    dp.add_handler(CommandHandler('gamerules', rules))
    dp.add_handler(CommandHandler('gamel',List_Lifetime_Stats))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command) & Filters.chat_type.groups,proc_text))
    return [
        BotCommand('gamestart24','开始一个24点游戏'),
        BotCommand('gameq','查询当前进行中的24点游戏'),
        BotCommand('gameend24','结束当前进行的游戏'),
        BotCommand('gamerules','查询24点的游戏规则'),
        BotCommand('gamel','查询总排行榜')
        ]