# -*- coding: utf-8 -*-
#  Copyright (c) 2019.
#  Hegedűs István
#  +36-20/969-7089
#  SolarPanelSystemSOFT
from getmac import get_mac_address
from tkinter import Tk, Menu, IntVar, StringVar, Label, Entry, Frame, Button, Radiobutton, Toplevel, filedialog, ttk, \
    END, LabelFrame, messagebox
from tkinter.ttk import Combobox
from math import ceil
import sqlite3 as db
from PIL import Image, ImageTk
from fpdf import FPDF
from datetime import datetime
import datetime
from os import getcwd, startfile, path
import pandas as pd

conn = db.connect('db/elmu.dll')
cur = conn.cursor()


# új ablakot nyit az adatbázis frissítéséhez
# excel fájlokból kinyeri az adatokat, összefűzi és menti sql adatbázisba
def adatbazis_frissites():
    class Root(Tk):
        def __init__(self):
            super(Root, self).__init__()
            self.title("Excel fájl kiválasztása")
            self.win_width = 550
            self.win_height = 220
            self.x_location = int(win.winfo_vrootwidth() / 2 - self.win_width / 2)
            self.y_location = '+150'
            self.program_location = str(self.x_location) + self.y_location
            self.geometry(str(self.win_width) + 'x' + str(self.win_height) + '+' + self.program_location)
            self.resizable(width=False, height=False)
            self.configure(bg="gray35")
            self.minsize(550, 220)
            self.maxsize(550, 220)
            self.iconbitmap(bitmap="hmke.ico")
            self.focus_force()

            self.labelFrame = LabelFrame(self, text="Fájl kiválasztása", background="gray35", fg="white")
            self.labelFrame.grid(column=1, row=1, padx=20, pady=20)

            self.button()

        def button(self):
            self.entry = ttk.Entry(self.labelFrame, width=80, state='readonly')
            self.entry.grid(column=0, row=1, pady=20, padx=10)
            self.button = ttk.Button(self.labelFrame, text="Fájl megnyitása és az adatbázis frissítése",
                                     command=self.fileDialog)
            self.button.grid(column=0, row=2, sticky='w', pady=10, padx=10)
            self.label = Label(self.labelFrame, text='', bg="gray35")
            self.label.grid(column=0, row=3, sticky='w', pady=10, padx=10)

        def fileDialog(self):
            self.label.configure(text='')
            self.entry.configure(state='normal')
            self.entry.delete(0, END)
            self.filename = filedialog.askopenfilename(initialdir="/", title="Fájl kiválasztása",
                                                       filetype=(("xlsx files", "*.xlsx"), ("all files", "*.*")))
            fajl = self.filename
            self.entry.insert(0, fajl)
            self.entry.configure(state='readonly')
            Root.focus_force(self)
            self.fajlnev()

        def fajlnev(self):
            global tuzes, df15, df10, df5, tableBaseName, uj_falj_nev, inv_neve

            # print(fajl_neve)
            try:
                fajl_neve = self.entry.get()
                darabolt_fajlknev = str(fajl_neve).split("/")

                xlsx_fajl_neve = darabolt_fajlknev[-1]
                xlsx_fajl_neve_darabolva = xlsx_fajl_neve.split("_")

                if xlsx_fajl_neve_darabolva[1] == "GROWATT":
                    inv_neve = "Growatt"
                if xlsx_fajl_neve_darabolva[1] == "FRONIUS":
                    inv_neve = "Fronius"
                if xlsx_fajl_neve_darabolva[1] == "SOLAREDGE":
                    inv_neve = "SolarEdge"

                if xlsx_fajl_neve_darabolva[-1] != "Tűzesetis.xlsx":
                    sheet_name_5 = inv_neve + " " + xlsx_fajl_neve_darabolva[4] + "Wp 20+5%"
                    sheet_name_10 = inv_neve + " " + xlsx_fajl_neve_darabolva[4] + "Wp 20+10%"
                    sheet_name_15 = inv_neve + " " + xlsx_fajl_neve_darabolva[4] + "Wp 20+15%"
                    tuzes = 0
                    uj_falj_nev = xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[4] + ".xlsx"

                    df15 = pd.read_excel(fajl_neve, sheet_name_15, skiprows=1)
                    df10 = pd.read_excel(fajl_neve, sheet_name_10, skiprows=1)
                    df5 = pd.read_excel(fajl_neve, sheet_name_5, skiprows=1)

                if xlsx_fajl_neve_darabolva[-1] == "Tűzesetis.xlsx":
                    sheet_name_5 = inv_neve + " " + xlsx_fajl_neve_darabolva[4] + "Wp 20+5% TELK"
                    sheet_name_10 = inv_neve + " " + xlsx_fajl_neve_darabolva[4] + "Wp 20+10% TELK"
                    sheet_name_15 = inv_neve + " " + xlsx_fajl_neve_darabolva[4] + "Wp 20+15% TELK"
                    tuzes = 1
                    uj_falj_nev = xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[4] + "_T.xlsx"

                    df15 = pd.read_excel(fajl_neve, sheet_name_15, skiprows=1)
                    df10 = pd.read_excel(fajl_neve, sheet_name_10, skiprows=1)
                    df5 = pd.read_excel(fajl_neve, sheet_name_5, skiprows=1)

                def uj_DataFrmare(df, kedvezmeny, tuzesetivel):
                    mennyi_adat = len(df)
                    # print(df.keys())
                    tuzeset = []
                    szezonal = []
                    for i in range(mennyi_adat):
                        tuzeset.append(tuzesetivel)
                        szezonal.append(kedvezmeny)

                    fazis = df['Fázisszám']
                    fazis.astype(int)
                    napelem_mennyiseg = df['Napelem mennyiség']
                    napelem_mennyiseg.astype(int)
                    rendszer = df['Rendszer méret']
                    rendszer.astype(float)
                    netto_listaar = df['Nettó listaár']
                    netto_listaar.astype(float)
                    netto_listaar = round(netto_listaar)
                    adatok = {
                        'rm': rendszer,
                        'fsz': fazis,
                        'tipus': df['Inverter típusa'],
                        'napelemszam': napelem_mennyiseg,
                        'mfbMuszak': df['MFB kompatibilis-e a műszaki tartalom?'],
                        'nettoListaar': netto_listaar,
                        'mfbAR': df['MFB kompatibilis-e az ár?.1'],
                        'tuzeseti': tuzeset,
                        'szezonalis': szezonal
                    }

                    return adatok

                df_15 = pd.DataFrame(uj_DataFrmare(df15, 15, tuzes))
                df_10 = pd.DataFrame(uj_DataFrmare(df10, 10, tuzes))
                df_5 = pd.DataFrame(uj_DataFrmare(df5, 5, tuzes))

                egyesitve = pd.concat([df_5, df_10, df_15])

                dataframe = pd.DataFrame(egyesitve)

                mentes_helye = './xls_csv/'

                dataframe.to_excel(mentes_helye + uj_falj_nev, index=False)

                tn = xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[4] + ".xlsx"
                t = xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[4] + "_T.xlsx"

                if path.isfile(mentes_helye + tn) and path.isfile(mentes_helye + t):
                    df_tn = pd.read_excel(mentes_helye + tn)
                    df_t = pd.read_excel(mentes_helye + t)

                    egyesitett = pd.concat([df_tn, df_t])

                    dataf = pd.DataFrame(egyesitett)
                    dataf.to_excel(
                        mentes_helye + xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[4] + "_concat.xlsx",
                        index=False)

                    df_t_tn = pd.read_excel(
                        mentes_helye + xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[4] + "_concat.xlsx")
                    df_t_tn.to_csv(
                        mentes_helye + "csv\\" + xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[
                            4] + ".csv",
                        index=False)

                    csv_file = mentes_helye + "csv\\" + xlsx_fajl_neve_darabolva[1] + "_" + xlsx_fajl_neve_darabolva[
                        4] + ".csv"

                    if xlsx_fajl_neve_darabolva[1] == 'GROWATT' and xlsx_fajl_neve_darabolva[4] == '295':
                        tableBaseName = 'G295CS'
                    if xlsx_fajl_neve_darabolva[1] == 'GROWATT' and xlsx_fajl_neve_darabolva[4] == '315':
                        tableBaseName = 'G315HY'
                    if xlsx_fajl_neve_darabolva[1] == 'FRONIUS' and xlsx_fajl_neve_darabolva[4] == '295':
                        tableBaseName = 'F295CS'
                    if xlsx_fajl_neve_darabolva[1] == 'FRONIUS' and xlsx_fajl_neve_darabolva[4] == '315':
                        tableBaseName = 'F315HY'
                    if xlsx_fajl_neve_darabolva[1] == 'SOLAREDGE' and xlsx_fajl_neve_darabolva[4] == '295':
                        tableBaseName = 'SE295CS'
                    if xlsx_fajl_neve_darabolva[1] == 'SOLAREDGE' and xlsx_fajl_neve_darabolva[4] == '315':
                        tableBaseName = 'SE315CS'

                    conn = db.connect('db/elmu.dll')

                    read_CSV = pd.read_csv(csv_file)

                    read_CSV.to_sql(tableBaseName, conn, if_exists='replace', index=False)

                    self.label.configure(text='Sikeres adatbázis frissítés')
                    self.label.configure(fg='lime')

                    conn.commit()

            except RuntimeError as e:
                self.label.configure(text='SIKERTELEN adatbázis frissítés')
                self.label.configure(fg='red')
                # print(e)

    root = Root()
    root.mainloop()


# ellenőrzi MAC cím alapján, hogy jogosult-e a számítógép és ezáltal a tulajdonosa a program használatára
def user_controll():
    global f_nev, f_email, f_tel, ok, tarolt_mac
    mac = get_mac_address()
    sql1 = "SELECT * FROM felhasznalok WHERE jogosultsag='1'"
    data = cur.execute(sql1)
    t_mac = data.fetchall()
    # print(t_mac)
    egy_mac = str(t_mac[0][2]).split(",")

    ok = False

    for mac_address in egy_mac:
        m_jo = mac_address.lower().replace("-", ":")
        if mac == m_jo:
            ok = True
            tarolt_mac = m_jo

    if not ok:
        messagebox.showerror('Figyelmeztetés', 'Önnek nincs jogosultsága\na program használatára!')
        exit()
    elif ok:
        lejar = str(t_mac[0][3]).split("-")
        if mac == tarolt_mac:
            lejarat = datetime.date(int(lejar[0]), int(lejar[1]), int(lejar[2]))
            lejarat_10 = datetime.date(int(lejar[0]), int(lejar[1]), int(lejar[2])) - datetime.timedelta(days=10)
            lejarat_10_plus = datetime.date(int(lejar[0]), int(lejar[1]), int(lejar[2])) + datetime.timedelta(days=10)

            f_nev = t_mac[0][4]
            f_email = t_mac[0][5]
            f_tel = t_mac[0][6]

            current_date = datetime.datetime.now().date()
            lejarat_mulva = str(lejarat - current_date).split(' ')
            lejart = str(lejarat_10_plus - current_date).split(' ')
            if lejarat_10 < current_date < lejarat:
                messagebox.showinfo('Figyelmeztetés',
                                    'A licensz szerződés lejár ' + str(lejarat_mulva[0]) + ' nap múlva: ' + str(
                                        lejarat))
            if lejarat < current_date < lejarat_10_plus:
                messagebox.showinfo('Figyelmeztetés',
                                    'A licensz szerződés lejárt ' + str(10 - int(lejart[0])) + ' napja!\n' + str(
                                        lejarat) + '\nMég ' + str(lejart[0]) + ' nap van a szerződés megújítására!')
            if current_date > lejarat_10_plus:
                messagebox.showerror('Figyelmeztetés', 'A program szerződése lejárt!')
                sql2 = "UPDATE felhasznalok SET jogosultsag='0' WHERE mac like '%" + mac + "%'"
                cur.execute(sql2)
                conn.commit()
                exit()
        else:
            messagebox.showerror('Figyelmeztetés', 'Önnek nincs jogosultsága\na program használatára!')


win = Tk()
win_width = 890
win_height = 680
x_location = int(win.winfo_vrootwidth() / 2 - win_width / 2)
y_location = '+5'
program_location = str(x_location) + y_location
win.geometry(str(win_width) + 'x' + str(win_height) + '+' + program_location)
win.resizable(width=False, height=False)
win.configure(bg="gray25")


# a program bezárása
def kilepes():
    win.destroy()

# menü létrehozása
menu = Menu(win, tearoff=0)
win.config(menu=menu)
file = Menu(menu, tearoff=0)
file.add_command(label='Adatbázis frissítése', command=adatbazis_frissites)
file.add_separator()
file.add_command(label='Kilépés', command=kilepes)
menu.add_cascade(label='Adatbázis', menu=file)

win.title("Napelemes rendszer kalkulátor [HMKE] - SolarPanelSystemSOFT")
win.iconbitmap(bitmap="hmke.ico")
# user_controll()
text_font = "Verdana 10"
csomag_text_font = "Verdana 8"
bg = "gray25"
fg = "white"

panelszam = StringVar()
eves_kwh_fogyas = StringVar()
rendszer_telj = StringVar()
poli_mono = IntVar()
nmeter = StringVar()
inverter = StringVar()
v = IntVar()
f = StringVar()

kristaly = ["Monokristályos (Growatt 315)", "Monokristályos (Fronius 315)", "Monokristályos (SolarEdge 315)",
            "Polikristályos (Fronius 295)", "Polikristályos (Growatt 295)", "Polikristályos (SolarEdge 295)"]

tajolas_value = ["É",
                 "É-ÉK",
                 "ÉK",
                 "K-ÉK",
                 "K",
                 "K-DK",
                 "DK",
                 "D-DK",
                 "D",
                 "D-DNY",
                 "DNY",
                 "NY-DNY",
                 "NY",
                 "NY-ÉNY",
                 "ÉNY",
                 "É-ÉNY"]

teto_dolesszog = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90]

megye = {"Bács-Kiskun": 1200,
         "Baranya": 1210,
         "Békés": 1200,
         "Borsod-Abaúj-Zemplén": 1140,
         "Budapest": 1130,
         "Csongrád": 1220,
         "Fejér": 1200,
         "Győr-Moson-Sopron": 1170,
         "Hajdú-Bihar": 1180,
         "Heves": 1160,
         "Jász-Nagykun-Szolnok": 1200,
         "Komárom-Esztergom": 1180,
         "Nógrád": 1150,
         "Pest": 1130,
         "Somogy": 1220,
         "Szabolcs-Szatmár-Bereg": 1170,
         "Tolna": 1210,
         "Vas": 1180,
         "Veszprém": 1180,
         "Zala": 1200}

megye_nev = []

for i, j in megye.items():
    megye_nev.append(i)


def szolgaltato_es_aramdij():
    sql = "SELECT * FROM aramdij"
    data = cur.execute(sql)
    aram = data.fetchall()
    aram_dict = dict(aram)

    return aram_dict

# szolgáltatók listája
def szolgaltato():
    szolgaltato_nev = []

    for key, value in szolgaltato_es_aramdij().items():
        szolgaltato_nev.append(key)

    return szolgaltato_nev


adatbekeres_frame = Frame(win, width=win_width / 2, bg=bg)
adatbekeres_frame.grid(row=0, column=0, sticky="w")

# villanyszámla vagy KWh alapján számolja a rendszercsomagot
Radiobutton(adatbekeres_frame, text='Villanyszámla', variable=f, value='ft', bg=bg, fg="white", font=text_font,
            width=0, anchor="w", activebackground="orange", activeforeground="white", cursor="hand2", highlightcolor=fg,
            highlightbackground=fg, indicator=0, selectcolor="orange").grid(row=0, column=0, sticky="nw", padx=10,
                                                                            pady=5)
Radiobutton(adatbekeres_frame, text='Éves KWh', variable=f, value='kwh', bg=bg, fg="white", font=text_font,
            width=0, anchor="w", activebackground="orange", activeforeground="white", cursor="hand2", highlightcolor=fg,
            highlightbackground=fg, indicator=0, selectcolor="orange").grid(row=0, column=0, sticky="ne", padx=5,
                                                                            pady=5)
f.set('ft')

v_szamla_input = Entry(adatbekeres_frame, width=17, justify="center", fg="white", bg="orange", font=("Arial 12 bold"))
v_szamla_input.grid(row=0, column=1, pady=5, sticky="e")

v_szamla_input.focus()

Label(adatbekeres_frame, text="Tető tájolása:", font=text_font, bg=bg, fg=fg, width=23, anchor="w") \
    .grid(row=1, column=0, padx=10, pady=5)
tajolas_combo = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
tajolas_combo['value'] = tajolas_value
tajolas_combo.set('válasszon tájolást')
tajolas_combo.grid(row=1, column=1, pady=5, sticky="e")

Label(adatbekeres_frame, text="Tető dőlésszöge (fok\u00BA):", font=text_font, bg=bg, fg=fg, width=23, anchor="w") \
    .grid(row=2, column=0, padx=10, pady=5)
teto_dolesszog_combo = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
teto_dolesszog_combo['value'] = teto_dolesszog
teto_dolesszog_combo.set('válasszon dőlésszöget')
teto_dolesszog_combo.grid(row=2, column=1, pady=5, sticky="e")

Label(adatbekeres_frame, text="Megye:", font=text_font, bg=bg, fg=fg, width=23, anchor="w") \
    .grid(row=3, column=0, padx=10, pady=5)
megye_combo = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")

megye_combo['value'] = megye_nev
megye_combo.set('válasszon megyét')
megye_combo.grid(row=3, column=1, pady=5, sticky="e")


def rendszer_meret():
    global aramdij, eves_kwh, panel_meret, panel_szam, poli_mono_kWp, tajolas, polikristalyos_kWp, pvgis, dolesszog, \
        teljesitmeny_sz
    v_szamla_input.focus()
    adatok_frame.grid_forget()
    csomagarak_frame.grid_forget()
    ajanlatkero_frame.grid_forget()

    panelszam.set('')
    eves_kwh_fogyas.set('')
    nmeter.set('')
    try:
        if tajolas_combo.get() is not "válasszon tájolást":
            tajolas = tajolas_combo.get()
        if teto_dolesszog_combo.get() is not "válasszon dőlésszöget":
            dolesszog = teto_dolesszog_combo.get()
        if szolgaltato_combo.get() is not "válasszon áramszolgáltatót":
            szolgaltato = szolgaltato_combo.get()
            for key, value in szolgaltato_es_aramdij().items():
                if key == szolgaltato:
                    aramdij = value

        if f.get() == "ft":
            v_szamla = int(v_szamla_input.get())
            eves_vill_szamla = v_szamla * 12
            eves_kwh = round(float(eves_vill_szamla / aramdij), 2)
        if f.get() == "kwh":
            kwh = int(v_szamla_input.get())
            eves_kwh = int(kwh)

        if megye_combo.get() is not "válasszon megyét":
            megye_neve = megye_combo.get()
            for key, value in megye.items():
                if key == megye_neve:
                    pvgis = value

        sql = "SELECT teljesitmeny FROM teljesitmeny_leadas WHERE " \
              "tajolas='" + tajolas + "' AND dolesszog='" + dolesszog + "'"
        data = cur.execute(sql)
        teljesitmeny = data.fetchone()

        teljesitmeny_sz = float(teljesitmeny[0]) / 100
        if tajolas_combo.get() != "válasszon tájolást" and \
                teto_dolesszog_combo.get() != "válasszon dőlésszöget" and \
                szolgaltato_combo.get() != "válasszon áramszolgáltatót" and \
                megye_combo.get() != "válasszon megyét":
            kezdo_kep.grid_forget()
            kezdo_kep2.grid_forget()
            adatok_frame.grid(row=0, column=1, columnspan=2, rowspan=8, sticky="n", padx=5, pady=3)
            csomagarak_frame.grid(row=1, column=0, columnspan=2, sticky="n", padx=5)
            ajanlatkero_frame.grid(row=2, column=0, columnspan=2, sticky="ws", padx=5, pady=3)

        #     ================================================== SZÁMOLÁS ============================================

        poli_mono_szetszedve = str(poli_mono.get()).split(' ')

        if poli_mono_szetszedve[2] == '315)':
            polikristalyos_kWp = 315
        if poli_mono_szetszedve[2] == '295)':
            polikristalyos_kWp = 295

        monokristalyos_kWp = 315

        if poli_mono_szetszedve[0] == 'Monokristályos':
            poli_mono_kWp = monokristalyos_kWp
            panel_meret = 1.65
        if poli_mono_szetszedve[0] != 'Monokristályos':
            poli_mono_kWp = polikristalyos_kWp
            panel_meret = 1.67

        watt_teljesitmeny = eves_kwh * 1000
        szuks_rendszer_telj = watt_teljesitmeny / pvgis

        rendszer_merete = round(float(szuks_rendszer_telj / 1000), 2)
        panel_szam = ceil(szuks_rendszer_telj / (poli_mono_kWp * teljesitmeny_sz))

        n_meter = round(panel_szam * panel_meret, 2)

        panelszam.set(str(panel_szam) + " db")
        eves_kwh_fogyas.set(str(eves_kwh) + " kWh")
        rendszer_telj.set(str(rendszer_merete) + " kW")
        nmeter.set(str(n_meter) + " m\u00b2")

        max_rm = round(float(rendszer_merete * 1.2), 2)  # éves kWh 20%-kal túllőv

        napelemes_rendszer(rendszer_merete, max_rm, panel_szam, teljesitmeny_sz)
    except:
        adatok_frame.grid_forget()
        csomagarak_frame.grid_forget()
        ajanlatkero_frame.grid_forget()
        kezdo_kep.grid(row=0, column=1, columnspan=2, sticky="n", pady=5)
        kezdo_kep2.grid(row=1, column=0, columnspan=2, sticky="n", pady=10)
        # print(e)


def select_ajanlott_inverter(egysor):
    global pdf_csomag
    csomagok = osszes_ajanlat[egysor]
    inverter.set('')
    inverter.set(csomagok[1])
    pdf_csomag = osszes_ajanlat[egysor]


def popupmsg():
    global popup
    try:
        global neve, lakcim, tel, email
        popup = Toplevel()
        popup.title("Kiválasztott napelemes rendszercsomag mentése")
        popup.iconbitmap(bitmap="hmke.ico")
        popup.resizable(width=False, height=False)
        popup_width = 890
        popup_height = 200
        popup_x_location = int(popup.winfo_vrootwidth() / 2 - popup_width / 2)
        popup_y_location = '+250'
        popup_location = str(popup_x_location) + popup_y_location
        popup.geometry(str(popup_width) + 'x' + str(popup_height) + '+' + popup_location)
        popup.configure(bg="green")
        # ajánlatkérő adatainak bekérése
        bg1 = "green"
        Label(popup, text="", bg=bg1, fg=fg, width=15, anchor="w", font=text_font) \
            .grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=12)

        Label(popup, text="Ajánlatkérő neve:", bg=bg1, fg=fg, width=15, anchor="w", font=text_font) \
            .grid(row=1, column=0, sticky="w", padx=10, pady=12)
        neve = Entry(popup, width=40)
        neve.grid(row=1, column=1, sticky="w", padx=10, pady=12)

        Label(popup, text="Lakcíme:", bg=bg1, fg=fg, width=10, anchor="w", font=text_font) \
            .grid(row=1, column=2, sticky="w", padx=10, pady=12)
        lakcim = Entry(popup, width=50)
        lakcim.grid(row=1, column=3, sticky="w", padx=10, pady=12)

        Label(popup, text="Telefonszáma:", bg=bg1, fg=fg, width=15, anchor="w", font=text_font) \
            .grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tel = Entry(popup, width=40)
        tel.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        Label(popup, text="E-mail címe:", bg=bg1, fg=fg, width=10, anchor="w", font=text_font) \
            .grid(row=2, column=2, sticky="w", padx=10, pady=5)
        email = Entry(popup, width=50)
        email.grid(row=2, column=3, sticky="w", padx=10, pady=5)

        mentes_gomb = Button(popup, text="Ajánlat elkészítése", width=30, cursor="hand2", bg="orange", fg="white",
                             bd=0, font=text_font, command=to_pdf)
        mentes_gomb.grid(row=4, column=0, columnspan=4, sticky="n", pady=15)

        neve.focus()

        popup.mainloop()
    except:
        messagebox.showinfo('Figyelmeztetés', 'Nem választott ki rendszer csomagot!')


# kiválasztja a beírt adatok alapján megfelelő napelemes rendszereket
def napelemes_rendszer(panelsz, teljesitmeny_szazalek):
    global mrm, sqlcs, sql, osszes_ajanlat, tuzeseti_kapcsolo, inverter_tipusa, inv_csomag, tizedesjegy

    finansz = finanszirozas.get()
    tuzeseti_levalaszto = tuzeseti.get()
    szezonalis_kedvezmeny = szezonalis_kedv.get()
    fazis = int(fazisszam.get())

    for label in csomagarak_frame.grid_slaves():
        label.grid_forget()

    inverter.set('')

    if tuzeseti_levalaszto == 'Nem szükséges':
        tuzeseti_kapcsolo = 0
    elif tuzeseti_levalaszto == 'Szükséges':
        tuzeseti_kapcsolo = 1

    adatbazis_tabla = inverter_tipus()

    if "MFB pályázat" in finansz:
        max_panelszam = panelsz + 1
        if tulmeretezes.get() == 'Igen':
            sql = "SELECT * FROM \'{0}\' WHERE {1}<=napelemszam AND napelemszam<={2} AND FSZ={3} AND TUZESETI={4}" \
                  " AND SZEZONALIS={5} AND mfbAR=\'Igen\' AND mfbMuszak=\'Igen\' ORDER BY rm LIMIT 6" \
                .format(
                adatbazis_tabla,
                str(panelsz),
                str(max_panelszam),
                str(fazis),
                str(tuzeseti_kapcsolo),
                str(szezonalis_kedvezmeny)
            )
        if tulmeretezes.get() == 'Nem':
            sql = "SELECT * FROM \'{0}\' WHERE {1}=napelemszam AND FSZ={3} AND TUZESETI={4} AND SZEZONALIS={5} " \
                  "AND mfbAR=\'Igen\' AND mfbMuszak=\'Igen\' ORDER BY rm LIMIT 6" \
                .format(
                adatbazis_tabla,
                str(panelsz),
                str(max_panelszam),
                str(fazis),
                str(tuzeseti_kapcsolo),
                str(szezonalis_kedvezmeny)
            )

        data = cur.execute(sql)
        inv_csomag = data.fetchall()

    if "MFB pályázat" not in finansz:
        max_panelszam = panelsz + 2
        if tulmeretezes.get() == 'Igen':
            sql = "SELECT * FROM \'{0}\' WHERE {1}<=napelemszam AND napelemszam<={2} AND FSZ={3} AND TUZESETI={4} " \
                  "AND SZEZONALIS={5} ORDER BY rm LIMIT 6" \
                .format(
                adatbazis_tabla,
                str(panelsz + 1),
                str(max_panelszam + 1),
                str(fazis),
                str(tuzeseti_kapcsolo),
                str(szezonalis_kedvezmeny)
            )

        if tulmeretezes.get() == 'Nem':
            sql = "SELECT * FROM \'{0}\' WHERE {1}<=napelemszam AND napelemszam<={2} AND FSZ={3} AND TUZESETI={4} " \
                  "AND SZEZONALIS={5} ORDER BY rm LIMIT 6" \
                .format(
                adatbazis_tabla,
                str(panelsz),
                str(max_panelszam),
                str(fazis),
                str(tuzeseti_kapcsolo),
                str(szezonalis_kedvezmeny)
            )

        data = cur.execute(sql)
        inv_csomag = data.fetchall()

    if len(inv_csomag) != 0:
        inverter_tipusa = inv_csomag[0][2]
        inverter.set(inverter_tipusa)
        Label(adatok_frame, text="Éves kWh fogyasztás:", bg=bg, fg=fg, width=23, anchor="w", font=text_font) \
            .grid(row=0, column=0, sticky="w", padx=10, pady=5)
        Label(adatok_frame, text="", textvariable=eves_kwh_fogyas, bg=bg, fg=fg, width=20, anchor="w",
              font=text_font) \
            .grid(row=0, column=1, sticky="w")

        Label(adatok_frame, text="Napelem panel szükséglet:", bg=bg, fg="lime", width=23, anchor="w",
              font=text_font) \
            .grid(row=1, column=0, sticky="w", padx=10, pady=5)
        Label(adatok_frame, text="", textvariable=panelszam, bg=bg, fg="lime", width=20, anchor="w", font=text_font) \
            .grid(row=1, column=1, sticky="w")

        Label(adatok_frame, text="Napelemes rendszer\nteljesítménye:", bg=bg, fg="lime", width=23, anchor="w",
              font=text_font) \
            .grid(row=2, column=0, sticky="w", padx=10, pady=5)
        Label(adatok_frame, text="", textvariable=rendszer_telj, bg=bg, fg="lime", width=20, anchor="w",
              font=text_font) \
            .grid(row=2, column=1, sticky="w")

        Label(adatok_frame, text="Szükséges tető felület:", bg=bg, fg="lime", width=23, anchor="w", font=text_font) \
            .grid(row=3, column=0, sticky="w", padx=10, pady=5)
        Label(adatok_frame, text="", textvariable=nmeter, bg=bg, fg="lime", width=20, anchor="w", font=text_font) \
            .grid(row=3, column=1, sticky="w")

        Label(adatok_frame, text="Ajánlott inverter:", bg=bg, fg=fg, width=23, anchor="w", font=text_font) \
            .grid(row=4, column=0, sticky="w", padx=10, pady=5)
        Label(adatok_frame, text="", textvariable=inverter, bg=bg, fg=fg, width=20, anchor="w", font=text_font) \
            .grid(row=4, column=1, sticky="w")

        try:
            image = Image.open("kepek/" + inverter_tipusa + ".jpg")
        except:
            image = Image.open("kepek/default.jpg")

        image = image.resize((200, 200), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        inverter_kep = Label(adatok_frame, image=photo, padx=2, pady=2, bg="lime")
        inverter_kep.image = photo
        inverter_kep.grid(row=5, column=0, columnspan=2, sticky="n", pady=5)

        mentes_gomb = Button(adatok_frame, text="Csomagajánlat mentése", width=30, cursor="hand2", bg="orange",
                             fg="white",
                             bd=0, font=text_font, command=popupmsg)
        mentes_gomb.grid(row=6, column=0, columnspan=2, sticky="n", pady=5)

        Label(csomagarak_frame, text=170 * "_", bg=bg, fg=fg) \
            .grid(row=0, column=0, columnspan=10, pady=5, sticky="w")

        Label(csomagarak_frame, text="Rendsz.\ntelj.\n(kW)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=1, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Inverter típus", bg=bg, fg='lime', width=18, font=csomag_text_font) \
            .grid(row=1, column=2, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Panel\nszám\n(db)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=3, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Nettó \nkedv.\nár (20%)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=4, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Szezonális\nkedv.\n(Ft)", bg=bg, fg='lime',
              font=csomag_text_font).grid(row=1, column=5, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Nettó\nszezonális\nkedv. ár(Ft)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=6, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="ÁFA\n(Ft)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=7, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Bruttó kedv. ár\n(Ft)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=8, sticky="nsew", pady=2)
        Label(csomagarak_frame, text="Önerő\n(Ft)", bg=bg, fg='lime', font=csomag_text_font) \
            .grid(row=1, column=9, sticky="nsew", pady=2)

    elif len(inv_csomag) == 0:
        kezdo_kep.grid(row=0, column=1, columnspan=2, sticky="n", pady=5)
        ajanlatkero_frame.grid_forget()
        adatok_frame.grid_forget()
        kezdo_kep2.grid(row=1, column=0, columnspan=2, sticky="n", pady=10)
        if finansz == 'MFB pályázat':
            messagebox.showinfo('Figyelmeztetés',
                                'Nincs az MFB pályázatnak megfelelő csomagajánlat\na megadott adatok alapján!')
        if finansz == "Részletfizetés" or finansz == "Készpénz":
            messagebox.showinfo('Figyelmeztetés', 'Nincs megfelelő csomagajánlat\na megadott adatok alapján!')

    cella_adat = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    r = 2
    c = 0
    z = 0
    k = 0

    osszes_ajanlat = []
    radio_szamok = [0, 1, 2, 3, 4, 5]

    for csomag_mfb in inv_csomag:
        # 20% általános kedvezmény
        szamhossz = len(str(csomag_mfb[0]))
        if szamhossz == 4:
            tizedesjegy = 2
        if szamhossz == 5:
            tizedesjegy = 3

        altalanosKedvezmeny = 0.2
        telj = str(csomag_mfb[0]) + " (" + str(round(float(csomag_mfb[0] * teljesitmeny_szazalek), tizedesjegy)) + ")"
        invTipusa = csomag_mfb[2]
        napelemSzam = csomag_mfb[3]
        nettoListaar = csomag_mfb[8]
        if nettoListaar > 30:
            nettoListaar = csomag_mfb[8]
        elif nettoListaar < 30:
            nettoListaar = csomag_mfb[5]

        nettoKedvezmenyesAr = round(nettoListaar - (nettoListaar * altalanosKedvezmeny))
        szezonKedv = round(nettoKedvezmenyesAr * (int(szezonalis_kedv.get()) / 100))
        nettoKedvSzezonAr = nettoKedvezmenyesAr - szezonKedv
        afa = round(nettoKedvSzezonAr * 0.27)
        bruttoKedvAr = nettoKedvSzezonAr + afa
        onero = round(bruttoKedvAr * 0.1)

        nettoKedvezmenyesArF = '{:,}'.format(nettoKedvezmenyesAr).replace(',', ' ') + ' Ft'
        szezonKedvF = '{:,}'.format(szezonKedv).replace(',', ' ') + ' Ft'
        nettoKedvSzezonArF = '{:,}'.format(nettoKedvSzezonAr).replace(',', ' ') + ' Ft'
        afaF = '{:,}'.format(afa).replace(',', ' ') + ' Ft'
        oneroF = '{:,}'.format(onero).replace(',', ' ') + ' Ft'
        bruttoKedvArF = '{:,}'.format(bruttoKedvAr).replace(',', ' ') + ' Ft'

        kiirandoSorok = [telj, invTipusa, napelemSzam, nettoKedvezmenyesArF, szezonKedvF, nettoKedvSzezonArF, afaF,
                         bruttoKedvArF, oneroF]
        osszes_ajanlat.append(kiirandoSorok)

        for number in range(len(cella_adat)):

            if c == 0:
                x = Radiobutton(csomagarak_frame, text='Kiválaszt', variable=v, value=k, width=7, cursor="hand2",
                                command=lambda: select_ajanlott_inverter(v.get()))
                x.config(activebackground="gray25")
                x.config(activeforeground="white")
                x.config(bg="gray25")
                x.config(highlightbackground="orange")
                x.config(highlightcolor="white")
                x.config(fg="white")
                x.config(indicator=0)
                x.config(selectcolor="orange")
                x.config(bd=0)

                x.grid(row=r, column=0, padx=0, sticky="w")

            adat = Label(csomagarak_frame, text=kiirandoSorok[number], bg=bg, fg=fg, font=csomag_text_font)
            adat.grid(row=r, column=c + 1, sticky="nsew", pady=2)

            c = c + 1

            if c == len(cella_adat):
                c = 0

        k = k + 1
        r = r + 1
        z = z + 1
    # a kiírt sorok aláhúzása a ciklus végén
    Label(csomagarak_frame, text=107 * "=", bg=bg, fg=fg).grid(row=r, column=0, columnspan=10, sticky="w")
    # a legelső Radibutton kiválasztása
    v.set(0)
    select_ajanlott_inverter(v.get())


def inverter_tipus():
    global inv

    if poli_mono.get() != 'Polikristályos (SolarEdge 295)':
        arnyek.set('Nem')

    arnyekos = arnyek.get()

    if poli_mono.get() == 'Polikristályos (Fronius 295)':
        if arnyekos == 'Nem':
            inv = 'F295CS'
        elif arnyekos == 'Igen':
            inv = 'SE295CS'
            poli_mono.set('Polikristályos (SolarEdge 295)')

    if poli_mono.get() == 'Polikristályos (Growatt 295)':
        if arnyekos == 'Nem':
            inv = 'G295CS'
        elif arnyekos == 'Igen':
            inv = 'SE295CS'
            poli_mono.set('Polikristályos (SolarEdge 295)')

    if poli_mono.get() == 'Monokristályos (Growatt 315)':
        if arnyekos == 'Nem':
            inv = 'G315HY'
        elif arnyekos == 'Igen':
            inv = 'SE295CS'
            poli_mono.set('Polikristályos (SolarEdge 295)')

    if poli_mono.get() == 'Polikristályos (SolarEdge 295)':
        inv = 'SE295CS'
        arnyek.set('Igen')

    if poli_mono.get() == 'Monokristályos (SolarEdge 315)':
        if arnyekos == 'Nem':
            inv = 'SE315CS'
        elif arnyekos == 'Igen':
            inv = 'SE295CS'
            poli_mono.set('Polikristályos (SolarEdge 295)')

    if poli_mono.get() == 'Monokristályos (Fronius 315)':
        if arnyekos == 'Nem':
            inv = 'F315HY'
        elif arnyekos == 'Igen':
            inv = 'SE295CS'
            poli_mono.set('Polikristályos (SolarEdge 295)')

    return inv


Label(adatbekeres_frame, text="Áramszolgáltató:", font=text_font, bg=bg, fg=fg, width=23, anchor="w") \
    .grid(row=5, column=0, padx=10, pady=5)
szolgaltato_combo = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
szolgaltato_combo['value'] = szolgaltato()
szolgaltato_combo.set('válasszon áramszolgáltatót')
szolgaltato_combo.grid(row=5, column=1, pady=5, sticky="e")

Label(adatbekeres_frame, text="Poli- vagy monokristályos:", bg=bg, fg=fg, font=text_font).grid(row=6, column=0, padx=10,
                                                                                               pady=5,
                                                                                               sticky="w")
poli_mono = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
poli_mono['value'] = kristaly
poli_mono.set('Monokristályos (Fronius 315)')
poli_mono.grid(row=6, column=1, pady=5, sticky="w")

Label(adatbekeres_frame, text="Fázisszám:", bg=bg, fg=fg, font=text_font).grid(row=7, column=0, padx=10, pady=5,
                                                                               sticky="w")
fazisszam = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
fazisszam['value'] = [1, 3]
fazisszam.set(1)
fazisszam.grid(row=7, column=1, pady=5, sticky="w")

Label(adatbekeres_frame, text="Árnyékos hely:", bg=bg, fg=fg, font=text_font).grid(row=8, column=0, padx=10, pady=5,
                                                                                   sticky="w")

arnyek = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
arnyek['value'] = ['Nem', 'Igen']
arnyek.set('Nem')
arnyek.grid(row=8, column=1, pady=5, sticky="w")

Label(adatbekeres_frame, text="Tűzeseti leválasztó:", bg=bg, fg=fg, font=text_font).grid(row=9, column=0, padx=10,
                                                                                         pady=5, sticky="w")

tuzeseti = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
tuzeseti['value'] = ['Nem szükséges', 'Szükséges']
tuzeseti.set('Nem szükséges')
tuzeseti.grid(row=9, column=1, pady=5, sticky="w")

Label(adatbekeres_frame, text="Finanszírozás:", bg=bg, fg=fg, font=text_font).grid(row=10, column=0, padx=10, pady=5,
                                                                                   sticky="w")

finanszirozas = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
finanszirozas['value'] = ['MFB pályázat', 'Részletfizetés', 'Készpénz']
finanszirozas.set('MFB pályázat')
finanszirozas.grid(row=10, column=1, pady=5, sticky="w")

Label(adatbekeres_frame, text="Szezonális kedv. (%):", bg=bg, fg=fg, font=text_font).grid(row=11, column=0, padx=10,
                                                                                          pady=5,
                                                                                          sticky="w")

szezonalis_kedv = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
szezonalis_kedv['value'] = ['5', '10', '15']
szezonalis_kedv.set('5')
szezonalis_kedv.grid(row=11, column=1, pady=5, sticky="w")

Label(adatbekeres_frame, text='Rendszer bővítése', bg=bg, fg=fg, font=text_font) \
    .grid(row=12, column=0, padx=10, pady=5, sticky="w")
tulmeretezes = Combobox(adatbekeres_frame, width=25, justify="center", state="readonly")
tulmeretezes['value'] = ['Nem', 'Igen']
tulmeretezes.set('Nem')
tulmeretezes.grid(row=12, column=1, pady=5, sticky="w")

kalkulal_gomb = Button(adatbekeres_frame, text="Rendszer kalkuláció", width=45, cursor="hand2", bg="green", fg="white",
                       bd=0, font=text_font, command=rendszer_meret)
kalkulal_gomb.grid(row=13, column=0, columnspan=2, pady=10, padx=10, sticky="s")

# ==================================== Csomag árak Frame ===========================================================

csomagarak_frame = Frame(win, width=win_width, height=40, bg=bg)

# ====================================  Adatok Frame ===============================================================

adatok_frame = Frame(win, width=win_width / 2, bg=bg)

# ====================================  Ajánlatkérő adatok Frame ====================================================

ajanlatkero_frame = Frame(win, width=win_width, bg=bg)

# ====================================  Kezdő kép Frame ====================================================

kezdo_kep_frame = Frame(win, width=win_width / 2, bg=bg) \
    .grid(row=0, column=1, rowspan=18, sticky="n", padx=20, pady=3)

kezdo_kep_frame2 = Frame(win, width=win_width, bg=bg) \
    .grid(row=2, column=0, columnspan=2, sticky="ws", padx=5, pady=3)

image1 = Image.open("kepek/napelem.png")
image2 = Image.open("kepek/nap.png")

image1 = image1.resize((250, 404), Image.ANTIALIAS)
image2 = image2.resize((750, 200), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(image1)
photo1 = ImageTk.PhotoImage(image2)

kezdo_kep = Label(kezdo_kep_frame, image=photo, padx=2, pady=2, bg=bg)
kezdo_kep.image = photo
kezdo_kep.grid(row=0, column=1, columnspan=2, sticky="n", pady=5)

kezdo_kep2 = Label(kezdo_kep_frame2, image=photo1, padx=2, pady=2, bg=bg)
kezdo_kep2.image = photo1
kezdo_kep2.grid(row=1, column=0, columnspan=2, sticky="n", pady=10)


def latin_szoveg(nev):
    uj_nev = nev.replace("ű", "\u00FB").replace("Ű", "\u00DB").replace("ő", "\u00F4").replace("Ő", "\u00D4")

    return uj_nev


def to_pdf():
    global kedv_ar
    if str(neve.get()).strip() != "" and str(lakcim.get()).strip() != "":
        datum = datetime.date.today()
        # óre, perc, másodpercet ad vissza az strftime("%X")
        o_p_mp = datetime.datetime.now().strftime("%X")
        p_mp = o_p_mp.split(":")
        pMp = p_mp[1] + p_mp[2]
        # 1 hónap érvényesség (1*365/12)    2 hónap érvényesség (2*365/12)
        # vagy a napok számát írjuk be || ervenyesseg = datetime.date.today() + datetime.timedelta(30) 30 nap
        ervenyesseg = datetime.date.today() + datetime.timedelta(15)

        fajl_nev = neve.get() + "_" + lakcim.get()

        a = fajl_nev.replace(" ", "_").replace(".", "_").replace(",", "") \
            .replace("/", "_").replace("&", "_").replace("-", "_")

        output_nev = a + "_" + pMp + ".pdf"

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_title('Napelemes rendszer aj\u00E1nlat [HMKE]')
        pdf.set_author('SolarPanelSystemSOFT - Napelemes rendszer kalkulátor')
        pdf.set_creator('SolarPanelSystemSOFT - Napelemes rendszer kalkulátor')
        pdf.set_subject('Napelemes rendszer ajánlat!')

        pdf.set_font('Arial', 'B', 16)
        pdf.set_fill_color(0, 102, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 10, 'Napelemes rendszer aj\u00E1nlat - HMKE', 0, 1, 'C', fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Times', '', 12)
        pdf.cell(190, 10, ' ', 'B', 0, 'L')
        pdf.ln(10)
        # Ajánlatkérő adatai =========================================================================

        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'Ajánlatkér\u00F4: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(70, 10, '' + latin_szoveg(neve.get()) + '', 0, 0, 'R')
        pdf.cell(10, 10, '')
        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'Ajánlatadó: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(40, 10, latin_szoveg(f_nev), 0, 0, 'R')

        pdf.ln(6)

        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'Cím: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(70, 10, '' + latin_szoveg(lakcim.get()) + '', 0, 0, 'R')
        pdf.cell(10, 10, '')
        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'Tel.: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(40, 10, f_tel, 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'Tel.: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(70, 10, '' + tel.get() + '', 0, 0, 'R')
        pdf.cell(10, 10, '')
        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'E-mail: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(40, 10, f_email, 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'E-mail: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(70, 10, '' + email.get() + '', 0, 0, 'R')
        pdf.cell(10, 10, '')
        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, 'Dátum: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(40, 10, '' + str(datum) + '', 0, 0, 'R')

        pdf.ln(6)

        pdf.set_font('Times', '', 10)
        pdf.cell(30, 10, '')
        pdf.cell(70, 10, '')
        pdf.cell(10, 10, '')

        pdf.cell(30, 10, 'Érvényesség: ')
        pdf.set_font('Times', 'I', 10)
        pdf.cell(40, 10, '' + str(ervenyesseg) + '', 0, 0, 'R')
        pdf.ln(2)
        pdf.cell(190, 10, ' ', 'B', 0, 'L')
        pdf.ln(15)
        # ==============================================================================================================
        pdf.set_font('Arial', 'I', 14)
        pdf.set_fill_color(153, 255, 153)
        pdf.set_text_color(0, 102, 0)

        pdf.cell(190, 10, 'Kalkuláció alapja ', 0, 1, 'L', fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        if f.get() == "ft":
            pdf.cell(70, 10, 'Havi villanysz\u00E1mla: ')
            pdf.set_font('Times', 'B', 12)
            vsz = int(v_szamla_input.get())
            vszamla = '{:,}'.format(vsz).replace(',', ' ') + ' Ft/hó'
            pdf.cell(30, 10, '' + vszamla + '')
            pdf.ln(6)
        if f.get() == "kwh":
            pdf.cell(70, 10, 'Éves kWh fogyasztás: ')
            pdf.set_font('Times', 'B', 12)
            vsz = int(v_szamla_input.get())
            vszamla = '{:,}'.format(vsz).replace(',', ' ') + ' kWh'
            pdf.cell(30, 10, '' + vszamla + '')
            pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Napelem panel sz\u00FCks\u00E9glet: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + panelszam.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Napelemes rendszer teljes\u00EDtm\u00E9nye: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + rendszer_telj.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Sz\u00FCks\u00E9ges tet\u00F4 fel\u00FClet: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + nmeter.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Tet\u00F4 t\u00E1jol\u00E1sa: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + tajolas_combo.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Tet\u00F4 d\u00F4l\u00E9sszöge (fok\u00BA): ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + teto_dolesszog_combo.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Megye: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + megye_combo.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, '\u00C1ramszolg\u00E1ltat\u00F3: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + szolgaltato_combo.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Poli- vagy monokrist\u00E1lyos: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + poli_mono.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'F\u00E1zissz\u00E1m: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + fazisszam.get() + ' f\u00E1zis')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, '\u00C1rny\u00E9kos hely: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + arnyek.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'T\u00FBzeseti lev\u00E1laszt\u00F3: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + tuzeseti.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Finansz\u00EDroz\u00E1s: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + latin_szoveg(finanszirozas.get()) + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'Szezon\u00E1lis kedv. (%): ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + szezonalis_kedv.get() + '')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(70, 10, 'B\u00F4vített rendszer: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(30, 10, '' + tulmeretezes.get() + '')
        pdf.ln(10)

        pdf.set_font('Arial', 'I', 14)
        pdf.set_fill_color(153, 255, 153)
        pdf.set_text_color(0, 102, 0)
        pdf.cell(190, 10, 'Napelemes rendszer csomagaj\u00E1nlat', 0, 1, 'L', fill=True)

        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)

        fazis = int(fazisszam.get())

        nl = pdf_csomag[3].split(" ")
        if len(nl) == 4:
            kedv_ar = int(nl[0] + nl[1] + nl[2])
        if len(nl) == 3:
            kedv_ar = int(nl[0] + nl[1])

        nettoKedvezmenyesAr = kedv_ar
        szezonKedv = round(nettoKedvezmenyesAr * (int(szezonalis_kedv.get()) / 100))
        nettoKedvSzezonAr = nettoKedvezmenyesAr - szezonKedv
        afa = round(nettoKedvSzezonAr * 0.27)
        bruttoKedvAr = nettoKedvSzezonAr + afa
        onero = round(bruttoKedvAr * 0.1)

        nettoKedvezmenyesArF = '{:,}'.format(nettoKedvezmenyesAr).replace(',', ' ') + ' Ft'
        szezonKedvF = '{:,}'.format(szezonKedv).replace(',', ' ') + ' Ft'
        nettoKedvSzezonArF = '{:,}'.format(nettoKedvSzezonAr).replace(',', ' ') + ' Ft'
        afaF = '{:,}'.format(afa).replace(',', ' ') + ' Ft'
        oneroF = '{:,}'.format(onero).replace(',', ' ') + ' Ft'
        bruttoKedvArF = '{:,}'.format(bruttoKedvAr).replace(',', ' ') + ' Ft'

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Rendszer teljes\u00EDtm\u00E9ny')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + str(pdf_csomag[0]) + ' kW', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'F\u00E1zissz\u00E1m: ')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + str(fazis) + ' f\u00E1zis', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Inverter t\u00EDpus')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + str(pdf_csomag[1]) + '', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Napelem sz\u00E1m')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + str(pdf_csomag[2]) + ' db', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Nett\u00F3 kedvezm\u00E9nyes \u00E1r')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + nettoKedvezmenyesArF + '', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Szezon\u00E1lis kedv.')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + szezonKedvF + '', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Nett\u00F3 szezon\u00E1lis kedv. \u00E1r')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + nettoKedvSzezonArF + '', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, '\u00C1fa')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + afaF + '', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, 'Brutt\u00F3 kedv. \u00E1r')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + bruttoKedvArF + '', 0, 0, 'R')
        pdf.ln(6)

        pdf.set_font('Times', '', 12)
        pdf.cell(20)
        pdf.cell(50, 10, '\u00D6ner\u00F4')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(40, 10, '' + oneroF + '', 0, 1, 'R')
        # pdf.ln(5)

        koszono_szoveg = 'KÖSZÖNJÜK AJÁNLATKÉRÉSÉT!'
        pdf.set_font('Times', '', 12)
        pdf.cell(190, 10, ' ', 'B', 0, 'L')
        pdf.ln(10)
        pdf.set_font('Times', 'B', 13)
        pdf.set_text_color(0, 102, 0)
        pdf.cell(190, 10, koszono_szoveg, 0, 0, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)
        pdf.set_font('Times', '', 8)
        pdf.cell(190, 10, str(pdf.page_no()) + '/2 oldal', 0, 0, 'R')

        # Második oldal

        pdf.add_page()
        pdf.set_font('Times', 'B', 12)
        pdf.cell(190, 5, 'Részletfizetés', 'B', 0, 'L')
        pdf.ln(8)
        pdf.set_font('Times', '', 10)
        reszletfizetes1 = "Teljes körű szolgáltatásunk keretében finanszírozási kérdésekben is megoldást nyújtunk."
        reszletfizetes2 = " Ügyfeleink számára díj- és kamatmentes (0% THM) részletfizetési lehetőséget biztosítunk."

        valasztas = "Miért érdemes a részletfizetést választani?"

        ok_1 = "- 0% kamat, 0% THM"
        ok_2 = "- nincsenek egyéb felmerülő díjtételek (pl. külön eljárási díj)"

        ok_3 = "- nincsenek adminisztrációs terhek: a végszámla keltéhez képest állapítjuk meg a rendszeres törlesztési"
        ok_3_1 = "  határidőt, hogy Önnek lehetősége legyen rendszeres banki átutalás beállítására"

        ok_4 = "- a szerződéses összeg bármikor, bármekkora mértékben elő-, illetve végtörleszthető"
        ok_5 = "- csak 10%-os előlegre van szükség a szerződéskötéskor, míg a fennmaradó 90% tíz havi részletben,"
        ok_5_1 = "  a számla kibocsátását követően fizetendő"

        ervenyes = "Az ajánlat visszavonásig érvényes. A feltüntetett adatok kizárólag tájékoztató jellegűek, " \
                   "nem minősülnek szerződéskötési ajánlatnak."

        pdf.cell(190, 5, latin_szoveg(reszletfizetes1), align='J')
        pdf.ln(5)
        pdf.cell(190, 5, latin_szoveg(reszletfizetes2), align='J')
        pdf.ln(10)
        pdf.cell(190, 5, latin_szoveg(valasztas))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_1))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_2))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_3))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_3_1))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_4))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_5))
        pdf.ln(5)
        pdf.cell(6)
        pdf.cell(190, 5, latin_szoveg(ok_5_1))
        pdf.ln(8)
        pdf.cell(190, 5, latin_szoveg(ervenyes))
        pdf.ln(10)
        pdf.set_font('Times', 'B', 12)
        pdf.cell(190, 5, latin_szoveg('Kivételek téli időszakban történő kivitelezés esetén'), 'B', 0, 'L')
        pdf.ln(8)
        pdf.set_font('Times', '', 10)

        kivetelek1 = "Amennyiben a felmérés/kivitelezés/próbaüzem és átadás november 15. és március 15. közötti téli " \
                     "időszakra esik, úgy a Vállalkozó"
        kivetelek2 = "teljesítési határidejébe ezen időszak nem számít bele, tekintettel arra, hogy a tetőn történő " \
                     "biztonságos munkavégzés feltételei az"
        kivetelek3 = "időjárás miatt nem adottak. Amennyiben a felek, a Vállalkozó kezdeményezését követően, " \
                     "úgy ítélik meg, hogy a helyi időjárási"
        kivetelek4 = "körülmények engedik a biztonságos munkavégzést, úgy ezen téli időszak alatt is folytatható a " \
                     "kivitelezés, amely beleszámít a"
        kivetelek5 = "teljesítési határidőbe."

        pdf.cell(190, 5, latin_szoveg(kivetelek1), align='J')
        pdf.ln(5)
        pdf.cell(190, 5, latin_szoveg(kivetelek2), align='J')
        pdf.ln(5)
        pdf.cell(190, 5, latin_szoveg(kivetelek3), align='J')
        pdf.ln(5)
        pdf.cell(190, 5, latin_szoveg(kivetelek4), align='J')
        pdf.ln(5)
        pdf.cell(190, 5, latin_szoveg(kivetelek5), align='J')
        pdf.ln(10)
        pdf.set_font('Times', 'B', 12)
        pdf.cell(190, 5, latin_szoveg('Jótállás'), 'B', 0, 'L')
        pdf.ln(8)
        pdf.set_font('Times', '', 10)

        jotallas1 = 'Napelem'
        jotallas1_1 = '10 év jótállás'
        jotallas1_2 = '10 év 90% teljesítmény jótállás'
        jotallas1_3 = '25 év 80% teljesítmény jótállás'

        jotallas2 = 'Inverter'
        jotallas2_1 = 'Growatt: 10 év jótállás'
        jotallas2_2 = 'Fronius: 5 év jótállás'
        jotallas2_3 = 'SolarEdge: 12 év jótállás'
        jotallas2_4 = 'SolarEdge optimalizáló: 25 év jótállás'

        jotallas3 = 'Tartó szerkezet: 10 év jótállás'
        jotallas4 = 'Egyéb villamos szerkezetek: 5 év jótállás'

        pdf.cell(190, 5, jotallas1)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas1_1)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas1_2)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas1_3)
        pdf.ln(5)

        pdf.cell(190, 5, jotallas2)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas2_1)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas2_2)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas2_3)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(190, 5, jotallas2_4)
        pdf.ln(8)

        pdf.cell(190, 5, jotallas3)
        pdf.ln(5)
        pdf.cell(190, 5, jotallas4)

        pdf.ln(20)
        pdf.cell(190, 5, latin_szoveg('Bízva a sikeres együttműködésben,'), 0, 0, 'L')
        pdf.ln(5)
        pdf.cell(190, 5, latin_szoveg(f_nev), 0, 0, 'C')
        pdf.ln(3)
        pdf.cell(190, 5, str(datum), 0, 0, 'R')

        pdf.ln(36)
        pdf.set_font('Times', '', 8)
        pdf.cell(190, 5, str(pdf.page_no()) + '/2 oldal', 0, 0, 'R')

        mappa = "./ajanlatok/" + output_nev
        pdf.output(mappa)
        popup.destroy()
        fajl_helye = getcwd()
        startfile(fajl_helye + "/ajanlatok/" + output_nev)
    else:
        pass


conn.commit()
win.mainloop()
