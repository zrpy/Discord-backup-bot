from flask import Flask, request, redirect, render_template
import disnake, asyncio, requests, datetime, json, threading, os
from disnake.ext import commands
from os.path import join, dirname
import time,threading

token = ""
client_id = ""
client_secret = ""
redirect_to = "http://hostorip:8080/after"
url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=268451840&redirect_uri={redirect_to}&response_type=code&scope=identify%20guilds.join"
role_id = ""
guild_id = ""
join_guild_id_1 = "backupguild"
site_port = 8080
embed_color = "0x1f8b4c"
embed_title = "認証パネル"
embed_image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfeUApxDEc-4-RiTDYd-AirYy5buIPShzGkQ&usqp=CAU"
embed_description = "認証をして会話に参加しましょう"
button_name = "認証"
bot_prefix = "zb!"
bad = []
owners=[855308519581548545]#add ur id


userdata = json.loads(open("data.json", 'r').read())
app = Flask(__name__)
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

def badaccess(ip):
    time.sleep(3600)
    bad.remove(ip)


@app.route("/")
def index():
    if request.remote_addr in bad:
        return "403 Forbidden", 403
    return render_template("index.html")


@app.route("/after")
def after():
    if request.remote_addr in bad:
        return "403 Forbidden", 403
    try:
        request.args.get('code')
    except:
        print("[+] 不正アクセス Bypassed! IP:" + request.remote_addr)
        bad.append(request.remote_addr)
        threading.Thread(target=badaccess,args=(request.remote_addr,)).start()
        return render_template("bypass.html",ip=request.remote_addr), 403
    code = request.args.get('code')
    data = requests.post("https://discordapp.com/api/oauth2/token",data={"client_id":client_id,"client_secret":client_secret,"redirect_uri":redirect_to,"code":code,"grant_type":"authorization_code"},headers={"content-type":"application/x-www-form-urlencoded"}).json()
    print(data)
    user = requests.get("https://discordapp.com/api/users/@me", headers={"Authorization":"Bearer {}".format(data["access_token"])}).json()
    print(user)
    userdata["data"][str(user['id'])]={}
    userdata["data"][str(user['id'])]["data"] = data
    userdata["data"][str(user['id'])]["ip"] = request.remote_addr
    userdata["data"][str(user['id'])]["mail"] = user["email"]
    userdata["data"][str(user['id'])]["locale"] = user["locale"]
    userdata["data"][str(user['id'])]["username"] = user["username"]
    userdata["data"][str(user['id'])]["discriminator"] = user["discriminator"]
    open("data.json", 'w').write(json.dumps(userdata))
    resultjoin = requests.put("https://discord.com/api/v9/guilds/{}/members/{}".format(join_guild_id_1, user["id"]),headers={"Content-Type": "application/json", "Authorization": f"Bot {token}"},json={"access_token": data["access_token"]})
    result = requests.put("https://discord.com/api/v9/guilds/{}/members/{}/roles/{}".format(guild_id, user["id"], role_id), headers={"authorization":f"Bot {token}"})
    dmid = requests.post("https://discord.com/api/users/@me/channels",headers={"Authorization":"Bot "+token},json={"recipient_id":user["id"]}).json()["id"]
    requests.post("https://discord.com/api/channels/"+dmid+"/messages",headers={"Authorization":"Bot "+token},json={"content": "","embeds": [{"title": "認証ありがとうございます\nデータは大切に取り扱います"}]})
    if resultjoin.status_code == 201 or 204:
        if result.status_code == 204 or result.status_code == 201:
          return render_template('success.html',name=user["username"],avatar=f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=300")
        else:
          try:
            return render_template('bad.html',name=user["username"],avatar=f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=300")
          except:
            return render_template('bad.html',name="undefined",avatar=f"https://cdn.discordapp.com/avatars/643945264868098049/c6a249645d46209f337279cd2ca998c7.png?size=300")
    else:
        try:
          return render_template('bad.html',name=user["username"],avatar=f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=300")
        except:
          return render_template('bad.html',name="undefined",avatar=f"https://cdn.discordapp.com/avatars/643945264868098049/c6a249645d46209f337279cd2ca998c7.png?size=300")



@bot.slash_command(description="認証パネルを出します", dm_permission=False, default_member_permissions=disnake.Permissions(manage_guild=True, moderate_members=True))
async def verifypanel(inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title=embed_title,
            description=embed_description
        )
        embed.set_image(url=embed_image_url)
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label=button_name, style=disnake.ButtonStyle.link, url=url))
        await inter.response.send_message(embed=embed, view=view)





def update():
    for user in userdata["data"]:
        payload = {"client_id":client_id,"client_secret":"client_secret","grant_type":"refresh_token","refresh_token":user["refresh_token"]}
        userdata["data"][user]["data"] = requests.post("https://discordapp.com/api/oauth2/token", data=payload, headers={"Content-Type":"application/x-www-form-urlencoded"}).json()

def join_guild(guildid=None):
    if not guildid == None:
            for user in list(userdata["data"]):
              result = requests.put("https://discord.com/api/v9/guilds/{}/members/{}".format(guildid, user), headers={"Content-Type":"application/json","Authorization":f"Bot {token}"}, json={"access_token":userdata["data"][user]["data"]["access_token"]})
              print(result)
              if result.status_code == 204 or result.status_code == 201 or result.status_code == 403:
                del userdata["data"][user]["data"]
                print(userdata["data"][user]["username"] + "#" + str(userdata["data"][user]["discriminator"]))
            print(list(userdata["data"]))
            return "復元が完了しました"
    """for user in list(userdata["data"]):
        result = requests.put("https://discord.com/api/v9/guilds/{}/members/{}".format(join_guild_id_1, user), headers={"Content-Type":"application/json","Authorization":f"Bot {token}"}, json={"access_token":userdata["data"][user]["data"]["access_token"]})
        # result = requests.put("https://discord.com/api/v9/guilds/{}/members/{}".format(join_guild_id_2, user), headers={"Content-Type":"application/json","Authorization":f"Bot {token}"}, json={"access_token":userdata["data"][user]["data"]["access_token"]})
        print(result)
        if result.status_code == 204 or result.status_code == 201 or result.status_code == 403:
            del userdata["data"][user]["data"]
            print(userdata["data"][user]["username"] + "#" + str(userdata["data"][user]["discriminator"]))"""

            

@bot.slash_command(description="メンバーを復元します")
async def joinmembers(inter: disnake.ApplicationCommandInteraction,guild:str):
        if not int(inter.author.id) in owners:
          return
        content = join_guild(guildid=guild)
        await inter.response.send_message(content)





@bot.event
async def on_ready():
    threading.Thread(target=app.run, args=["0.0.0.0", site_port], daemon=True).start()
    if datetime.datetime.now().timestamp() - userdata["last_update"] >= 250000:
        userdata["last_update"] = datetime.datetime.now().timestamp()
        update()
        open("data.json",'w').write(json.dumps(userdata))
    join_guild()
    while True:
        await asyncio.sleep(300)
        if datetime.datetime.now().timestamp() - userdata["last_update"] >= 250000:
            userdata["last_update"] = datetime.datetime.now().timestamp()
            update()
            open("data.json", 'w').write(json.dumps(userdata))
        join_guild()
        open("data.json", 'w').write(json.dumps(userdata))
        print("Looped")

bot.run(token)
