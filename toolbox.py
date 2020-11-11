#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Erimus'

# 全局常用工具箱

import sys
import json
import time
from datetime import datetime, timedelta
import logging
import coloredlogs

# ═══════════════════════════════════════════════ logging

logging.basicConfig(level=logging.INFO,
                    format=('[%(asctime)s] %(message)s'),
                    datefmt='%m-%d %H:%M:%S')

log = logging.getLogger()
coloredlogs.DEFAULT_FIELD_STYLES = {
    'asctime': {},
    'hostname': {'color': 'magenta'},
    'levelname': {'color': 'black', 'bold': True},
    'name': {'color': 'blue'},
    'programname': {'color': 'cyan'}
}
coloredlogs.DEFAULT_LEVEL_STYLES = {
    'critical': {'color': 'red', 'bold': True},
    'debug': {'color': 'green'},
    'error': {'color': 'red'},
    'info': {},
    'notice': {'color': 'magenta'},
    'spam': {'color': 'green', 'faint': True},
    'success': {'color': 'green', 'bold': True},
    'verbose': {'color': 'blue'},
    'warning': {'color': 'yellow'}
}


def set_log(level='INFO', logger=None,
            fmt='[%(asctime)s] %(message)s', datefmt='%H:%M:%S'):
    [logging.root.removeHandler(hdlr) for hdlr in logging.root.handlers[:]]
    if logger is not None:
        global log
        log = logging.getLogger(logger)
    coloredlogs.install(level=level, logger=log,
                        fmt=fmt,
                        datefmt=datefmt)
    return log


# ═══════════════════════════════════════════════ 颜色格式
import colorama
from colorama import Fore as FG
from colorama import Back as BG
from colorama import Style as STYLE
colorama.init(autoreset=True)


class FontStyle():
    def __init__(self):
        self.bold = STYLE.BRIGHT
        self.end = STYLE.RESET_ALL
        _colors_alias = {  # rgb/cmyk/w
            'red': ['r'],
            'green': ['g'],
            'blue': ['b'],
            'cyan': ['c'],
            'magenta': ['m'],
            'yellow': ['y'],
            'black': ['k'],
            'white': ['w'],
        }
        self._colors = {}  # {alias: full name}
        for k, v in _colors_alias.items():
            self._colors[k] = k.upper()
            self._colors['light' + k] = 'LIGHT' + k.upper() + '_EX'
            for alias in v:
                self._colors[alias] = k.upper()
                self._colors['l' + alias] = 'LIGHT' + k.upper() + '_EX'

    def css(self, string, style=None):
        # 自定义组合style，style由位置/粗体/亮色/颜色4种类型构成，小写，由.分割。
        # 位置/粗体/亮色 需要在颜色前定义。
        if style is None:  # default style
            if isinstance(string, str):
                return FG.LIGHTYELLOW_EX + string + self.end
            if isinstance(string, int) or isinstance(string, float):
                return FG.MAGENTA + str(string) + self.end
            return FG.WHITE + str(string) + self.end

        if style is '':
            return string

        string = str(string)
        styles = style.lower().split('/')  # 字体样式/背景样式
        for pos, style in enumerate(styles):
            if pos == 0:  # 前景
                for mk in ['bold', 'bd', 's', 'em']:
                    if style.startswith(mk):
                        string = self.bold + string
                        style = style[len(mk):]  # 截取粗体之后的样式
            if style in self._colors:
                color = self._colors[style].upper()
                if color == 'BLACK' and len(styles) == 1:
                    string = BG.LIGHTBLACK_EX + string
                string = eval(['FG.', 'BG.'][pos] + color) + string
            else:
                print(self.warning(f'Color error: "{style}"'))
                self.help()
        return string + self.end

    def help(self):
        print('CSS(string, params).\n'
              'e.g. style="boldLightRed/white" or "bdlr/w"\n'
              'Params have 3 part.\n'
              '1. Position. "/" split font style and background color.\n'
              '2. Bold.     "bold|bd|strong|s|em" (only valid on mac).\n'
              '3. Color.    (alias----full name)')
        for k, v in self._colors.items():
            print('   ' + self.css(f'{k:-<20s}{v}', k))

    def title(self, string, fg='lw', bg='r'):
        return '\n' + self.css(f' {string} ', f'bd{fg}/{bg}') + '\n'

    def warning(self, string):
        return self.css(f' {string} ', f'bdr/lw')

    def rainbow(self, string, bg=False):
        c = ['r', 'lr', 'y', 'ly', 'g', 'lg', 'c', 'lc', 'b', 'lb', 'm', 'lm']
        c = c * (len(string) // len(c) + 1)
        if not bg:
            return ''.join([self.css(s, c[i]) for i, s in enumerate(string)])
        return ''.join([self.css(s, 'k/' + c[i]) for i, s in enumerate(string)])


FS = FontStyle()
CSS = FS.css
# FS.help()

# ═══════════════════════════════════════════════ 打印耗时


# 时间统计
class Timer():

    def __init__(self, unit='s'):
        self.timeList = [datetime.now()]
        self.s = self._start = self.timeList[0]  # 开始
        self.e = self._end = self.timeList[-1]  # 结束
        self.unit = unit

    def now(self):  # 插入当前时间
        self.timeList.append(datetime.now())
        self.e = self._end = self.timeList[-1]  # 结束
    end = now

    def gap(self):  # 和上一次的时间间隔
        self.now()  # 插入当前时间
        gap = self.timeList[-1] - self.timeList[-2]
        return self.__print(gap)

    def total(self):  # 开始至今的总计
        self.now()  # 插入当前时间
        total = self.timeList[-1] - self.timeList[0]
        return self.__print(total)

    def __print(self, t):
        if t == timedelta(0):
            tstr = '0'
        elif self.unit == 's':  # second
            tstr = '%.3f' % (t.seconds + t.microseconds * (10**-6))
        else:  # self.unit == 'h'
            tstr = '%s' % t
        return tstr


# 倒计时
def countdown(wait=60):
    while wait > 0:
        text = f'Wait {FG.LIGHTYELLOW_EX}{wait}{STYLE.RESET_ALL} seconds...'
        sys.stdout.write(text)
        sys.stdout.flush()  # 显示输出
        if isinstance(wait, float):
            time.sleep(wait % 1)
            wait = int(wait)
        else:
            time.sleep(1)
            wait -= 1
        # 光标回到行首 用等长的空格覆盖 然后再回到行首
        sys.stdout.write('\r' + ' ' * len(text) + '\r')


# ═══════════════════════════════════════════════ 打印


def formatJSON(obj, indent=4, sort=False):
    return json.dumps(obj, ensure_ascii=False, indent=indent, sort_keys=sort)


# ═══════════════════════════════════════════════ 其它
from playsound import playsound


def beep(repeat=99):
    for i in range(repeat):
        playsound('1up.mp3')


# ═══════════════════════════════════════════════ 终止进程
import psutil
import signal
import os


def process_exists(pname):
    r = []
    for p in psutil.process_iter():
        try:  # sometime do not has name
            if pname.lower() in p.name().lower():  # contains in fullname
                r.append({'name': p.name(), 'pid': p.pid})
        except Exception:
            pass
    return r


def kill_process(pname):
    # 输入pid
    if isinstance(pname, int):
        print(f'PID [{pname}], kill process.')
        os.kill(pname, signal.SIGINT)
        return

    # 输入名称
    pList = process_exists(pname)
    for r in pList:
        pid = r.get('pid')
        print(f'PID of [{pname}] is [{pid}], kill process.')
        os.kill(pid, signal.SIGINT)
    else:
        print(f'[{pname}] is not running.')
