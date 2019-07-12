# -*- coding: utf-8 -*-
"""
@author: Maciej Ulaszewski
mail:ulaszewski.maciej@gmail.com
github: https://github.com/ulaszewskim
"""


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
from PIL import ImageTk, Image
import zipfile
import shutil
import operator
import requests
import bs4
from getpass import getuser

#============
#choose directory
#============
def choose_directory():
    directory = fd.askdirectory()
    folder_path.configure(state='normal')
    folder_path.delete(0,tk.END)
    folder_path.insert(tk.INSERT, directory)


#============
#Image Download
#============
def image_download(url, path, filename):

    
    if not os.path.exists(path+'/images/'):
        os.makedirs(path+'/images/')
    
    short_url="https://www.thesimsresource.com"
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    image_url = short_url+soup.find("a", class_= "magnific-gallery-image")['href']
    img = Image.open(requests.get(image_url, stream = True).raw)
    img.save(path+'/images/'+filename+'.jpg')


#============
#log window
#============
def log_window(window, text):
    window.configure(state='normal')
    window.insert(tk.INSERT, text+'\n')
    window.see(tk.END)
    window.configure(state='disabled')

#============
#label update
#============
def label_update(label, text):
    label.configure(text = text)
    label.update()


#============
#list files in directory
#============
def list_of_packages(path):
    files=[]
    try:
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                files.append(file)
    except:
        FileNotFoundError
    return files

#============
#last modified file in directory
#============
def last_modified(sciezka):
    packages = list_of_packages(sciezka)
    pack=[]
    for i in range(len(packages)):
        pack.append([packages[i],os.path.getmtime(sciezka+'/' + packages[i])])
    najnowszy=pack[0]
    for i in range(1,len(pack)):
        if pack[i][1]>najnowszy[1]:
            najnowszy = pack[i]
    return najnowszy


#============
#remove duplicate
#============
def remove_duplicate(sciezka):
    najnowszy=last_modified(sciezka)
    packages = list_of_packages(sciezka)
    for i in range(len(packages)):
        if najnowszy[0][:-12]+'.package'==packages[i]:
            os.remove(sciezka+'/'+najnowszy[0])
            log_window(status_window, "    File {} already exists. Deleted.".format(najnowszy[0]))


def remove_duplicate_image(sciezka):
    sciezka=sciezka+'/images'
    najnowszy=last_modified(sciezka)
    packages = list_of_packages(sciezka)
    for i in range(len(packages)):
        if najnowszy[0][:-16]+'.package.jpg'==packages[i]:
            os.remove(sciezka+'/'+najnowszy[0])
            log_window(status_window, "    File {} already exists. Deleted.".format(najnowszy[0]))


#============
#download
#input: url, download directory
#============
def download(url, sciezka):
    czas_start2 = time.time()
    czas = [60,60,10,10]
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : sciezka}
    #chromeOptions.add_argument('headless')
    chromeOptions.add_experimental_option("prefs",prefs)
    
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    
    browser.get(url)
    time.sleep(2)
    
    ciast_xp= '/html/body/div[1]/div/div[1]/div/button[2]'
    xp= "/html/body/div[8]/div[2]/div[1]/div[2]/div[3]/a[1]"
    
    element_present = EC.presence_of_element_located((By.XPATH, ciast_xp))
    WebDriverWait(browser, czas[0]).until(element_present)
    ciast = browser.find_element_by_xpath(ciast_xp)
    ciast.click()
    
    element_present = EC.presence_of_element_located((By.XPATH, xp))
    WebDriverWait(browser, czas[1]).until(element_present)
    download = browser.find_element_by_xpath(xp)
    browser.execute_script("$(arguments[0]).click();", download)
    
    for x in range(czas[2]):
        time.sleep(1)
    
    check_xp = '//*[@id="dllink"]'
    element_present = EC.presence_of_element_located((By.XPATH, check_xp))
    WebDriverWait(browser, czas[0]).until(element_present)
    
    #3 minutes to download
    x=0
    while x<180:
        if last_modified(sciezka)[0][-11:] != '.crdownload' and last_modified(sciezka)[0][-4:] != '.tmp' and last_modified(sciezka)[1]>czas_start2:
            log_window(status_window, "Downloaded: {}".format(last_modified(sciezka)[0]))
            x=181
            image_download(url,sciezka,last_modified(sciezka)[0])
            time.sleep(2)
            if last_modified(sciezka)[0][-4:] == '.zip':
                
                zip_ref = zipfile.ZipFile(sciezka+'/'+last_modified(sciezka)[0], 'r')
                nazwazip=last_modified(sciezka)[0]
                zip_ref.extractall(sciezka)
                
                ziplist=zipfile.ZipFile.namelist(zip_ref)
                for z in range(len(ziplist)):
                    log_window(status_window, "   Unziped: {}".format(ziplist[z]))
                for a in range(len(ziplist)):
                    shutil.copyfile(sciezka+'/images/'+nazwazip+'.jpg', sciezka+'/images/'+ziplist[a]+'.jpg')
                zip_ref.close()
                os.remove(sciezka+'/'+nazwazip)
                os.remove(sciezka+'/images/'+nazwazip+'.jpg')
                
            browser.close()
        else:
            time.sleep(1)
            x=x+1
    if x==180:
        log_window(status_window, "Timeout. File has not been downloaded..")
        browser.close()

    remove_duplicate(sciezka)
    remove_duplicate_image(sciezka)
    


#============
#START
#============
def start():
    #============
    #Disable window with urls
    #============
    links_list.configure(state='disabled')
    
    #============
    #Clear logs
    #============
    status_window.configure(state='normal')
    status_window.delete(1.0, tk.END)
    
    #============
    #Get urls list
    #============
    links = links_list.get(1.0, tk.END+'-1c')
    links = links.split('\n')
    while links.count('') > 0:
        links.remove('')
    log_window(status_window, "URLs: {}".format(len(links)))
    link_count.configure(text = 'URLs: {}'.format(len(links)))
    
    '''
    #============
    #Reload urls counter
    #============
    link_count.configure(text = 'URLs: {}'.format(len(links)))
    downloaded_count.configure(text = 'Downloaded: 0/{}'.format(len(links)))
    '''
    
    #============
    #Destination path
    #============
    path = folder_path.get()
    
    #============
    #Downloading
    #============
    for mod in range(len(links)):
        download(links[mod],path)
    

    #============
    #Enable window with urls
    #============
    links_list.configure(state='normal')
    bar['value']=100
    bar.update()
    refresh()



#============
#GUI
#============

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
import tkinter.filedialog as fd

win = tk.Tk()
win.title('The Sims 4 Mods Manager')
win.geometry('810x600+20+20')


#============
#tab1 - downloading
#============


#variables
path = tk.StringVar() #destination folder
links = tk.StringVar()


#bookmarks

tabControl = ttk.Notebook(win)

ptab = ttk.Frame(tabControl)
ztab = ttk.Frame(tabControl)
tabControl.add(ptab, text = "Download")

tabControl.add(ztab, text = "Manage")
tabControl.pack(expand=1, fill="both")


#Progresbar
bar=ttk.Progressbar(ptab, length=730)
bar['value'] = 0
bar.grid(column=0, row=0, columnspan=2, sticky='w', pady=5, padx=5)


#urls header
links_header = tk.Label(ptab, text='Paste URLs in new lines:', font=('',9))
links_header.grid(column=0, row=1, sticky = 'w')

#urls list
links_list = scrolledtext.ScrolledText(ptab, width=60, height=34, font=('',8))
links_list.grid(column=0, row=2, rowspan = 3, sticky='nw')

#directory with mods header
folder_header = tk.Label(ptab, text = "Mods path:", font=('',9))
folder_header.grid(column=1, row=1, sticky = 'w', padx=5)

#directory with mods 
folder_path = tk.Entry(ptab, width=57, state='normal', textvariable = path)
folder_path.grid(column=1, row=2, sticky = 'w',  padx=5)
folder_path.insert(tk.INSERT, 'C:/Users/{}/Documents/Electronic Arts/The Sims 4/Mods'.format(getuser()))
#folder_path.configure(state='disabled')

#select directory button
folder_btn = tk.Button(ptab, text = "Select", state='normal', command=choose_directory)
folder_btn.grid(column=3, row=2, sticky='w')


#log window header
status_header = tk.Label(ptab, text = "Logs:", font = ('',9))
status_header.grid(column=1, row=3, sticky='nw', padx=5)

#log window 
status_window = scrolledtext.ScrolledText(ptab, width=63, height=33, state='disabled', bg='lightgrey', font=('',8))
status_window.grid(column=1, row=4, columnspan=3, rowspan=8, sticky='nw', padx=5)
log_window(status_window, "In the window on the left paste URLs from thesimsrecource.com in new lines.\nFor example:\nhttps://www.thesimsresource.com/downloads/details/category/sims4-mods-poses/title/the-wall-and-me-pose-pack-1/id/1449049/\nhttps://www.thesimsresource.com/downloads/details/category/sims4-hair-facial-eyebrows/title/ea-n15-eyebrow-recolor/id/1447613/\netc.")

#start button
start_btn = tk.Button(ptab, text = 'Start', bg='lightgreen', font = ('',11), command=start)
start_btn.grid(column=3, row=0)


#URLs counter
link_count = tk.Label(ptab, text = 'URLs: ', font = ('',9))
link_count.grid(column=0, row=6, sticky='w')
'''
#downloaded counter
downloaded_count = tk.Label(ptab, text = 'Downloaded: ', font = ('',9))
downloaded_count.grid(column=0, row=10, sticky='w')
'''


#============
#tab2 - manage
#============
def files_with_time(sciezka):
    installed_list = list_of_packages(sciezka)
    
    installed_list_with_time=[]
    for i in range(len(installed_list)):
        installed_list_with_time.append([installed_list[i],os.path.getmtime(sciezka+'/' + installed_list[i])])
    list.sort(installed_list_with_time, key=operator.itemgetter(1), reverse=True)
    return installed_list_with_time


def refresh():
    list_box_update()
    select_images()


def delete():
    sciezka_plik = folder_path.get()+'/'
    sciezka_obraz = sciezka_plik+'/images/'
    checked = lb_check.get(0, tk.END)
    names = lb_name.get(0, tk.END)
    for i in range(len(names)):
        if checked[i] == "X":
            os.remove(sciezka_plik+names[i])
            if os.path.isfile(sciezka_obraz+names[i]+'.jpg'):
                os.remove(sciezka_obraz+names[i]+'.jpg')
    refresh()


def call_help():
    win = tk.Toplevel()
    win.title('Help')
    win.geometry('510x510+40+40')
    status_window = scrolledtext.ScrolledText(win, state='disabled', height=35,bg='white', font=('',8))
    status_window.grid(column=0, row=0,sticky='nw', padx=5)
    log_window(status_window, "HELP\n\nDownload:\nIn the window on the left paste URLs from thesimsrecource.com in new lines.\nEmpty lines does not matter.\n\n\nManage:\nTo scroll use only scrollbar!\n\nIn the column Delete double-click to select or deselect.\n\nThere is image to the mod if name of the mod is highlighted green.\nTo open image double-click on the name.\n\nRefresh button reloads list.\n\nDelete button deletes selected (higlighted red) mods.\nWARNING! Delete cannot be undone!\n\n\n\n@author: Maciej Ulaszewski\ngithub: https://github.com/ulaszewskim")


#scrollbar
frametwo = tk.Frame(ztab) 
frametwo.grid(row = 1, column = 0, columnspan=4, rowspan=10)
canvas = tk.Canvas(frametwo)
canvas_frame = tk.Frame(canvas)
canvas.grid(row=2, column=0, columnspan=5, sticky=tk.N+tk.S+tk.E+tk.W)


#scroll listboxes together
def yview(*args):
    lb_number.yview(*args)
    lb_check.yview(*args)
    lb_name.yview(*args)
    lb_time.yview(*args)

scrollbar = tk.Scrollbar(canvas, command=yview)
scrollbar.grid(row=1, column=6, sticky="ns")

def height():
    installed_list_with_time = files_with_time(folder_path.get())
    if len(installed_list_with_time) >34:
        h=34
    else:
        h=len(installed_list_with_time)
    h=34
    return h


#lists

lb_number_header = tk.Label(canvas, text='#')
lb_number_header.grid(column=0, row=0, sticky='w')

lb_number = tk.Listbox(canvas,width=3, height=height(), yscrollcommand=scrollbar.set)
lb_number.grid(column=0, row=1, sticky='n')


lb_check_header = tk.Label(canvas, text='Delete')
lb_check_header.grid(column=1, row=0, sticky='w')

lb_check = tk.Listbox(canvas, width=4, height=height(), yscrollcommand=scrollbar.set, justify='center')
lb_check.grid(column=1, row=1, sticky='n')


lb_name_header = tk.Label(canvas, text='Name')
lb_name_header.grid(column=2, row=0, sticky='w')

lb_name = tk.Listbox(canvas,width=85, height=height(), yscrollcommand=scrollbar.set)
lb_name.grid(column=2, row=1, sticky='n')


lb_time_header = tk.Label(canvas, text='Install date')
lb_time_header.grid(column=3, row=0,sticky='w')

lb_time = tk.Listbox(canvas, width=20, height=height(), yscrollcommand=scrollbar.set)
lb_time.grid(column=3, row=1, sticky='n')

#reload button
refresh_btn = tk.Button(ztab, text = "Reload", bg='lightblue', width=9, height=3,state='normal', command=refresh)
refresh_btn.grid(column=4, row=1, sticky='n', pady=10,padx=10)

#delete button
del_btn = tk.Button(ztab, text = "Delete", bg='red', width=9,height=3,state='normal', command=delete)
del_btn.grid(column=4, row=2, sticky='n', pady=10,padx=10)

#help button
help_btn = tk.Button(ztab, text = "Help", bg='pink', width=9,height=3,state='normal', command=call_help)
help_btn.grid(column=4, row=3, sticky='n', pady=10,padx=10)


def add_to_list(listbox, i, text):
    listbox.configure(state='normal')
    listbox.update()
    listbox.insert(i, text)
    listbox.configure(state='normal',disabledforeground="black")
    listbox.update()


def update_list(listbox, i, text):
    listbox.configure(state='normal')
    listbox.update()
    listbox.delete(i)
    listbox.insert(i, text)
    listbox.configure(state='normal',disabledforeground="black")
    listbox.update()


def list_box_update():
    lb_number.delete(0,tk.END)
    lb_check.delete(0,tk.END)
    lb_name.delete(0,tk.END)
    lb_time.delete(0,tk.END)
    installed_list_with_time = files_with_time(folder_path.get())
    for i in range(len(installed_list_with_time)):
        add_to_list(lb_number, i, i+1)
        add_to_list(lb_check,i,"")
        add_to_list(lb_name, i, installed_list_with_time[i][0])
        add_to_list(lb_time, i, time.strftime("%d %b %Y %H:%M:%S", time.localtime(installed_list_with_time[i][1])))


def select_name(evt):
    w = evt.widget
    value = w.get(tk.ACTIVE)
    sciezka=folder_path.get()
    obraz=sciezka+'/images/'+value+'.jpg'
    if os.path.isfile(obraz):
        
        img0=Image.open(obraz)
        w,h=img0.size
        w=int(w*2/3)
        h=int(h*2/3)
        imgres=img0.resize((w,h), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(imgres)
        novi = tk.Toplevel()
        novi.title(value)
        
        geom=str(w)+'x'+str(h)+'+30+30'
        novi.geometry(geom)
        
        panel = tk.Label(novi, image = img)
        panel.grid(column=0, row=0)
        canvas.create_image(50, 10, image = img, anchor ='nw')
        canvas.image = img


def select_check(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(tk.ACTIVE)
    if value=="":
        update_list(lb_check,index,"X")
        lb_number.itemconfig(index, fg='red')
        lb_check.itemconfig(index, fg='red')
        lb_name.itemconfig(index, fg='red')
        lb_time.itemconfig(index, fg='red')
    else:
        update_list(lb_check,index,"")
        lb_number.itemconfig(index, fg='black')
        lb_check.itemconfig(index, fg='black')
        lb_name.itemconfig(index, fg='black')
        lb_time.itemconfig(index, fg='black')


lb_check.bind('<Double-1>', select_check)
lb_name.bind('<Double-1>', select_name)

#highlight green
def select_images():
    installed_list_with_time = files_with_time(folder_path.get())
    for i in range(len(installed_list_with_time)):
        sciezka=folder_path.get()
        if os.path.isfile(sciezka+'/images/'+installed_list_with_time[i][0]+'.jpg'):
            lb_name.itemconfig(i, bg='lightgreen')


list_box_update()
select_images()

win.mainloop()
