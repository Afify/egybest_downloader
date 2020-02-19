#!/usr/bin/env python3

import os
import sys
# from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.firefox.options import Options as FOptions


def get_request(url):
    """ send get request return all """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    if req.status_code == 200:
        result = soup.find_all("div", class_="movies_small")[0]
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

def check_inserted_link(url):
    if check_url(url) != 200:
        print("no internet or invalid link")
        sys.exit()

def get_season_eps(season_url):
    """ get season url page, return each_ep url """
    req = get_request(season_url)
    eps_list = req.find_all("a")
    return eps_list

class Egybest():
    """ open url of a movie get download link """
    def __init__(self, url, selected_season=False):
        self.url = url
        self.selected_season = selected_season
        self.firefox_driver_path = ""
        self.chrome_driver_path = ""
        self.ser_mov_name = ""
        self.output_dir = ""
        self.type = ""
        self.series_sum_eps = ""
        self.series_done = ""
        self.output_file = self.output_dir + self.ser_mov_name + ".txt"
        self.driver = ""

        check_inserted_link(self.url)
        self.get_url_data()
        self.start_browser()

        if self.type == "series":
            self.get_series_urls(self.url)
        else:
            self.get_links(self.url)

    def get_url_data(self):
        """ configure inputted url """
        self.url = self.url.rsplit('?', 1)[0]
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        self.ser_mov_name = self.url.rsplit('/', 1)[-1]
        self.output_dir = "./"
        self.type = self.url.split('/')[3]
        if self.selected_season:
            self.output_file = (
                self.output_dir + self.ser_mov_name +
                "_" + self.selected_season + ".txt")
        else:
            self.output_file = self.output_dir + self.ser_mov_name + ".txt"
        if os.path.isfile(self.output_file):
            os.remove(self.output_file)
        print(self.ser_mov_name)
        print("Checking Browsers")

    def start_browser(self):
        """ start Browsers """

        try:
            print("try Firefox")
            conf_options = FOptions()
            conf_options.add_argument("--headless")
            self.driver = webdriver.Firefox(
                options=conf_options,
                service_log_path=os.path.devnull)

        except WebDriverException:
            print("Firefox not installed")

            try:
                print("try Chrome")
                conf_options = COptions()
                conf_options.add_argument("--headless")
                self.driver = webdriver.Chrome(
                    options=conf_options)

            except WebDriverException:
                print("Chrome not installed")
                print("Please install Firefox or Google Chrome.")
                sys.exit()


    def get_series_urls(self, url):
        """ if url is series, use BeautifulSoup get sum of seasons
        for each season get it's episodes,
        for each episode send to get_links() """
        req = get_request(url)
        seasons_list = req.find_all("a")
        number_of_seasons = len(seasons_list)
        season_eps = []
        all_eps = []

        for each_season_page in seasons_list:
            season_eps.append(get_season_eps(each_season_page['href']))


        season_eps = season_eps[::-1] # reverse order

        if not self.selected_season:
            for each_season in season_eps:
                for each_ep in each_season:
                    all_eps.append(each_ep['href'])

        if self.selected_season:
            for each_ep in season_eps[int(self.selected_season)-1]:
                all_eps.append(each_ep['href'])

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
            print("clean")

        down_css_sel = ".dls_table > tbody:nth-child(2) > "
        down_css_sel += "tr:nth-child(1) > td:nth-child(4) > a:nth-child(1)"
        down_xpath = "/html/body/div[4]/div[2]/div[3]/div[7]/table/tbody/tr[1]/td[4]/a[1]"
        vid_css_sel = "a.bigbutton:nth-child(1)"
        vid_xpath = "/html/body/div[1]/div/p[2]/a[1]"

        # 1- open page
        self.gototab(0)
        print("try opening link")
        self.driver.get(url)
        print("link opened")

        # 2- click tahmil button
        self.gototab(0)
        self.get_css_sel(down_css_sel).click()
#         self.get_xpath(down_xpath).click()

        # 3- close tab 0 egybest
        self.gototab(0)
        self.driver.close()

        # 4- got to vidstream page get download button class
        self.gototab(0)
#         button_status = self.check_css_sel(vid_css_sel)
        button_status = self.check_xpath(vid_xpath)

        print(button_status)

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
                print("ad didn't reload")

#             button_status = self.check_css_sel(vid_css_sel)
            button_status = self.check_xpath(vid_xpath)

        url = self.get_xpath(vid_xpath).get_attribute("href")

        # get link write to file
        ofile = open(self.output_file, "a")
        ofile.writelines(url + "\n\n")
        ofile.close()
        print("written")

        if self.type == "movie":
            sys.exit()
            self.driver.quit()

        # check type series count
        elif self.type == "series":
            self.series_done += 1
            print(
                self.ser_mov_name + " " +
                str(self.series_done) + " / " +
                str(self.series_sum_eps))
            if self.series_done == self.series_sum_eps:
                print("All series episodes are finished")
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
        try:
            Egybest(url=sys.argv[1], selected_season=sys.argv[2])

        except IndexError:
            Egybest(url=sys.argv[1])

    except KeyboardInterrupt:
        print("\n\033[31mError, Keyboard Interrupted\033[00m\n")
