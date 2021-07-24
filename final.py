import re
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from pydub import AudioSegment 
import requests
import csv
import os
import textwrap




def getImage():
    imagePath = input("Enter image file location.The file should be 1080p*1080p :")
    imageFile2= Image.open(imagePath)
    width , height =imageFile2.size
    if(width != 1080 & height!=1080):
        print("Please enter image with exactly 1080p*1080p dimensions")
        getImage()
    imageFile2.close()
    return imagePath


def readCSV(csv_file):
    fields = []
    rows = []
    with open(csv_file, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)

        # extracting field names through first row
        fields = next(csvreader)
    
        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)
    return fields,rows

def get_ar_mr_text(row):
    arabicText = row[2]
    marathiText = row[3]
    return arabicText,marathiText

def getFinalAudio(row ,ayahNo):
    urlarabic = "https://marathiquran.com/media/"+row[4]
    urlmara = "https://marathiquran.com/media/"+row[5]
    try:
        arAudio = requests.get(urlarabic)
        mrAudio = requests.get(urlmara)
        open('arabic.mp3', 'wb').write(arAudio.content)
        open('marathi.mp3', 'wb').write(mrAudio.content)
        if(arAudio.status_code == 200 & mrAudio.status_code == 200):
            arabic_audio = AudioSegment.from_file(file="arabic.mp3", format="mp3")
            marathi_audio = AudioSegment.from_file(file="marathi.mp3", format="mp3")
            combined = arabic_audio+ marathi_audio
            combined.export("ayah"+str(ayahNo)+"combined.mp3")
            return "ayah"+str(ayahNo)+"combined.mp3"
        else:
            print("Some Error occured")
    except requests.ConnectionError :
        print("Sorry Failed to establish a connection please check your network connection and try again :)")





def getFinalImage(arabicText , marathitext ,imageFile,ayahNo):
    fontFilearabic = "/home/fladdra/Desktop/webscraping/Utman.ttf"
    fontFilemarathi = "/home/fladdra/Desktop/webscraping/mangalb.ttf"
    fontAr = ImageFont.truetype(fontFilearabic, 48)
    fontMr = ImageFont.truetype(fontFilemarathi, 27)
    imageFile2= Image.open(imageFile)
    draw = ImageDraw.Draw(imageFile2)
    lengthmar = len(marathitext)
    length = len(arabicText)+150
    height=250
    height2=500

    wrapper = textwrap.TextWrapper(width=80)
    wordlist_arabic = wrapper.wrap(text=arabicText)
    wordslist_marathi = wrapper.wrap(text=marathitext)
    for word in wordlist_arabic:
        draw.text((length, height), word, (255,255,255), font=fontAr,align="right")
        height=height +50
    for word1 in wordslist_marathi:
        draw.text((30,height2), word1, (255,255,255), font=fontMr,align="center")
        height2= height2 +27
    
    #draw = ImageDraw.Draw(imageFile)
    imageFile2.save("outputayah" +str(ayahNo)+".jpg")
    imageFile2.close()
    return "outputayah" +str(ayahNo)+".jpg" 


def generateVideo(imageFile , audioFile ,ayahNo):
    #comaudio =AudioSegment.from_file(file=audioFile, format="mp3")
    audio = AudioFileClip(audioFile)
    #imageFile2= Image.open(imageFile)
    image = ImageClip(imageFile).set_duration(audio.duration) 
    video = image.set_audio(audio)
    video.write_videofile("/home/fladdra/Desktop/Quranic Ayahs/ayah"+ str(ayahNo) +".mp4", fps=24)
    return True






def main():
    fields=[]
    rows=[]
    fields,rows = readCSV("dbcopy.csv")
    imageFile1 = getImage()
    ayahNo=15
    len(rows)
    for ayahNo in range(10,12):
        finalAudio = getFinalAudio(rows[ayahNo],ayahNo)
        #audio = "/home/fladdra/Desktop/webscraping/ayah"+str(ayahNo)+"combined.mp3"
        #print(audio)
        arabicText , marathiText = get_ar_mr_text(rows[ayahNo])
        finalImage = getFinalImage(arabicText , marathiText , imageFile1 ,ayahNo)
        status = generateVideo(finalImage ,finalAudio ,ayahNo)
        os.remove(finalImage)
        os.remove(finalAudio)
        os.remove("arabic.mp3")
        os.remove("marathi.mp3")
    #print("Video generated =" + status)
if __name__ == "__main__":
    main()