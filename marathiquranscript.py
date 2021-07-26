from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.VideoClip import ImageClip
from bidi.algorithm import get_display
from pydub import AudioSegment 
import requests
import textwrap
import csv
import sys
import os

def getImage():
    
    '''Takes image file path as input , checks it to be of 1080 by 1080 and returns
     the file path'''
    imagePath = input("Enter image file location.The file should be 1080p*1080p :")
    imageFile= Image.open(imagePath)
    width , height =imageFile.size
    if(width != 1080 & height!=1080):
        print("Please enter image with exactly 1080p*1080p dimensions")
        getImage()
    imageFile.close()
    return imagePath

def readCSV(csv_file):
    '''
    Takes the csv file with data as input and processes it to read the file and returns rows list 
    '''
    fields = []
    rows = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            rows.append(row)
    return rows

def get_ar_mr_text(row):
    '''
    Takes one row as the input and returns the arabic and marathi text cells respectively
    '''
    arabicText = row[2]
    marathiText = row[3]
    return arabicText,marathiText

def getFinalAudio(row ,ayahNo):
    '''
    Takes single row as input and the ayahno processes the row ,extracts the arabic and 
    marathi links , downloads the audio , combines them and returns the same.
    '''
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
        print("Sorry Failed to establish a connection .")
        print("Please check your network connection and try again :) ")

def getFinalImage(arabicText , marathitext ,imageFile,ayahNo):
    '''
    Takes the arabic marathi texts , image file path and ayahNo as input , renders the text 
    on the image with proper formatting and saves the image with ayahNo as the name
    '''
    fontFilearabic = os.getcwd()+"/Utman.ttf"
    fontFilemarathi = os.getcwd()+"/mangalb.ttf"
    fontAr = ImageFont.truetype(fontFilearabic, 48)
    fontMr = ImageFont.truetype(fontFilemarathi, 27)
    imageFile= Image.open(imageFile)
    draw = ImageDraw.Draw(imageFile)
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
    imageFile.save("outputayah" +str(ayahNo)+".jpg")
    imageFile.close()
    return "outputayah" +str(ayahNo)+".jpg" 

def generateVideo(imageFile , audioFile ,ayahNo):
    '''
    Takes image path audio file and ayahno as input and combines them to generate video ,
    finally saves the video with the name as ayahno in seperate folder named Quranic Ayahs 
    present in the same directory
    '''
    audio = AudioFileClip(audioFile)
    image = ImageClip(imageFile).set_duration(audio.duration) 
    video = image.set_audio(audio)
    store = os.getcwd()+"/Quranic Ayahs/ayah"+str(ayahNo)+".mp4"
    video.write_videofile(store, fps=24)
    return True

def main():
    rows=[]
    rows = readCSV("dbcopy.csv")
    

    print("\n")
    print("-----!!!!!-----Welcome to Quranic Ayahs Video generator-----!!!!!-----")
    print("Please select the correct numeric option as per your requirements.")
    print("1.Generate Videos for all the ayahs over one image as input.")
    print("2.Generate Videos for specific set of ayahs.")
    print("\n")
    menuopt= int(input())
    if (menuopt ==1):
        imageFilePath = getImage()
        ayahStart = 0
        ayahEnd =len(rows)
        for ayahNo in range(ayahStart,(ayahEnd+1)):
            finalAudio = getFinalAudio(rows[ayahNo],ayahNo)
            arabicText , marathiText = get_ar_mr_text(rows[ayahNo])
            finalImage = getFinalImage(arabicText , marathiText , imageFilePath ,ayahNo)
            status = generateVideo(finalImage ,finalAudio ,ayahNo)
            os.remove(finalImage)
            os.remove(finalAudio)
            os.remove("arabic.mp3")
            os.remove("marathi.mp3")
        print("Video generated for ayahs " + str(ayahStart) + "to ayah "+ str(ayahEnd))
    elif(menuopt == 2):
        imageFilePath = getImage()
        ayahStart = int(input("Enter the Ayah Number from where you want to generate the videos :"))
        ayahEnd = int(input("Enter the Ayah Number till where you want to generate the videos :"))
        for ayahNo in range(ayahStart,(ayahEnd+1)):
            finalAudio = getFinalAudio(rows[ayahNo],ayahNo)
            arabicText , marathiText = get_ar_mr_text(rows[ayahNo])
            finalImage = getFinalImage(arabicText , marathiText , imageFilePath ,ayahNo)
            status = generateVideo(finalImage ,finalAudio ,ayahNo)
            os.remove(finalImage)
            os.remove(finalAudio)
            os.remove("arabic.mp3")
            os.remove("marathi.mp3")
        print("Video generated for Ayah " + str(ayahStart) + " to Ayah "+ str(ayahEnd))
    else:
        print("Sorry wrong input !!! Exiting the program ")
        sys.exit()


if __name__ == "__main__":
    main()