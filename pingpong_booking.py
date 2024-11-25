import json
import time
import datetime

import requests
from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from utils import init_driver, login
import base64


class YdmVerify(object):
    _custom_url = "http://api.jfbym.com/api/YmServer/customApi"
    _token = "vybeXw8HV7rbd5dBdHcqzRbVvly141-UVUhC5Z8nmAM"
    _headers = {
        'Content-Type': 'application/json'
    }

    def slide_verify(self, slide_image, background_image, verify_type="20111"):
        # 滑块类型
        # 通用双图滑块  20111
        payload = {
            "slide_image": slide_image,
            "background_image": background_image,
            "token": self._token,
            "type": verify_type
        }

        resp = requests.post(self._custom_url, headers=self._headers, data=json.dumps(payload))
        # print(resp.text)
        return resp.json()['data']['data']


def skip_verify(driver: Chrome):
    # 下载验证码背景图片
    canvas = driver.find_element(By.XPATH,
                                 '/html/body/div[1]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/canvas')
    back_ground_64 = driver.execute_script("""
                        var canvas = arguments[0];
                        return canvas.toDataURL('image/png').substring(22);
                    """, canvas)

    slider_pic = driver.find_element(By.XPATH,
                                     '/html/body/div[1]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/div/div[2]/div[2]/div[1]/div[1]/img')
    # 获取图片的src属性值
    image_src = slider_pic.get_attribute('src')

    # 检查图片src是否是Base64编码
    if image_src.startswith('data:image'):
        # 提取Base64编码部分
        slider_base64_data = image_src.split(',')[1]
    else:
        # 如果不是Base64编码，则需要下载图片并进行编码
        import requests
        response = requests.get(image_src)
        slider_base64_data = base64.b64encode(response.content).decode('utf-8')

    y = YdmVerify()
    distance = int(y.slide_verify(slider_base64_data, back_ground_64, verify_type="20111")) - 22  # 验证码应该位移的轨迹
    # distance = 63
    distance = distance * (50 / 63)  # 这个误差我不知道怎么得出的
    print(f"验证码位移距离为{distance}")
    # 找到滑块元素
    slider = driver.find_element(By.XPATH,
                                 '/html/body/div[1]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/div/div[2]/div[2]/div[2]/div[1]/div[1]/img')

    # 使用ActionChains模拟拖动滑块
    action = ActionChains(driver)
    action.click_and_hold(slider).perform()
    action.move_by_offset(distance, 0).perform()
    time.sleep(0.1)
    action.release().perform()


time_table = {1: "8:00-9:00", 2: "9:00-10:00", 3: "10:00-11:00", 4: "11:00-12:00", 5: "12:00-13:00", 6: "13:00-14:00", 7: "14:00-15:00", 8: "15:00-16:00", 9: "16:00-17:00", 10: "17:00-18:00", 11: "18:00-19:00", 12: "19:00-20:00", 13: "20:00-21:00"}

# 每个体育馆的展开按钮的path
gym_zhankai_path = {1: '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[2]/uni-view/uni-view[1]/uni-view[1]/uni-view[1]/uni-view/uni-view[1]',
            2: '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[2]/uni-view/uni-view[2]/uni-view[1]/uni-view[1]/uni-view/uni-view[1]',
            3: '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[2]/uni-view/uni-view[3]/uni-view[1]/uni-view[1]/uni-view/uni-view[1]',
            4: '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[2]/uni-view/uni-view[4]/uni-view[1]/uni-view[1]/uni-view/uni-view[1]'}

gym_name = {1: "松园体育馆", 2: "竹园体育馆", 3: "风雨体育馆", 4: "杏林体育馆"}
act_id = {1: [21, "羽毛球"], 2: [22, "乒乓球"], 3: [23, "健身房"]}

information = []


def xuanze_shijian(times: list, driver: Chrome, num: int, accept: int) -> list:
    chosen = False
    delete_time = []
    successful_time = []
    last_t = -1
    for t in times:
        if last_t != -1 and t - last_t != 1:
            print(f"时间段{time_table[t]}不连续，将分多次预约")
            break
        time_button = driver.find_element(By.XPATH, '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[1]/uni-view[2]/uni-view[3]/uni-view[{}]'.format(t))
        if "disable" in time_button.get_attribute("class"):
            print("时间段{}已被预约".format(time_table[t]))
            if accept == 1:
                print("你接受这种情况，将继续预约其他时间段")
                continue
            else:
                print(f"你不接受这种情况，将退出对场地{num}的预约")
                return
        time_button.click()
        last_t = t
        chosen = True
        delete_time.append(t)
    for t in delete_time:
        successful_time.append(t)
        times.remove(t)
    if chosen:
        confirm_button = driver.find_element(By.XPATH, '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[1]/uni-view[3]/uni-view[2]/uni-view[3]')
        confirm_button.click()
        # 完成验证码：
        skip_verify(driver)
        # 出现成功界面
        try:
            success = driver.find_element(By.XPATH,
                                          '//*[@id="app"]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[1]/uni-view[1]/uni-text/span')
            if success.text == '预约成功':
                for t in successful_time:
                    information.append((num - 1, time_table[t]))
                return information
            else:
                print("时间段已被预约")
                return []
        except NoSuchElementException:
            print("时间段均被预约")
            return []
    else:
        print("时间段均已被预约")
        return []


def book_pingpong(driver: Chrome, gym: int, fav_time: list, accept: int, id: int, fav_ground: list) -> int:
    # 遍历每个场地号，查看是否能预约
    yuyue = False
    wait = True
    # 只选择用户的场子，如果额外选择候补，则在后面进行另一轮预约
    driver.get('https://gym.whu.edu.cn/hsdsqhafive/pages/index/reserve?typeId={}'.format(act_id[id][0]))
    next_day = driver.find_element(By.XPATH, '/html/body/div[1]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[1]/uni-view[1]/uni-view[3]')
    # 循环直到当前时间大于18:00，不然抢不到场子
    while wait:
        # 获取当前时间
        now = datetime.datetime.now()
        target_time = now.replace(hour=18, minute=0, second=0, microsecond=300)
        # 检查当前时间是否大于18:00
        if now > target_time:
            print(f"已到{now.hour}:{now.minute}:{now.second}:{now.microsecond}！开始预约！")
            wait = False
            break  # 结束循环
        else:
            print(f"当前时间是{now.hour}:{now.minute}:{now.second}，等待中...")
            time.sleep(0.1)  # 等待0.1秒再次检查

    next_day.click()  # 切换到下一天
    # 展开场馆时间
    zhankai = driver.find_element(By.XPATH, gym_zhankai_path[int(gym)])
    # print(zhankai.get_attribute("class"))
    zhankai.click()

    for i in fav_ground:
        i += 1
        yuyue_button = driver.find_element(By.XPATH, '/html/body/div[1]/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[2]/uni-view/uni-view[{}]/uni-view[2]/uni-view/uni-view/uni-view[{}]/uni-view[5]/uni-text'.format(int(gym), i))
        # 我们发现每个场馆有他自己的编号id, 且每个场馆的场地号也是有自己的id, 通过这个id我们可以直接定位到对应的场地
        if "disable" in yuyue_button.get_attribute("class"):
            print("场地{}已预约满".format(i - 1))
            i += 1
            continue
        yuyue_button.click()  #  进入选择时间阶段
        if xuanze_shijian(fav_time, driver, i, accept):
            yuyue = True
        i += 1
    if yuyue:
        print(f"预约成功，感谢使用！")
        print("预约信息：")
        print(f"活动：{act_id[id][1]}")
        print(f"体育馆：{gym_name[int(gym)]}")
        for info in information:
            print(f"场地：{info[0]}: 时间：{info[1]}")
        return True
    else:
        print("预约失败，感谢使用！")
        return False
