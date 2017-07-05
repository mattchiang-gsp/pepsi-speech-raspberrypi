#!/usr/bin/env python

import glob
import os
import vlc
import pygame

current_working_directory = os.getcwd()
os.chdir(current_working_directory)
for file in glob.glob('*.wav'):
	the_mp3 = file

pygame.mixer.init()
pygame.mixer.music.load(the_mp3)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
	continue


# os.startfile("file://" + current_working_directory + "/" + the_mp3)
# p = vlc.MediaPlayer("file://" + current_working_directory + "/" + the_mp3)
# print(p)
# p.play()