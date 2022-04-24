#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Erimus'
# 这个版本用的uiautomator
# https://github.com/openatx/uiautomator2
# 先要把模拟器下adb所在目录加入环境变量
# 确认下截图为540x960（设置/分辨率/自定义）
# 使用极速模式 DirectX 颜色和其它模式会有所不同
# 先启动夜神模拟器，然后运行本程序。

from util.uiautomator2 import *
import os
import random
from toolbox import set_log, FS, CSS, Timer, time, countdown, formatJSON, beep, kill_process
import fire

# ═══════════════════════════════════════════════
d = im_pixel = ''
package_name = 'com.supercell.clashroyale'
SHOW_CHECK_COLOR_LOG = 0  # 是否显示截图检查颜色的色值 debug用
interval = 1
mismatch_count = 0
# ═══════════════════════════════════════════════


def screen_capture(save=0):
    global im_pixel
    tm = Timer()
    im = d.screenshot()
    im_pixel = im.load()
    # im.show()
    if save:
        HERE = os.path.abspath(os.path.dirname(__file__))
        im.save(os.path.join(HERE, 'screen_shot/sc.png'))
    log.info(CSS(f'{"Screen capture took ":-<25s} {tm.gap()}', 'lk'))


def check_point(pos, color, tolerance=20, showLog=0):  # 棋子取色精确范围
    r, g, b = color
    src = im_pixel[tuple(pos)]
    if showLog:
        log.info(CSS(f'{pos} = {src}', 'lk'))
    return ((r - tolerance < src[0] < r + tolerance)
            and (g - tolerance < src[1] < g + tolerance)
            and (b - tolerance < src[2] < b + tolerance))


def check_match(*conditionList, tolerance=20, showLog=SHOW_CHECK_COLOR_LOG):
    # 标准输入格式为(([x,y],[r,g,b]),...)
    if not isinstance(conditionList[0], tuple):  # 简化输入 [x,y],[r,g,b] 转换
        conditionList = [conditionList]
    for pos, color in conditionList:
        if not check_point(pos, color, tolerance=tolerance, showLog=showLog):
            return False
    return True


def click(x, y, info='', wait=0):
    if info:
        log.info(CSS(info))
    d.click(x, y)
    countdown(wait)


def debug():
    time.sleep(3)
    screen_capture(save=1)
    raise


# ═══════════════════════════════════════════════


class UI():

    def 开始对战(self):
        return check_match(([240, 600], [255, 185, 0]),     # 左黄
                           ([300, 600], [0, 176, 255]))     # 右蓝

    def 确认无金币(self):
        return check_match(([120, 340], [98, 104, 124]),    # 弹出框灰框
                           ([120, 600], [227, 238, 243]),   # 浅灰底
                           ([270, 620], [78, 175, 255]))    # 确认蓝色按钮

    def 战斗中(self):
        # 这个匹配方式在对方或我方主城失血后就失效了
        # 等于对方主城失血就匹配不到模式，于是不出兵，可以保证输。
        # return check_match(([270, 42], [230, 188, 40]),     # 敌方皇冠
        #                    ([270, 734], [230, 188, 40]),    # 我方皇冠
        #                    ([50, 810], [255, 255, 255]))    # 左下表情图标

        # 始终有效的判断方式
        return check_match(([25, 65], [252, 194, 70]),      # 敌方奖杯
                           ([140, 940], [255, 29, 228]),    # 我方圣水图标
                           ([50, 810], [255, 255, 255]))    # 左下表情图标

    def 能量未满(self):
        return check_match(([445, 935], [88, 68, 50]))      # 能量条背景

    def 结束(self):
        return check_match(([270, 315], [156, 12, 71]),     # 敌方底色
                           ([270, 595], [40, 103, 186]),    # 我方底色
                           ([270, 860], [77, 174, 255]))    # 下方按钮

    def 升降级(self):
        return check_match(([5, 955], [70, 83, 103]),       # 左下
                           ([535, 955], [70, 83, 103]),     # 右下
                           ([270, 925], [78, 175, 255]))    # 按钮

    def 重新登录(self):
        return check_match(([80, 410], [60, 60, 60]),       # 左上
                           ([450, 540], [60, 60, 60]))      # 右下


ui = UI()


# ═══════════════════════════════════════════════
CY = 850  # card y
CARD = ((170, CY), (270, CY), (370, CY), (470, CY))  # 卡片坐标
AXIS = {'左': 125, '右': 405, '上': 200, '下': 720}


def random_play(power_empty=True, degrade=0):
    card_index = random.randint(0, 3)
    axis_x = random.choice(('左', '右'))
    axis_y = random.choice(('上', '下'))
    log.info(f"{CSS(f'战斗中', 'r')} | 卡片{card_index+1} | {axis_x}{axis_y}")
    if power_empty or degrade:
        countdown(random.randint(1, interval))
    click(*CARD[card_index])
    click(AXIS[axis_x], AXIS[axis_y])


# ═══════════════════════════════════════════════


def play_game(degrade=0):  # 寻找起点和终点坐标
    global mismatch_count

    screen_capture()  # 获取截图

    if ui.开始对战():  # 冒险上的白色区域
        log.info(FS.rainbow("=" * 40))
        click(160, 620, CSS('开始对战', 'ly'), wait=3)

    elif ui.确认无金币():
        if degrade:
            click(270, 600, CSS('确认无金币', 'b'), wait=5)  # 继续游戏
        else:
            print('无法再获得金币 退出游戏')
            # kill_process('Nox')  # quit_emulator
            d.press('home')
            return 'quit'

    elif ui.战斗中():
        random_play(power_empty=ui.能量未满(), degrade=degrade)

    elif ui.结束():
        click(270, 850, CSS('===== 结束 =====', 'b'), wait=3)

    elif ui.升降级():
        click(270, 920, '升降级', wait=3)

    elif ui.重新登录():
        print(CSS('需要重新登陆'))
        countdown(300)  # 给手机留出操作时间
        click(120, 525, '重新登录', wait=5)

    else:
        mismatch_count += 1
        log.info(CSS(f'截图不匹配任何模式 {mismatch_count}', 'lk'))
        if mismatch_count > 20:
            mismatch_count = 0
            launch_app(d, package_name)
        countdown(3)
        return

    mismatch_count = 0


# ═══════════════════════════════════════════════


def main(degrade=0):
    # degrade 是否为了降级
    global interval
    interval = degrade or interval
    print(f'{degrade = } | {interval = }')

    global d
    d = get_device()
    launch_app(d, package_name)

    # screen_capture(save=1)  # 测试用截屏
    # print(d.app_current())
    # return

    # 防出错自动重启
    while True:
        try:
            r = play_game(degrade=degrade)
            if r == 'quit':
                return
        except Exception as e:
            print(repr(e))
            # restart game
            try:
                launch_app(d, package_name, force=True)
            except Exception as e:
                beep(1)
                raise e


# ═══════════════════════════════════════════════


if __name__ == '__main__':

    log = set_log(level='INFO')
    fire.Fire(main)

    '''
    使用方法 命令行
    python clash_royale.py {degrade}

    degrade 是否为了强制降级
    默认零，无金币时自动退出模拟器。

    宝箱还是需要手动开。
    '''
