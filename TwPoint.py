import random, string, re, datetime, config
from random import sample
from telegram.ext import Dispatcher,CommandHandler, MessageHandler, Filters, Updater
from telegram import BotCommand

games = {}
LifetimeStats = config.CONFIG['LifetimeStats']

def help():
    return r"""欢迎来到 Noah 的 24 点游戏! 
    
您的目标是尝试去使用四个数字来算出 24。
每张牌都必须使用一次，但不能重复使用。
请记住, 您只能使用 +, -, *, / 和 ()。 

祝你们好运!"""


def correctAnswers(func):
    return func['correct']

def errors(func):
    return func['error']

def list_lifetime_stats(update,context):
    lead = ""
    index = 1
    title = ""
    info = []
    uid = update.effective_user.id
    first_name = update.effective_user.first_name
    check_lifetime_stats(uid,first_name)
    for uids in LifetimeStats:
        info.append({
            'uid': uids,
            'correct':LifetimeStats[uids]['correct'],
            'error':LifetimeStats[uids]['error'],
            'fname':LifetimeStats[uids]['fname']
            })
        info.sort(key=errors,reverse=False)
        info.sort(key=correctAnswers,reverse=True)
    for each in info:  
        if index != 1 and index != 2 and index != 3:
            lead += f"「{index}𝘁𝗵 𝗽𝗹𝗮𝗰𝗲」 ✨ {each['fname']}: ✅ {each['correct']} 次正确 ❌ {each['error']} 次错误\n"
        else:
            if index == 1:
                title = "🏆 𝗖𝗵𝗮𝗺𝗽𝗶𝗼𝗻" 
            elif index == 2:
                title = "🎖 𝗪𝗶𝗻𝗻𝗲𝗿"
            elif index == 3:
                title = "🏅 𝗩𝗶𝗰𝘁𝗼𝗿"
            lead += f"「{title}」 ✨ {each['fname']}: ✅ {each['correct']} 次正确 ❌ {each['error']} 次错误\n"
        index += 1
    update.message.reply_text(lead)

def sort_leaderboards(chatid,uid,fname):
    lead = ""
    index = 1
    title = ""
    info = []
    check_user(uid,chatid,fname)
    for uids in games[chatid]['users']:
        info.append({
            'uid': uids,
            'correct':games[chatid]['users'][uids]['correct']['count'],
            'error':games[chatid]['users'][uids]['error'],
            'fname':games[chatid]['users'][uids]['fname']
            })
        info.sort(key=correctAnswers,reverse=True)
        print(info)
    for each in info:  
        if index != 1 and index != 2 and index != 3:
            lead += f"「{index}𝘁𝗵 𝗽𝗹𝗮𝗰𝗲」 ✨ {each['fname']}: ✅ {each['correct']} 次正确 ❌ {each['error']} 次错误\n"
        else:
            if index == 1:
                title = "🏆 𝗖𝗵𝗮𝗺𝗽𝗶𝗼𝗻" 
            elif index == 2:
                title = "🎖 𝗪𝗶𝗻𝗻𝗲𝗿"
            elif index == 3:
                title = "🏅 𝗩𝗶𝗰𝘁𝗼𝗿"
            lead += f"「{title}」 ✨ {each['fname']}: ✅ {each['correct']} 次正确 ❌ {each['error']} 次错误\n"
        index += 1
    return lead 
    
def detective_system(answer,cards):
    Cheat = False
    Numbers = list(dict.fromkeys(re.findall(r'\d+', answer)))
    modsAnswer = answer.replace("+","_").replace("-","_").replace("*","_").replace("/","_")
    numberCount = modsAnswer.split("_")
    if not len(numberCount) == 4:
        Cheat = True
    for number in Numbers:
        if not int(number) in cards:
            Cheat = True
    return Cheat

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
    print(games)

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

def start(update,context): 
    uid = str(update.effective_user.id)
    fname = str(update.effective_user.first_name)
    chatid = update.effective_chat.id
    cards = random.sample(range(1,10),4) 
    update.effective_message.reply_text(f" {help()} 四个数字分别是：") 

    context.bot.send_message(chatid, text=f"{cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}")
    set_games_cards(chatid,cards,uid,fname)


def question(update,context):
    title = ""
    index = 1
    first_name = update.effective_user.first_name
    uid = str(update.effective_user.id)
    chatid = update.effective_chat.id
    correctAnswers = ""
    lead = ""
    try:
        check_user(uid,chatid,first_name)
        for uid in games[chatid]['users']:
            for answer in games[chatid]['users'][uid]['correct']['answer']:
                time = answer[1] - games[chatid]['time']
                time = str(time)[:-7]
                if index != 1 and index != 2 and index != 3:
                    correctAnswers += f"「{index}𝘁𝗵 𝗮𝗻𝘀𝘄𝗲𝗿」{games[chatid]['users'][uid]['fname']}  ✔︎  {answer[0]} ⏱ ({time})\n"
                else:
                    if index == 1:
                        title = "🥇 𝗚𝗼𝗹𝗱"
                    elif index == 2:
                        title = "🥈 𝗦𝗶𝗹𝘃𝗲𝗿"
                    elif index == 3:
                        title = "🥉 𝗕𝗿𝗼𝗻𝘇𝗲"
                    correctAnswers += f"「{title}」{games[chatid]['users'][uid]['fname']}  ✔︎  {answer[0]} ⏱ ({time})\n"
                index += 1
        update.effective_message.reply_text(f"""当前卡牌：{games[chatid]['cards']}
--------------------
目前的正确答案：

{correctAnswers}
--------------------
个人排行榜：

{sort_leaderboards(chatid,uid,first_name)}
""")
    except KeyError:
        update.effective_message.reply_text("目前没有被开启的游戏。/gamestart24 来开启一个游戏。")

def end(update,context):
    update.effective_message.reply_text("游戏结束。/gamestart24 来开启一个游戏。")
    del games[update.effective_chat.id]

def rules(update,context):
    update.message.reply_text(help())
    
def proc_text(update,context):
    first_name = update.effective_user.first_name
    chatid = update.effective_chat.id
    uid = str(update.effective_user.id)    
    msg = ""
    answer = update.message.text.replace(".","").replace("（","(").replace("）",")")
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
                            games[chatid]['users'][uid]['correct']['answer'].append([answer.replace(" ",""),datetime.datetime.now()])
                            games[chatid]['totalanswers'].append(answer.replace(" ",""))
                            print(games)  
                        else:  
                            msg = f"{first_name} 答错啦！"
                            games[chatid]['users'][uid]['error'] += 1
                            LifetimeStats[uid]['error'] += 1
                    else:
                        games[chatid]['users'][uid]['error'] += 1
                        LifetimeStats[uid]['error'] += 1
                        msg = f"请使用我给你的那几个数字！需有查看更多规则，请查看 /gamerules ."                                                                                                                    
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
    dp.add_handler(CommandHandler('gamelifetimestats',list_lifetime_stats))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command) & Filters.chat_type.supergroup,proc_text))
    return [
        BotCommand('gamestart24','开始一个24点游戏'),
        BotCommand('gameq','查询当前进行中的24点游戏'),
        BotCommand('gameend24','结束当前进行的游戏'),
        BotCommand('gamerules','查询24点的游戏规则'),
        BotCommand('gamelifetimestats','查询总排行榜')
        ]