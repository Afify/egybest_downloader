#!/usr/bin/env python3

import os
import sys
import tkinter
from tkinter.ttk import Progressbar
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

from PIL import Image
from PIL import ImageTk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.firefox.options import Options as FOptions

# driver.save_screenshot('C:\\Users\\user\\Desktop\\screen.png') # save a screenshot to disk
# sbtn = driver.find_element_by_css_selector(vid_css_sel).get_attribute("class")
# sbtnc = sbtn.get_attribute("class")
# print(sbtnc)
# sbtn = driver.find_element_by_css_selector("a.bigbutton:nth-child(1)").get_attribute("class")
# sbtn = driver.find_element_by_xpath("/html/body/div[1]/div/p[2]/a[1]").get_attribute("class")

def get_request(url, html_tag, class_name):
    """ send get request return all """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    if req.status_code == 200:
        result = soup.find_all(html_tag, class_=class_name)
    else:
        print("check connection")
        sys.exit()
    return result

def check_url(url):
    """ check link, validate, connected  to internet  """
    try:
        req = requests.get(url)
        return req.status_code
    except requests.exceptions.ConnectionError:
        print("no internet")
#         sys.exit()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Egybest():
    """ open url of a movie get download link """
    def __init__(self, run_type):
        self.url = ""
        self.phantomjs_driver_path = ""
        self.firefox_driver_path = ""
        self.chrome_driver_path = ""
        self.icon_path = ""
        self.image_path = ""
        self.progress_val = ""
        self.progress = ""
        self.ser_mov_name = ""
        self.output_dir = ""
        self.type = ""
        self.series_sum_eps = ""
        self.series_done = ""
        self.output_file = self.output_dir + self.ser_mov_name + ".txt"
        self.driver = ""


        # get resourses
        self.get_resources_path(run_type)

        # open tkinter
        self.get_tk_win_url()



    def get_resources_path(self, the_type):
        """ get drivers and images path (case exe and normal python run """
        if the_type == "python":
            self.firefox_driver_path = "geckodriver64.exe"
            self.chrome_driver_path = "chromedriver.exe"
            self.icon_path = "wolf.ico"
            self.image_path = "wolf_rev_s.png"
        elif the_type == "exe":
            self.firefox_driver_path = resource_path("geckodriver64.exe")
            self.chrome_driver_path = resource_path("chromedriver.exe")
            self.icon_path = resource_path("wolf.ico")
            self.image_path = resource_path("wolf_rev_s.png")


    def get_tk_win_url(self):
        """ get url from tk """
        root_background = "black"
        title = "Egybest Downloder"

        self.root = tkinter.Tk()
        self.root.resizable(width=False, height=False)
        self.root.wm_title(title)
        self.root.wm_iconbitmap(self.icon_path)
        self.root.configure(background=root_background)

        self.title_label = tkinter.Label(
            self.root,
            bg="black",
            fg="green",
            text="Egybest Downloder",
            font=("system", 16))
        self.title_label.grid(row=1, column=0, sticky='EW')

        self.status_label = tkinter.Label(
            self.root,
            bg="black",
            fg="green",
            text="copy movie link\npress Crl+v then Enter",
            font=("system", 16))
        self.status_label.grid(row=2, column=0, sticky='EW')

        self.user_input = tkinter.Entry(
            self.root,
            borderwidth=0,
            highlightthickness=0,
            fg="green", bg="#222222",
            font=('system', 16))
        self.user_input.grid(row=3, column=0, sticky='EW')

        image_h = Image.open(self.image_path)
        tkimage = ImageTk.PhotoImage(image_h)
        logo = tkinter.Label(
            self.root,
            borderwidth=0,
            highlightthickness=0,
            bg="black", image=tkimage)
        logo.grid(row=0, column=0, sticky='EW')

        self.user_input.focus_set()
        self.user_input.bind("<Return>", self.enter_press)
        self.root.mainloop()

    def enter_press(self, event=None):
        """ after pressed enter with url """
        self.url = self.user_input.get()
        self.user_input.destroy()
        self.root.update()

        self.check_inserted_link()
        self.root.update()
        self.show_progress_bar()
        self.root.update()
        self.get_url_data()
        self.root.update()
        self.start_browser()
        self.root.update()

        if self.type == "series":
            self.get_series_urls(self.url)
        else:
            self.update_progress(enc=10)
            self.get_links(self.url)

    def show_progress_bar(self):
        # Progressbar
        self.progress_val = tkinter.IntVar()
        self.progress = Progressbar(
            self.root, length=200,
            mode="determinate", takefocus=True, maximum=100)
        self.progress['variable'] = self.progress_val
        self.progress.grid(row=3, column=0, sticky='EW')

    def update_status(self, string):
        """ update status in tk """
        self.status_label.config(text=string)
        self.root.update()

    def update_title(self, string):
        """ update status in tk """
        self.title_label.config(text=string)
        self.root.update()

    def get_url_data(self):
        self.url = self.url.rsplit('?', 1)[0]
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        self.ser_mov_name = self.url.rsplit('/', 1)[-1]
        self.output_dir = USER_HOME + "\\Desktop\\"
        self.type = self.url.split('/')[3]
        self.output_file = self.output_dir + self.ser_mov_name + ".txt"
        self.update_title(self.ser_mov_name)
        self.root.update()
        self.update_status("Checking Browsers")


    def check_inserted_link(self):
        if check_url(self.url) != 200:
            self.user_input.destroy()
            self.title_label.destroy()
            self.update_status("no internet or invalid link")
            sleep(2)
            sys.exit()

    def update_progress(self, enc):
        """ update_progress """
        if self.progress_val.get() >= 96:
            self.progress.destroy()
        else:
            self.progress.step(enc)
            self.root.update()

    def start_browser(self):
        """ start Browsers """

        try:
            print("try Firefox")
            conf_options = FOptions()
            conf_options.add_argument("--headless")
            self.driver = webdriver.Firefox(
                options=conf_options,
                service_log_path=os.path.devnull,
                executable_path=self.firefox_driver_path)

        except WebDriverException:
            print("Firefox not installed")

            try:
                print("try Chrome")
                conf_options = COptions()
                conf_options.add_argument("--headless")
#                 self.conf_options.add_argument('--disable-extensions')
#                 self.conf_options.add_argument('--disable-logging')
#                 self.conf_options.add_argument('--disable-gpu')
#                 self.conf_options.add_argument('--hide-scrollbars')
#                 self.conf_options.add_argument("--log-level=3")  # fatal

                self.driver = webdriver.Chrome(
                    options=conf_options,
                    executable_path=self.chrome_driver_path)

            except WebDriverException:
                print("Chrome not installed")
                print("Please install Firefox or Google Chrome.")
                sys.exit()

        self.update_progress(enc=5)


    def get_season_eps(self, season_url):
        """ get season url page, return each_ep url """
        req = get_request(season_url, "div", "movies_small")[0]
        eps_list = req.find_all("a")
        return eps_list


    def get_series_urls(self, url):
        """ if url is series, use BeautifulSoup get sum of seasons
        for each season get it's episodes,
        for each episode send to get_links() """
        res = get_request(url, "div", "movies_small")[0]
        seasons_list = res.find_all("a")
        number_of_seasons = len(seasons_list)
        season_eps = []
        all_eps = []

        for each_season_page in seasons_list:
            season_eps.append(self.get_season_eps(each_season_page['href']))
        self.update_progress(enc=5)

        for each_season in season_eps:
            for each_ep in each_season:
                all_eps.append(each_ep['href'])
        self.update_progress(enc=5)

        all_eps = all_eps[::-1] # reverse order

        result = "\033[32m" + self.ser_mov_name + " [" + str(number_of_seasons) +\
            " S - "  + str(len(all_eps)) + " E]\033[00m"

        self.series_sum_eps = len(all_eps)
        self.series_done = 0

        print(result)
        for each_ep in all_eps:
            print(each_ep)
            self.get_links(each_ep)

    def gototab(self, tab_num):
        """ go to spec tab """
        self.driver.switch_to.window(self.driver.window_handles[tab_num])


    def get_links(self, url):
        """ open headless firefox driver, open movie or episode page
        click download button go to vidstream page click download open file
        append download link """
#         get(85%)

        self.gototab(0)
        try:
            self.gototab(1)
            self.driver.close()
            self.gototab(1)
            self.driver.close()
        except IndexError:
            self.update_status("clean")

        self.update_progress(enc=5)
        down_css_sel = ".dls_table > tbody:nth-child(2) > "
        down_css_sel += "tr:nth-child(1) > td:nth-child(4) > a:nth-child(1)"
        down_xpath = "/html/body/div[4]/div[2]/div[3]/div[7]/table/tbody/tr[1]/td[4]/a[1]"
        vid_css_sel = "a.bigbutton:nth-child(1)"
        vid_xpath = "/html/body/div[1]/div/p[2]/a[1]"

        # 1- open page
        self.gototab(0)
        self.update_status("try opening link")
        self.driver.get(url)
        self.update_status("link opened")
        self.update_progress(enc=15)

        # 2- click tahmil button
        self.gototab(0)
        self.get_css_sel(down_css_sel).click()
#         self.get_xpath(down_xpath).click()
        self.update_progress(enc=15)

        # 3- close tab 0 egybest
        self.gototab(0)
        self.driver.close()

        # 4- got to vidstream page get download button class
        self.gototab(0)
#         button_status = self.check_css_sel(vid_css_sel)
        button_status = self.check_xpath(vid_xpath)

        self.update_status(button_status)
        self.update_progress(enc=15)

        # 5- if download button class not bigbutton loop
        while button_status != "bigbutton":            # class must be bigbutton
            self.gototab(0)                            # got to vidstream page
            self.get_css_sel(vid_css_sel).click()      # click download

            # 6- get current url wait until ad reload the download page
            self.gototab(0)                            # got to vidstream page
            tab_current_url = self.driver.current_url
            try:
                WebDriverWait(self.driver, 15).until(EC.url_changes(tab_current_url))
            except:
                self.update_status("ad didn't reload")

#             button_status = self.check_css_sel(vid_css_sel)
            button_status = self.check_xpath(vid_xpath)
            self.update_progress(enc=15)

        url = self.get_xpath(vid_xpath).get_attribute("href")
        self.update_progress(enc=15)

        # get link write to file
        ofile = open(self.output_file, "a")
        ofile.writelines(url + "\n\n")
        ofile.close()
        self.update_status("written")
        self.update_progress(enc=5)

        if self.type == "movie":
            self.root.destroy()
            sys.exit()
            self.driver.quit()

        # check type series count
        elif self.type == "series":
            self.series_done += 1
            self.update_title(
                self.ser_mov_name +
                str(self.series_done) + " / " +
                str(self.series_sum_eps))
            if self.series_done == self.series_sum_eps:
                self.update_status("All series episodes are finished")
                self.root.destroy()
                sys.exit()
                self.driver.quit()

    def get_xpath(self, the_xpath, seconds=15):
        """ return element from passed xpath """
        WebDriverWait(self.driver, seconds).until(
            EC.element_to_be_clickable((By.XPATH, the_xpath)))
#             EC.presence_of_element_located((By.XPATH, the_xpath)))
        return self.driver.find_element_by_xpath(the_xpath)

    def get_css_sel(self, the_css_sel, seconds=15):
        """ return element from passed xpath """
        WebDriverWait(self.driver, seconds).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, the_css_sel)))
#             EC.presence_of_element_located((By.CSS_SELECTOR, the_css_sel)))
        return self.driver.find_element_by_css_selector(the_css_sel)

    def check_xpath(self, the_xpath):
        """ check download button class  if bigbutton == link is ready """
        return self.get_xpath(the_xpath).get_attribute("class")

    def check_css_sel(self, the_css_sel):
        """ check download button class  if bigbutton == link is ready """
        return self.get_css_sel(the_css_sel).get_attribute("class")


if __name__ == "__main__":
    try:
        USER_HOME = str(Path.home())
        RUN_T = "python"
#         RUN_T = "exe"
        Egybest(run_type=RUN_T)

    except KeyboardInterrupt:
        print("\n\033[31mError, Keyboard Interrupted\033[00m\n")

