from tkinter import *
import requests
import xmltodict

# Inloggegevens van de NS API
inlogGegevens = ('indy.sterk@student.hu.nl', 'ALvg1w3M5QqXBdYxLe6tSRCrU9QicAjnMVviHTsI15brq8Y6qgQ8cQ')
response = requests.get('http://webservices.ns.nl/ns-api-stations-v2', auth=inlogGegevens)


# Maakt van alle vertrektijden strings en zet deze in een lijst en returnt deze lijst.
def vertrek_tijden(code):
    api_url = 'http://webservices.ns.nl/ns-api-avt?station=' + code
    response = requests.get(api_url, auth=inlogGegevens)
    vertrekXML = xmltodict.parse(response.text)
    vertrek_list = []
    for vertrek in vertrekXML['ActueleVertrekTijden']['VertrekkendeTrein']:
        str = vertrek['EindBestemming'] + ';'
        str += vertrek['VertrekTijd'][11:16] + ';'
        str += vertrek['TreinSoort'] + ';'
        # Bij sommige vertrektijden is er geen spoor bekend. Als oplossing gebruiken we try/except.
        try:
            str += vertrek['VertrekSpoor']['#text']
        except:
            str += ''
        vertrek_list.append(str)
    return vertrek_list


# Maakt van alle vertrektijden strings en zet deze in een lijst en returnt deze lijst.
def storingen(code):
    api_url = 'http://webservices.ns.nl/ns-api-storingen?station=' + code
    response = requests.get(api_url, auth=inlogGegevens)
    storingXML = xmltodict.parse(response.text)
    storing_list = []
    if storingXML['Storingen']['Gepland'] != None:
        storing_list.append('Werkzaamheden')
        if type(storingXML['Storingen']['Gepland']['Storing']) == list:
            for storing in storingXML['Storingen']['Gepland']['Storing']:
                storing_list.append(storing['Traject'] + ' ' + storing['Periode'])
        else:
            storing_list.append(storingXML['Storingen']['Gepland']['Storing']['Traject'] + ' ' +
                               storingXML['Storingen']['Gepland']['Storing']['Periode'])

    if storingXML['Storingen']['Ongepland'] != None:
        storing_list.append('')
        storing_list.append('Ongeplande storingen')
        if type(storingXML['Storingen']['Ongepland']['Storing']) == list:
            x = storingXML['Storingen']['Ongepland']['Storing'][0]
            storing_list.append(x['Traject'] + ' ' + x['Reden'])
        else:
            x = storingXML['Storingen']['Ongepland']['Storing']
            storing_list.append(x['Traject'] + ' ' + x['Reden'])

    return storing_list


# Opent een scherm met vertrektijden van het huidigestation (in ons geval Ut)
def reis_informatie(code):
    infoFrame = Frame(width=1280,
                      height=720,
                      bg="Gold")
    listBox = Listbox(infoFrame,
                      height=25,
                      width=128,
                      font=('Consolas', 14),
                      bg='Gold')
    # for loop die de juiste tijden ophaalt via de functie vertrek_tijden() om ze in een ListBox te plaatsen met de juiste opmaak door middel van make_string()
    for tijd in vertrek_tijden(code):
        listBox.insert(END, make_string(tijd))
    listBox.insert(END, '')
    # dezelfde for loop voor de functie storingen()
    for storing in storingen(code):
        listBox.insert(END, storing)
    listBox.place(x=0, y=25)
    infoLabel = Label(master=infoFrame,
                      text=make_string('Bestemming;Tijd;Type;Spoor'),
                      fg='Navy',
                      font=('Consolas', 14, 'bold'),
                      bg='Gold',
                      width=108)
    infoLabel.place(x=0, y=0)
    # Button om terug te keren naar het hoofdmenu
    back = Button(master=infoFrame,
                  text='Terug',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2,
                  command=infoFrame.destroy)
    back.place(x=1000, y=610)
    infoFrame.place(x=0, y=0)


# Roept reis_informatie() aan voor ons huidgige station met de code van Utrecht
def reis_info_utrecht():
    reis_informatie('ut')


# opent een frame om een stationsnaam in te voeren
def reis_info_ander():
    # deze functie kijkt of de invoer juist is. zo ja sluit ie zijn eigen frame en roept reisInformatie() aan met de bijhoorende code
    def check_station():
        found = ''
        for naam in station_dict:
            if naam == textInvoer.get():
                found = naam
                break
        if found == '':
            melding = Label(master=selectFrame,
                            text='Dit is geen geldig station!,\n bedoelde u:',
                            bg="Gold",
                            fg="Black",
                            font=('Helvetica', 20, 'bold'),
                            width=30,
                            height=3)
            melding.place(x=50, y=110)
            listBox = Listbox(master=selectFrame,
                              height=10,
                              width=30,
                              selectborderwidth=0,
                              fg='Black',
                              font=('Helvetica', 20, 'bold'),
                              bg='Gold')
            for naam in station_dict:
                if textInvoer.get() in naam:
                    listBox.insert(END, naam)
            listBox.place(x=500, y=110)
        else:
            reis_informatie(station_dict[found])
            selectFrame.destroy()

    # Het frame met de textinvoer en de buttons
    selectFrame = Frame(width=1280,
                        height=720,
                        bg="Gold")
    textInvoer = Entry(master=selectFrame,
                       font=('Helvetica', 34))
    textInvoer.place(x=50, y=50)
    goButton = Button(master=selectFrame, text='>',
                      bg="Navy",
                      fg="White",
                      activebackground="Navy",
                      activeforeground="White",
                      font=('Helvetica', 19, 'bold'),
                      width=7,
                      height=1,
                      command=check_station)
    goButton.place(x=550, y=50)
    back = Button(master=selectFrame, text='Terug',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2,
                  command=selectFrame.destroy)
    back.place(x=1000, y=500)
    selectFrame.place(x=0, y=0)


# Maakt spaties tussen de string om het geordend te houden
def make_string(inputString):
    outputString = ''
    for word in inputString.split(';'):
        while len(word) < 27:
            word += ' '
        outputString += word
    return outputString


# Maakt een dictionary van alle stationsnamen en de bijhoorende codes.
station_dict = {}
for station in xmltodict.parse(response.text)['Stations']['Station']:
    station_dict[station['Namen']['Lang']] = station['Code']

# Zet de juiste afmetingen voor het TK window met de buttons en labels van het startscherm.
root = Tk()
root.geometry("1280x720")
root.configure(background='Gold')


b=Button(root,justify = LEFT)
photo=PhotoImage(file="nstrein.png")
b.config(image=photo,width="250",height="250")
b.place(x=510, y= 180)
b=DISABLED

# Titel boven aan het scherm: Welkom NS
title = Label(master=root,
              text='Welkom bij NS',
              bg="Gold",
              fg="navy",
              font=('Helvetica', 72, 'bold'),
              width=14,
              height=1)
title.pack()
# Buttons die geen functie hebben.
button01 = Button(master=root,
                  text='Ik wil naar \nAmsterdam',
                  bg="Navy",
                  fg="White",
                  activebackground="Blue",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2, )
button01.place(x=60, y=500)
button02 = Button(master=root,
                  text='Kopen \nlos kaartje',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2)
button02.place(x=260, y=500)
button03 = Button(master=root,
                  text='Kopen \nOV-Chipkaart',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2)
button03.place(x=460, y=500)
button04 = Button(master=root,
                  text='Ik wil naar \nhet buitenland',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2)
button04.place(x=660, y=500)

# Button voor functie reisinformatie  Utrecht.
button05 = Button(master=root,
                  text='Reisinformatie \nUtrecht',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2,
                  command=reis_info_utrecht)
button05.place(x=860, y=500)

# Button die functie voor andercstation opent.
button06 = Button(master=root,
                  text='Reisinformatie \nander station',
                  bg="Navy",
                  fg="White",
                  activebackground="Navy",
                  activeforeground="White",
                  font=('Helvetica', 14, 'bold'),
                  width=14,
                  height=2,
                  command=reis_info_ander)
button06.place(x=1060, y=500)

# start de mainloop van TKinter
root.mainloop()
