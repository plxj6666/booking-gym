import os
import platform
import time
import datetime

from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

act_id = {1: [21, "羽毛球"], 2: [22, "乒乓球"], 3: [23, "健身房"]}
def init_driver() -> Chrome:
    if 'Windows' in platform.platform():
        executable_path = os.path.join(os.path.dirname(__file__), './driver/chromedriver.exe')
    else:
        executable_path = os.path.join(os.path.dirname(__file__), './driver/chromedriver')
    service = Service(executable_path=executable_path)
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(3)
    return driver

def is_captcha_present(driver):
    try:
        captcha_input = driver.find_element(By.XPATH, '//*[@id="dxcaptcha"]')  # 请替换为验证码输入框的实际XPATH
        return True
    except NoSuchElementException:
        return False

def login(driver: Chrome, username: str, password: str, id: int) -> bool:
    driver.get(
        'https://cas.whu.edu.cn/authserver/login?service=https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId={}'.format(act_id[id][0]))
    username_input = driver.find_element(By.XPATH, '//*[@id="username"]')
    username_input.send_keys(username)
    password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_input.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//*[@id="casLoginForm"]/p[2]/button')
    login_button.click()
    loginstates = True
    time.sleep(2)
    # 检查是否出现验证码
    if is_captcha_present(driver):
        print("验证码出现，请手动输入后继续脚本执行。")
        input("按Enter键继续...")
    else:
        loginstates = True
        try:
            loginstate = driver.find_element(By.XPATH, '//*[@id="casLoginForm"]/*[@id="msg"]').text
            if loginstate == "您提供的用户名或者密码有误":
                loginstates = False
        except:
            pass

    return loginstates
