#coding:utf-8
import os
import itchat
import json
from itchat.content import RECORDING,TEXT
from wxtool import VoiceRobot

app = VoiceRobot()

text_chatroom_names=["测试群","胡家大湾","胡家大屋","熊家大湾小分队"]
voice_chatroom_names=["测试群","胡家大湾","胡家大屋","熊家大湾小分队"]
voice_chatroom_user_nicknames=["bluecatr"]
text_user_nicknames=["bluecatr"]
voice_user_nicknames=["bluecatr"]
my_user_nickname = "蓝猫"

@itchat.msg_register(TEXT,isGroupChat=True)
def group_text_chat(msg):
    if msg['isAt']:
        #print json.dumps(msg).decode('unicode-escape')
        chatroom_name = msg["User"]["NickName"]
        chatroom_id = msg['FromUserName']
        print "Receive a TEXT message from chatroom: RoomName(%s)/ID(%s)" % (chatroom_name,chatroom_id)
        if not chatroom_name in text_chatroom_names:
            return
        user_name = msg['ActualUserName']
        user_group_nickname = msg['ActualNickName']
        user_nickname = user_group_nickname
        user = itchat.search_friends(userName=user_name)
        if user:
            #print json.dumps(user).decode('unicode-escape')
            user_nickname = user["NickName"]
        print "The group message from user: NickName(%s)/GroupNickName(%s)/ID(%s)" % (user_nickname,user_group_nickname,user_name)
        message = msg['Text']
        answer = app.processText(msg['FromUserName'], message)
        itchat.send(u'@%s %s' % (user_group_nickname,answer), msg['FromUserName'])

@itchat.msg_register([RECORDING],isGroupChat=True)
def group_voice_chat(msg):
    chatroom_name = msg["User"]["NickName"]
    chatroom_id = msg['FromUserName']
    print "Receive a VOICE message from chatroom: RoomName(%s)/ID(%s)" % (chatroom_name,chatroom_id)
    if not chatroom_name in text_chatroom_names:
        return
    
    user_name = msg['ActualUserName'] 
    user_group_nickname = msg['ActualNickName']
    user_nickname = user_group_nickname
    user = itchat.search_friends(userName=user_name)
    if user:
        #print json.dumps(user).decode('unicode-escape')
        user_nickname = user["NickName"]
    print "The group message from user: NickName(%s)/GroupNickName(%s)/ID(%s)" % (user_nickname,user_group_nickname,user_name)
        
    if not user_nickname in voice_chatroom_user_nicknames:
        return
    msg['Text'](msg['FileName'])
    #itchat.send('@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']), msg['FromUserName'])
    audiofile = os.path.join(os.path.dirname(os.path.abspath(__file__)),msg['FileName'])
    #print audiofile
    text = app.transcribeAudio(audiofile)
    os.remove(audiofile)
    return u'%s刚才说: %s' % (user_nickname, text)

@itchat.msg_register(TEXT,isGroupChat=False)
def text_chat(msg):
    #print json.dumps(msg).decode('unicode-escape')
    try:
        user_nickname = msg["User"]['NickName']
    except KeyError, k:
        print 'Receive NEWS message, ignore!'
        return 
    
    user_name = msg['FromUserName'] 
    user = itchat.search_friends(userName=user_name)
    if user:
        #print json.dumps(user).decode('unicode-escape')
        if user["NickName"] == my_user_nickname:
            print "It is a message from myself to user: %s" % user_nickname
            return
    
    print "Receive a TEXT message from user: NickName(%s)/RemarkName(%s)/PYQuanPin(%s)/ID(%s)" % (user_nickname, msg["User"]['RemarkName'],msg["User"]['PYQuanPin'],user_name)
    if not user_nickname in text_user_nicknames:
        return
    
    message = msg['Text']
    answer = app.processText(user_name, message)
    itchat.send(u'%s: %s' % (user_nickname,answer), user_name)

@itchat.msg_register([RECORDING],isGroupChat=False)
def voice_chat(msg):
    user_nickname = msg["User"]['NickName']
    user_name = msg['FromUserName'] 
    user = itchat.search_friends(userName=user_name)
    if user:
        #print json.dumps(user).decode('unicode-escape')
        if user["NickName"] == my_user_nickname:
            print "It is a message from myself to user: %s" % user_nickname
            return
    
    print "Receive a VOICE message from user: NickName(%s)/RemarkName(%s)/PYQuanPin(%s)/ID(%s)" % (user_nickname, msg["User"]['RemarkName'],msg["User"]['PYQuanPin'], user_name)
    if not user_nickname in voice_user_nicknames:
        return
    msg['Text'](msg['FileName'])
    audiofile = os.path.join(os.path.dirname(os.path.abspath(__file__)),msg['FileName'])
    #print audiofile
    text = app.transcribeAudio(audiofile)
    os.remove(audiofile)
    answer = app.processText(user_name,text)
    return u'%s: %s\n%s: %s' % (user_nickname, text,my_user_nickname,answer)


try:
    itchat.auto_login(enableCmdQR=2,hotReload=True)
    chatrooms = itchat.get_chatrooms(update=True)
    print len(chatrooms)
    for chatroom in chatrooms:
        print chatroom['UserName'],chatroom['NickName']
    itchat.get_contact(update=True)
    itchat.get_friends(update=True)
    #friend = itchat.search_friends(userName="@6981d15fdba5b3aa91e0466472dc3ea347ee194733088a0d5d9c94ae42075bb4")
    #print json.dumps(friend).decode('unicode-escape')
    itchat.run()
except Exception, e:
    print 'repr(e):\t', repr(e)

