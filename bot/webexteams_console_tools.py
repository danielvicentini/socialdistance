# -*- coding: utf-8 -*-

from webexteams import getwebexRoomID, getwebexUserID, CleanUpWebhook, DeleteWebhook, CriaWebhook, WebexIncUser, webexmsgRoom, webexRoomsList, WebexRoomDel

def webexconsole(box):

    #################################################################
    # admin Console tools
    # webhook and rooms management (create, delete, etc)
     
    if box == "help+":
       msg="Available commands:\nuserid: Identifies userId\nroomid: Identifies roomid\nusermail: change user\nnovasala: Creates new room with an user\nremovesala: Deletes room\nsalas: lists all roms usermail belongs to\n"
       msg=msg+("webhook_create: creates webhook\nwebhook_del: deletes webhook\nwebhook_clean: lists webhooks and deletes disabled ones\n")
       print (msg)

    #gets usermail
    if box=="usermail":
        usermail=input("your email>")

    # find webex userid
    if box == "userid":
       email=input("Usermail:")
       msg = getwebexUserID(email)
       print (msg)

    # find room nome
    if box == "roomid":
        sala=input("Room Name? (type at least a piece of the room's name):")
        msg = getwebexRoomID(sala)
        print (msg)

    # Webhooks cleaning
    # list webhooks, delete the disabled ones
    if box =="webhook_clean":
        msg=CleanUpWebhook()
        print(msg)

	# Delete a specific webhook
    if box =="webhook_del":
        nome=input("webhook name:")
        msg=DeleteWebhook(nome)
        print(msg)

    # Create webhook
    if box =="webhook_create":
       nome=input("webhook tag:")
       url=input("webhook http address:")
       msg=CriaWebhook(nome,url)
       print(msg)

	# Create a room and includes an user 
    if box == "novasala":
       email=input ("usermail to be included:")
       msg=getwebexUserID(email)

       if msg!="erro":
           novasala=input ('Room name:')
           msg=WebexIncUser(novasala,email)
           webexmsgRoom(novasala,"Hello' "+str(email))
       else:
            msg="usermail not identified."

       print(msg)

    # Deletes a room
    if box == "removesala":
        nome_sala=input('Room name:')
        msg=WebexRoomDel(getwebexRoomID(nome_sala))
        print(msg)

    # List all Rooms
    if box =="salas":
        msg = webexRoomsList()
        print (msg)
            
    # END Admin console tools options
    #################################################################

    return