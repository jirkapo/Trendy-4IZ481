#Minimální řešení čtení a překladu lékařských zpráv ze scanu do lajcké řeči:
import majka
from PIL import Image
import pytesseract
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import csv
import sys

csv_file = csv.reader(open('slovnik.csv', "r", encoding="utf8"), delimiter=",")

#gui vstup
layout = [[sg.Text('Cesta k obrazku')],
          [sg.Text('Vstupni file'), sg.In(size=(10,1),key='file_cesta'), sg.FileBrowse()],
          [sg.Button('Submit'), sg.Button('Cancel')]]
window = sg.Window('take pillow pil', layout)
w_event, w_values = window.read(close=True) 

#ocr
#je treba dotahnout si i ty lang data
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
text = pytesseract.image_to_string(Image.open(w_values["file_cesta"]),lang="ces")
#tady je treba nastavit vlastni cestu k majka datum
morph = majka.Majka(r'C:\Users\Luky\Desktop\majka.w-lt')
morph.tags = False
#tohle thinking back by bylo lepsi true protoze stejne later pouzivam jen prvni
morph.first_only = False
morph.negative = "ne"
morph.flags |= majka.ADD_DIACRITICS
morph.flags |= majka.IGNORE_CASE

#zapise celou zpravu do txt
with open('zprava_raw.txt', 'w') as f:
    f.write(text)

#Načtení slovníku lékařských pojmů z csv:
Slovnik=list()
for row in csv_file:
    Slovnik.append(row[0])
#Slouží k odtstranění přebytečných mezer z ocr:
word1=0
line1=0
f=open('zprava_new.txt', 'w')
for line in text.split("\n"):
    #Odstranění přebytečných řádků:
    if line.replace(' ', '')=="":
        continue
    for word in line.split(" "):
        #Odstranění přebytečných mezer:
        if word1==word:
            continue
        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~•¶|♪â™Ş>0123456789'''
        word1=word
        for punct in punctuations:
          word1 = word1.replace(punct,"")
        #Nahrazení slov ve slovníku:
        for row in Slovnik:
            row=row.split(";")
            #if current rows 2nd value is equal to input, print that row
            if word1 == row[0]:
                #print(row[0],word1) 
                word=row[1]
        #Sepsání výsledné zprávy:
        f.write(word)
        f.write(" ")
    f.write("\n")


#odmaze new lines pro lematizaci    
text = text.replace("\n"," ")


word_count = {}
for word in text.split(" "):
  #preprocesing
  #asi toho bude treba vic, ale neni od veci treba smazat vsechna cisla a interpunkci
  punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~•¶|♪â™Ş>0123456789'''
  for punct in punctuations:
    word = word.replace(punct,"")
  morph_slovo = morph.find(str(word))
  #kdyz najde lemma tak ulozi to prvni
  if len(morph_slovo) > 0:
    if morph_slovo[0]["lemma"] not in word_count.keys():
      word_count[morph_slovo[0]["lemma"]] = 1
    else:
      word_count[morph_slovo[0]["lemma"]] += 1
  #kdyz nenajde lemma tak ulozi slovo 1:1
  else:
    if word not in word_count.keys():
      word_count[word] = 1
    else:
      word_count[word] += 1

#zapise cetnosti
with open("zprava_cetnosti.txt","w") as f:
  f.write(str(word_count))

#dal to by to v tom asi hledalo jestli ty slova jsou v nejakym tom slovniku medical terms a tak
#Dále by se dalo zapracovat na grafické úpravě výstupu


