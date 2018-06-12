import os, sys
import socket
import time
import tkMessageBox
import datetime
from Tkinter import *
import Tkinter


#	***   Functions part   ***

def make_remote_dir():
    global popup
    global entr

    popup = Tk()
    popup.title("New Directory")
    popup.geometry("260x120")
    popup.resizable(0, 0)

    Label(popup, text="Please select a name:").place(x=10, y=10)

    entr = Entry(popup, width=38, bd=1)
    entr.place(x=10, y=45)

    btn = Button(popup, text="OK", width=6, command=create_dir).place(x=10, y=80)
    return


def create_dir():
    global popup
    global entr
    global socket
    global sckt
    global currentRemoteDir

    newDirName = entr.get()
    popup.destroy()

    directory = newDirName
    path = currentRemoteDir + "/" + directory + "/"

    sckt.send("MKD " + path + '\n')
    rcmsg = sckt.recv(1024)  # catching respose code 

    write_to_list(logList, "Sent:             MKD " + path)
    write_to_list(logList, "Received:     " + rcmsg)
    return


def remove_remote_item():
    global socket
    global sckt
    global currentRemoteDir

    index = dstDirList.curselection()
    line = dstDirList.get(index)
    items = line.split(" ")
    totalen = len(items)
    itemIndex = totalen - 1

    #	items[0][0] holds "-" for file and "d" for directory 
    #	items[itemIndex] holds the file/dir name 

    if items[0][0] == "d":
        path = currentRemoteDir + "/" + items[itemIndex]

        sckt.send("RMD " + path + '\n')
        rcmsg = sckt.recv(1024)  # catching respose code 

        write_to_list(logList, "Sent:             RMD " + path)
        write_to_list(logList, "Received:     " + rcmsg)

    elif items[0][0] == "-":
        path = currentRemoteDir + "/" + items[itemIndex]

        sckt.send("DELE " + path + '\n')
        rcmsg = sckt.recv(1024)  # catching respose code 

        write_to_list(logList, "Sent:             DELE " + path)
        write_to_list(logList, "Received:     " + rcmsg)

    else:
        tkMessageBox.showerror("Error", "Unexpected error #002")
    return


def help_about():
    tkMessageBox.showinfo("About", "Version 1.0.0.1")
    return


def get_file(flag):
    #	flag = 1 for Get | 2 for Show 

    global currentLocalDir

    index = dstDirList.curselection()
    line = dstDirList.get(index)
    items = line.split(" ")
    totalen = len(items)
    itemIndex = totalen - 1

    if (flag == 1 and items[0][0] == "-"):  # items[0][0] holds "-" for file and "d" for directory 
        #	items[itemIndex] holds the file/dir name 
        fileContent = copy_file(items[itemIndex], 1)
        datafile = open(currentLocalDir + "\\" + items[itemIndex], "w")
        datafile.write(fileContent)
        datafile.close()

    elif (flag == 1 and items[0][0] == "d"):
        tkMessageBox.showinfo("Info", "You cannot copy full directory")

    elif (flag == 2 and items[0][0] == "-"):
        copy_file(items[itemIndex], 2)

    elif (flag == 2 and items[0][0] == "d"):
        navigate_to_directory(items[itemIndex])

    else:
        tkMessageBox.showerror("Error", "Unexpected error #001")

    return


def copy_file(fileName, flag):
    #	flag = 1 for Get | 2 for Show

    global socket
    global sckt
    global sckt2
    global currentRemoteDir

    create_ftp_data_connection()
    time.sleep(0.1)

    sckt.send("RETR " + currentRemoteDir + "/%s" % fileName + '\n')
    rcmsg = sckt.recv(1024)  # catching the: 150 Opening ASCII mode 
    rcmsg2 = sckt2.recv(2048)
    write_to_list(logList, "Sent:             RETR " + currentRemoteDir + "/%s" % fileName)
    write_to_list(logList, "Received:     " + rcmsg)
    write_to_list(logList, "Data ch:       ... Data is being transferred ...")
    sckt2.close()

    rcmsg = sckt.recv(1024)  # catching the: 226 Transfer Complete 
    write_to_list(logList, "Received:     " + rcmsg)

    prevList.delete(0, END)

    if flag == 1:  # Copy the file to the selected local directory 
        return rcmsg2;

    elif flag == 2:  # Show the file in the preview listbox 
        fileContent = rcmsg2.split("\r\n")
        for line1 in fileContent:
            write_to_list(prevList, line1)

    else:
        tkMessageBox.showerror("Error", "Unexpected error #003")

    return


def set_file():
    global socket
    global sckt
    global sckt2
    global currentRemoteDir
    global currentLocalDir

    index = locDirList.curselection()
    line = locDirList.get(index)

    if -1 == line.find("+", 0, 6):
        line = line.strip(' |+-')
        localPath = currentLocalDir + "\\" + line
        remotePath = currentRemoteDir + "/" + line

        print("local path: %s" % localPath)
        print("remote path: %s" % remotePath)

        sckt.send("STOR " + remotePath + '\n')
        rcmsg = sckt.recv(1024)  # catching
        write_to_list(logList, "Sent:             STOR " + remotePath)
        write_to_list(logList, "Received:     " + rcmsg)

        create_ftp_data_connection()




    elif -1 == line.find("-", 0, 6):
        tkMessageBox.showinfo("Info", "You cannot copy full directory")

    else:
        tkMessageBox.showerror("Error", "Unexpected error #004")

    return


def write_to_list(listName, string):
    listName.insert(END, string)

    return


def write_to_log_file(path, mode, text):
    logfile = open(path, mode)
    timestamp = str(datetime.datetime.now())
    logfile.write(timestamp + "\t" + text)
    logfile.write("\r\n")
    logfile.close()

    return


def connect():
    global socket
    global sckt
    global mode

    host = hostEntry.get()
    user = userEntry.get()
    pswd = passEntry.get()
    port = portEntry.get()
    mode = "PASV"

    if port == "":
        port = 21

    if host == "":
        host = "ftp.mcafee.com"

    if user == "":
        user = "anonymous"

    if pswd == "":
        pswd = "john"

    # print	"host: %s\nuser: %s\npswd: %s\nport: %s\nmode: %s" % (host, user, pswd, port, mode)
    write_to_list(logList, "Connect:      host: %s  |  user: %s  |  pass: %s  |  port: %s  |  mode: %s" % (
    host, user, pswd, port, mode))

    local_site_dir_tree(currentLocalDir)
    dstDirList.delete(0, END)
    create_ftp_control_connection(host, port)
    send_user_pass(user, pswd)
    sys_info()
    pwd()
    create_ftp_data_connection()
    show_directory_content()

    return


def local_site_dir_tree(path):
    global currentLocalDir

    locDirList.delete(0, END)
    dir = os.listdir(path)

    write_to_list(locDirList, "-%s" % path)

    for item in dir:
        if os.path.isfile(os.path.join(path, item)):
            write_to_list(locDirList, "    |-%s" % item)

        else:
            write_to_list(locDirList, "    |+%s" % item)

    currentLocalDir = path
    displayCurrentLocDir = currentLocalDir.replace("\\\\", "\\")

    localDir.delete(0, END)
    localDir.insert(0, displayCurrentLocDir)

    return


def create_ftp_control_connection(host, port):
    global socket
    global sckt

    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((host, port))

    hndl = handle("220")

    key = hndl[0]
    val = hndl[1]

    if key == 1:
        write_to_log_file(logFilePath, "a", "Connected server successfully\t%s" % val)
        return

    elif key == 0:
        write_to_log_file(logFilePath, "a", "Unable to connect server\t%s" % val)
        return

    else:
        write_to_log_file(logFilePath, "a", "Unexpected error from server\t%s" % val)
        return

    return


def handle(code):
    global socket
    global sckt

    rcmsg = sckt.recv(1024)
    splitMsg = rcmsg.split("\r\n")
    for x in splitMsg:
        if x != "":
            write_to_list(logList, "Received:     " + x)
    rCode = rcmsg.find(code)

    if rCode == 0:
        lst = [1, rcmsg]
        write_to_log_file(logFilePath, "a", "Handle OK:\tCode %s\tReceived %s" % (code, rcmsg))

    else:
        lst = [1, rcmsg]
        write_to_log_file(logFilePath, "a", "Handle KO:\tCode %s\tReceived %s" % (code, rcmsg))

    return lst


def send_user_pass(user, pswd):
    global socket
    global sckt

    sckt.send("USER " + user + '\n')
    write_to_list(logList, "Sent:             " + "USER " + user)
    hndl = handle("331")

    key1 = hndl[0]
    val1 = hndl[1]

    if key1 == 1:
        write_to_log_file(logFilePath, "a", "Received expected 331 code for user input\t%s" % val1)
        sckt.send("PASS " + pswd + '\n')
        write_to_list(logList, "Sent:             " + "PASS " + pswd)

        hndl2 = handle("230")

        key2 = hndl2[0]
        val2 = hndl2[1]

        if key2 == 1:
            write_to_log_file(logFilePath, "a", "Logged-in successfully\t\t\t\t%s" % val2)
            return
        elif key2 == 0:
            write_to_log_file(logFilePath, "a", "Password was rejected. Did not receive the expected 230 code\t%s" % val2)
        else:
            write_to_log_file(logFilePath, "a", "Unexpected error code for password\t\t%s" % val2)



    elif key1 == 0:
        write_to_log_file(logFilePath, "a", "Username was rejected. Did not receive the expected 331 code\t%s" % val1)
    else:
        write_to_log_file(logFilePath, "a", "Unexpected error code for username\t%s" % val1)

    return


def sys_info():
    global socket
    global sckt

    sckt.send("SYST\n")
    write_to_list(logList, "Sent:             SYST")
    hndl = handle("215")
    key = hndl[0]
    val = hndl[1]

    return


def navigate_to_directory(directory):
    global socket
    global sckt
    global currentRemoteDir

    sckt.send("CWD " + currentRemoteDir + "/" + directory + "/\n")
    write_to_list(logList, "Sent:             CWD /%s/" % directory)
    hndl = handle("250")

    if hndl[0] == 1:
        # print "handle CWD successfully"
        create_ftp_data_connection()
        dstDirList.delete(0, END)
        show_directory_content()
        pwd()

    elif hndl[0] == 0:
        print("Did not receive the expected 250 code")
        time.sleep(3)

    else:
        print("Unexpected error")
        time.sleep(3)

    return


def create_ftp_data_connection():
    global socket
    global sckt
    global sckt2

    sckt.send("PASV\n")
    write_to_list(logList, "Sent:             PASV")
    DataSocket = get_PASV_reply()

    if (DataSocket[0] != 0 and DataSocket[1] != 0):
        sckt2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt2.connect((DataSocket[0], DataSocket[1]))

    else:
        write_to_log_file(logFilePath, "a", "Cannot Open FTP data channel")

    return DataSocket


def get_PASV_reply():
    rcmsg = sckt.recv(1024)
    write_to_list(logList, "Received:     " + rcmsg)
    rCode = rcmsg.find('227')

    if rCode == 0:
        str1 = []
        str1 = rcmsg.split()

        sock = str1[4]
        sock = sock.strip('(')
        sock = sock.strip(')')
        lst1 = sock.split(",")

        ipaddr = lst1[0] + "." + lst1[1] + "." + lst1[2] + "." + lst1[3]
        tcpprt = int(lst1[4]) * 256 + int(lst1[5])

        ipaddr = str(ipaddr)
        tcpprt = int(tcpprt)

        lst = [ipaddr, tcpprt]

        write_to_list(logList, "                     (Socket for data channel is: " + ipaddr + " : " + str(tcpprt) + ")")
        write_to_log_file(logFilePath, "a", "Socket for data channel is:\t%s:%s" % (ipaddr, tcpprt))


    else:
        write_to_list(logList, "                     Did not find the expected code 227 for PASV command")
        write_to_log_file(logFilePath, "a", "Did not find the expected code 227 for PASV command")
        lst = [0, 0]

    return lst


def show_directory_content():
    global socket
    global sckt
    global sckt2

    sckt.send("LIST -l" + '\n')
    rcmsg = sckt.recv(1024)  # catching the: 150 Opening ASCII mode
    rcmsg2 = sckt2.recv(2048)

    write_to_list(logList, "Sent:             LIST -l")
    write_to_list(logList, "Received:     " + rcmsg)
    write_to_list(logList, "Data ch:       ... Data is being transferred ...")

    ftpdata = rcmsg2.split("\r\n")

    for directory in ftpdata:
        write_to_list(dstDirList, directory)

    rcmsg = sckt.recv(1024)  # catching the: 226 Transfer Complete 
    write_to_list(logList, "Received:     " + rcmsg)

    return


def on_double_remote(event):
    global currentLocalDir

    index = dstDirList.curselection()
    line = dstDirList.get(index)
    items = line.split(" ")
    totalen = len(items)
    itemIndex = totalen - 1

    if items[0][0] == "-":
        copy_file(items[itemIndex], 2)

    elif items[0][0] == "d":
        navigate_to_directory(items[itemIndex])

    else:
        tkMessageBox.showerror("Error", "Unexpected error #001")

    return


def create_log_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

    else:
        pass

    return


def go_back():
    global socket
    global sckt
    global currentRemoteDir

    sckt.send("CDUP\n")
    write_to_list(logList, "Sent:             CDUP")
    hndl = handle("250")

    dstDirList.delete(0, END)
    create_ftp_data_connection()
    show_directory_content()
    currentRemoteDir = pwd()

    return


def pwd():
    global socket
    global sckt
    global currentRemoteDir

    sckt.send("PWD\n")
    write_to_list(logList, "Sent:             PWD")
    hndl = handle("257")

    items = hndl[1].split(" ")
    items[1] = items[1].strip('"')
    remoteDir.delete(0, END)
    remoteDir.insert(0, items[1])

    currentRemoteDir = items[1]

    return items[1]


def go_back_local():
    global currentLocalDir

    path = currentLocalDir

    if path == "C:\\":
        return

    while 1:
        path = path[:-1]

        if "\\" == path[-1:]:
            # print "Final Path: %s" % path
            break

    path = path[:-1]
    local_site_dir_tree(path)

    return


def on_double_local(event):
    index = locDirList.curselection()
    line = locDirList.get(index)

    if -1 == line.find("+", 0, 6):
        print("This is a file")

    else:
        # print "This is a directory"
        line = line.strip(' |+-')
        newPath = currentLocalDir + "\\" + line + "\\"
        local_site_dir_tree(newPath)

    return


def delete_item():
    index = locDirList.curselection()
    line = locDirList.get(index)

    if -1 == line.find("+", 0, 6):
        line = line.strip(' |+-')
        delPath = currentLocalDir + "\\" + line

        if os.path.exists(delPath):
            reply = tkMessageBox.askquestion("Delete %s" % line, "Are you sure that you want to delete %s ?" % line)
            if reply == "yes":
                os.remove(delPath)

            elif reply == "no":
                pass

            else:
                tkMessageBox.showerror("Error", "Unexpected error #005")

    return


def remote_context_m(event, menu):
    index = dstDirList.curselection()
    line = dstDirList.get(index)
    menu.post(event.x_root, event.y_root)

    return


def local_context_m(event, menu):
    # nearIndex	=	locDirList.nearest(event.y)
    index = locDirList.curselection()
    line = locDirList.get(index)
    menu.post(event.x_root, event.y_root)

    return


#	***********************************************************
#	************        Program Starts Here        ************
#	***********************************************************


global logFilePath
global currentRemoteDir
global currentLocalDir

currentLocalDir = "C:\\"

logFileDir = "C:\\PythonLogs"
create_log_dir(logFileDir)
logFilePath = logFileDir + "\\LogFile.txt"
write_to_log_file(logFilePath, "w", "***    Program Started    ***")

# window = Tkinter.Tk()
window = Tk()
window.title("FTP Client Application")
window.geometry("1000x730")
window.resizable(0, 0)  # Disable resizing 

bgColor = "#AAFFAA"  # "#EFEFEF"
btnColor = "#55AAFF"
cntColor = "#FF9010"
pathColor = "#0000FF"

cnvs = Canvas(window, width=1000, height=600, bg=bgColor)
cnvs.pack(expand=YES, fill=BOTH)

#	***   Creating menu bar   *** 
mnb1 = Menu(window, bg=bgColor)

filemenu = Menu(mnb1, tearoff=0)
mnb1.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New")
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_command(label="Save as...")
filemenu.add_command(label="Close")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)

editmenu = Menu(mnb1, tearoff=0)
mnb1.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Undo")
editmenu.add_separator()
editmenu.add_command(label="Cut")
editmenu.add_command(label="Copy")
editmenu.add_command(label="Paste")
editmenu.add_command(label="Delete")
editmenu.add_command(label="Select All")

trnsmenu = Menu(mnb1, tearoff=0)
mnb1.add_cascade(label="Transfer", menu=trnsmenu)
trnsmenu.add_command(label="Pending")
trnsmenu.add_command(label="In progress")
trnsmenu.add_command(label="Done")

srvrmenu = Menu(mnb1, tearoff=0)
mnb1.add_cascade(label="Server", menu=srvrmenu)
srvrmenu.add_command(label="Network")

helpmenu = Menu(mnb1, tearoff=0)
mnb1.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Help")
helpmenu.add_command(label="About", command=help_about)

window.config(menu=mnb1)

#	***   Adding Top menu buttons   *** 
saveBtn = Button(window, width=6, text="MkDir", command=make_remote_dir, bg=btnColor)
saveBtn.place(x=0, y=0)

refBtn = Button(window, width=6, text="RmDir", bg=btnColor)
refBtn.place(x=53, y=0)

togBtn = Button(window, width=6, text="Delete", bg=btnColor)
togBtn.place(x=106, y=0)

#	***   Top menu Server access details bar 

hostLabel = Label(window, text="Host:", bg=bgColor)
hostLabel.place(x=0, y=37)
hostEntry = Entry(window, width=20)
hostEntry.place(x=37, y=37)

userLabel = Label(window, text="Username:", bg=bgColor)
userLabel.place(x=190, y=37)
userEntry = Entry(window, width=20)
userEntry.place(x=256, y=37)

passLabel = Label(window, text="Password:", bg=bgColor)
passLabel.place(x=415, y=37)
passEntry = Entry(window, width=20)
passEntry.place(x=480, y=37)

portLabel = Label(window, text="Port:", bg=bgColor)
portLabel.place(x=640, y=37)
portEntry = Entry(window, width=6)
portEntry.place(x=670, y=37)

connectBtn = Button(window, width=10, text="Connect", bg=cntColor, command=connect)
connectBtn.place(x=730, y=33)

#	***   Frames and Listboxes  

frameLog = Frame(window, width=996, height=100, bg="#FFFFFF")
frameLog.place(x=2, y=65)
scroll = Scrollbar(frameLog, orient=VERTICAL)
logList = Listbox(frameLog, width=162, height=6, bg="#FFFFFF", yscrollcommand=scroll.set)
scroll.config(command=logList.yview)
scroll.pack(side=RIGHT, fill=Y)
logList.pack(side=LEFT, fill=BOTH, expand=1)

#	***	Local Site Directories ***
frameLocDir = Frame(window, width=450, height=200, bg="#FFFFFF")
frameLocDir.place(x=2, y=210)
scrollLoc = Scrollbar(frameLocDir, orient=VERTICAL)
locDirList = Listbox(frameLocDir, width=72, height=12, bg="#FFFFFF", yscrollcommand=scrollLoc.set)
scrollLoc.config(command=locDirList.yview)
scrollLoc.pack(side=RIGHT, fill=Y)
locDirList.pack(side=LEFT, fill=BOTH, expand=1)
Label(window, text="Local Site:", bg=bgColor).place(x=2, y=189)
localDir = Entry(window, width=45, bg=bgColor, fg=pathColor, bd=0)
localDir.place(x=70, y=189)
locDirList.bind("<Double-Button-1>", on_double_local)
locDirList.bind("<Button-3>", lambda evt: local_context_m(evt, localDirContextMenu))

localDirContextMenu = Menu()
localDirContextMenu.add_command(label='Transfer')
localDirContextMenu.add_command(label='Refresh', command=lambda: local_site_dir_tree(currentLocalDir))
localDirContextMenu.add_command(label='Rename')
localDirContextMenu.add_separator()
localDirContextMenu.add_command(label='Delete', command=delete_item)
localDirContextMenu.add_separator()
localDirContextMenu.add_command(label='New Folder')

#	***	Remote Site Directories ***
frameDstDir = Frame(window, width=450, height=200, bg="#FFFFFF")
frameDstDir.place(x=543, y=210)
scrollDst = Scrollbar(frameDstDir, orient=VERTICAL)
dstDirList = Listbox(frameDstDir, width=72, height=12, bg="#FFFFFF", yscrollcommand=scrollDst.set)
scrollDst.config(command=dstDirList.yview)
scrollDst.pack(side=RIGHT, fill=Y)
dstDirList.pack(side=LEFT, fill=BOTH, expand=1)
Label(window, text="Remote Site:", bg=bgColor).place(x=543, y=189)
remoteDir = Entry(window, width=45, bg=bgColor, fg=pathColor, bd=0)
remoteDir.place(x=623, y=189)
dstDirList.bind("<Double-Button-1>", on_double_remote)
dstDirList.bind("<Button-3>", lambda evt: remote_context_m(evt, destDirContextMenu))

destDirContextMenu = Menu()
destDirContextMenu.add_command(label='Show', command=lambda: get_file(2))
destDirContextMenu.add_command(label='Get', command=lambda: get_file(1))
destDirContextMenu.add_separator()
destDirContextMenu.add_command(label='Delete', command=remove_remote_item)
destDirContextMenu.add_separator()
destDirContextMenu.add_command(label='New Directory', command=make_remote_dir)

#	***	Preview Window ***
framePrev = Frame(window, width=450, height=230, bg="#FFFFFF")
framePrev.place(x=543, y=460)
scrollPrev = Scrollbar(framePrev, orient=VERTICAL)
prevList = Listbox(framePrev, width=72, height=15, bg="#FFFFFF", yscrollcommand=scrollPrev.set)
scrollPrev.config(command=prevList.yview)
scrollPrev.pack(side=RIGHT, fill=Y)
prevList.pack(side=LEFT, fill=BOTH, expand=1)
Label(window, text="Preview", bg=bgColor).place(x=543, y=439)

#	***   Get/Set/Back/Show/Open buttons   

getBtn = Button(window, width=6, text="<- Get", command=lambda: get_file(1), bg=btnColor)
getBtn.place(x=474, y=236)

showBtn = Button(window, width=6, text="Show", command=lambda: get_file(2), bg=btnColor)
showBtn.place(x=474, y=293)

setBtn = Button(window, width=6, text="Set ->", command=set_file, bg=btnColor)
setBtn.place(x=474, y=350)

bck1Btn = Button(window, width=6, text="^ Back", command=go_back, bg=btnColor)
bck1Btn.place(x=925, y=182)

bck2Btn = Button(window, width=6, text="^ Back", command=go_back_local, bg=btnColor)
bck2Btn.place(x=384, y=182)

# opnBtn = Button(window, width = 6, text = "Open", bg=btnColor)
# opnBtn.place(x = 109 , y = 409)

refBtn = Button(window, width=6, text="Refresh", command=lambda: local_site_dir_tree(currentLocalDir), bg=btnColor)
refBtn.place(x=3, y=409)

delBtn = Button(window, width=6, text="Delete", command=delete_item, bg=btnColor)
delBtn.place(x=56, y=409)

window.mainloop()
