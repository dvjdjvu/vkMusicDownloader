#!/usr/bin/python3
#-*- coding: utf-8 -*-

import re
import os
import sys
import getopt
import pickle
from time import time
import vk_api
from vk_api import audio

class vkMusicDownloader():

    CONFIG_DIR = "config"
    USERDATA_FILE = "{}/UserData.datab".format(CONFIG_DIR) #файл хранит логин, пароль и id
    REQUEST_STATUS_CODE = 200 
    path = 'music/'

    def auth_handler(self, remember_device=None):
        code = input("Введите код подтверждения\n> ")
        if (remember_device == None):
            remember_device = True
        return code, remember_device

    def saveUserData(self):
        SaveData = [self.login, self.password, self.user_id]

        with open(self.USERDATA_FILE, 'wb') as dataFile:
            pickle.dump(SaveData, dataFile)

    def auth(self, new = False, user_id = None):
        try:
            if (os.path.exists(self.USERDATA_FILE) and new == False):
                with open(self.USERDATA_FILE, 'rb') as DataFile:
                    LoadedData = pickle.load(DataFile)

                self.login = LoadedData[0]
                self.password = LoadedData[1]
                if user_id :
                    self.user_id = user_id
                else :
                    self.user_id = LoadedData[2]
            else:
                if (os.path.exists(self.USERDATA_FILE) and new == True):
                    os.remove(self.USERDATA_FILE)

                self.login = str(input("Введите логин\n> ")) 
                self.password = str(input("Введите пароль\n> ")) 
                self.user_id = str(input("Введите id профиля\n> "))
                self.saveUserData()

            SaveData = [self.login, self.password, self.user_id]
            with open(self.USERDATA_FILE, 'wb') as dataFile:
                pickle.dump(SaveData, dataFile)

            vk_session = vk_api.VkApi(login=self.login, password=self.password)
            try:
                vk_session.auth()
            except:
                vk_session = vk_api.VkApi(login=self.login, password=self.password, auth_handler=self.auth_handler)
                vk_session.auth()
            print('Вы успешно авторизовались.')
            self.vk = vk_session.get_api()
            self.vk_audio = audio.VkAudio(vk_session)
        except KeyboardInterrupt:
            print('Вы завершили выполнение программы.')

    def main(self, auth_dialog = 'yes', user_id = None):
        try:
            if (not os.path.exists(self.CONFIG_DIR)):
                os.mkdir(self.CONFIG_DIR)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            
            if (auth_dialog == 'yes') :
                auth_dialog = str(input("Авторизоваться заново? yes/no\n> "))
                if (auth_dialog == 'yes'):
                    self.auth(new = True, user_id = user_id)
                elif (auth_dialog == "no"):
                    self.auth(new = False, user_id = user_id)
                else:
                    print('Ошибка, неверный ответ.')
                    self.main()
            elif (auth_dialog == "no") :
                self.auth(new = False, user_id = user_id)
            
            print('Подготовка к скачиванию...')
            
            # В папке music создаем папку с именем пользователя, которого скачиваем.
            info = self.vk.users.get(user_id=self.user_id)
            music_path = "{}/{} {}".format(self.path, info[0]['first_name'], info[0]['last_name'])
            if not os.path.exists(music_path):
                os.makedirs(music_path)
            
            index = 1
            time_start = time() # сохраняем время начала скачивания
            print("Скачивание началось...\n")
            
            os.chdir(music_path) #меняем текущую директорию
            audio = self.vk_audio.get(owner_id=self.user_id)
            print('Будет скачано: {} аудиозаписей с Вашей страницы.'.format(len(audio)))
            
            # собственно циклом загружаем нашу музыку 
            for i in audio:
                fileMP3 = "{} - {}.mp3".format(i["artist"], i["title"])
                fileMP3 = re.sub('/', '_', fileMP3)
                
                try:
                    if os.path.isfile(fileMP3) :
                        print("{} Уже скачен: {}.".format(index, fileMP3))
                    else :
                        print("{} Скачивается: {}.".format(index, fileMP3), end = "\n")
                    
                        os.system("ffmpeg -i {} -c copy -map a \"{}\"".format(audio[index-1]['url'], fileMP3))
                except OSError:
                    if not os.path.isfile(fileMP3) :
                        print("{} Не удалось скачать аудиозапись: {}".format(index, fileMP3))

                index += 1
            
            os.chdir("../..")
            albums = self.vk_audio.get_albums(owner_id=self.user_id)
            print('У Вас {} альбома.'.format(len(albums)))
            for i in albums:
                index = 1
                audio = self.vk_audio.get(owner_id=self.user_id, album_id=i['id'])
                
                print('Будет скачано: {} аудиозаписей из альбома {}.'.format(len(audio), i['title']))
                
                album_path = "{}/{}".format(music_path, i['title'])
                print(album_path)
                if not os.path.exists(album_path):
                    os.makedirs(album_path)
                    
                os.chdir(album_path) #меняем текущую директорию
                
                for j in audio:
                    fileMP3 = "{} - {}.mp3".format(j["artist"], j["title"])
                    fileMP3 = re.sub('/', '_', fileMP3)
                    try:
                        if os.path.isfile(fileMP3) :
                            print("{} Уже скачен: {}.".format(index, fileMP3))
                        else :
                            print("{} Скачивается: {}.".format(index, fileMP3), end = "")
                            
                            os.system("ffmpeg -i {} -c copy -map a \"{}\"".format(audio[index-1]['url'], fileMP3))
                    except OSError:
                        if not os.path.isfile(fileMP3) :
                            print("{} Не удалось скачать аудиозапись: {}".format(index, fileMP3))
                
                    index += 1
                
                os.chdir("../../..")
                
            time_finish = time()
            print("" + str(len(audio)) + " аудиозаписей скачано за: " + str(time_finish - time_start) + " сек.")
        except KeyboardInterrupt:
            print('Вы завершили выполнение программы.')

if __name__ == '__main__':
    vkMD = vkMusicDownloader()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hni:")
    except getopt.GetoptError:
        print('./main.py [-n] [-h] [-i]')
        sys.exit(2)
    
    auth_dialog = 'yes'
    user_id = None
    
    if len(args) == 1 :
        vkMD.main(auth_dialog = auth_dialog)
    else :
        for opt, arg in opts:
            if opt in ['-h']:
                print('./main.py [-n] [-h]')
                sys.exit()
            elif opt in ['-n']:
                auth_dialog = 'no'
            elif opt in ['-i']:
                user_id = int(arg)
        
        try:
            vkMD.main(auth_dialog = auth_dialog, user_id = user_id)
        except vk_api.exceptions.AccessDenied as e:
            print('[error]:', e)
