#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Erimus'

import uiautomator2
import subprocess
import re

import os

# ═══════════════════════════════════════════════

# 检测adb设备ip
def detect_adb_devices():
    cmd = 'adb devices'
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.decode('utf-8')
    print(f'{out = }')
    ports = re.findall(r'(?<=127\.0\.0\.1:)\d+', out)
    print(f'{ports = }')
    if ports:
        return ports


# 获取模拟器
def get_device(port=None):
    # 这里的端口号可以用 adb devices 查看。
    # 强制用端口号连接，有时候在 adb devices 找不到设备时仍可强制连接。
    if os.name == 'nt':
        if port is None:
            port_list = detect_adb_devices() or range(62001, 65535)
        else:
            port_list = [port]

        for port in port_list:
            device = f'127.0.0.1:{port}'
            try:
                print(f'Try connect device: {device}')
                d = uiautomator2.connect_adb_wifi(device)  # connect to device
                break
            except Exception:
                pass
    else:
        d = uiautomator2.connect()
    [print(f'{k}: {v}') for k, v in d.info.items()]
    return d


# 启动App
# 获取游戏包名称
# adb shell dumpsys window w |findstr \/ |findstr name=
# 或者直接运行 然后看 current app
def launch_app(d, package_name, force=False):
    current = d.app_current().get('package')
    print(f'Current App: {current}')
    if current == package_name:
        return

    pid = None
    while not pid or force:
        print(f'Restart: {package_name}')
        running_app = d.app_list_running()
        print(f'{running_app = }')
        if package_name in running_app:
            print(f'[{package_name}] is running')
        else:
            print(f'[{package_name}] not running')
        d.session(package_name, attach=True)
        # d.app_stop(package_name)
        d.app_start(package_name, use_monkey=True)  # 未启动的话会启动
        pid = d.app_wait(package_name)
        if pid:
            print(f'App [{package_name}] running in PID: {pid}')
            return


# ═══════════════════════════════════════════════


if __name__ == '__main__':

    detect_adb_devices()

    d = get_device()
    package_name = 'com.netease.cloudmusic'
    launch_app(d, package_name)
