# -*- coding:utf-8 -*-
# Author: Suummmmer
# Date: 2019-08-13

import subprocess
import pickle
import requests
from sub2conf_api import Sub2Conf, MyException


class V2rayL(object):
    def __init__(self):

        try:
            with open("/etc/v2rayL/ncurrent", "rb") as f:
                self.current, self.url, self.auto, self.check, self.http, self.socks = pickle.load(f)
        except:
            self.current = "未连接至VPN"
            self.url = None
            self.auto = False
            self.check = False
            self.http = 1081
            self.socks = 1080

        self.subs = Sub2Conf(subs_url=self.url)

        if self.auto and self.url:
            try:
                self.subs.update()
            except:
                with open("/etc/v2rayL/ncurrent", "wb") as jf:
                    pickle.dump(("未连接至VPN", None, False, False,
                                 self.http, self.socks), jf)
                raise MyException("更新失败, 已关闭自动更新，请更新订阅地址")

    def auto_check(self, flag):
        if flag:
            with open("/etc/v2rayL/ncurrent", "wb") as jf:
                self.check = True
                pickle.dump((self.current, self.url, self.auto, self.check), jf)
        else:
            with open("/etc/v2rayL/ncurrent", "wb") as jf:
                self.check = False
                pickle.dump((self.current, self.url, self.auto, self.check), jf)

    def subscribe(self, flag):
        if flag:
            with open("/etc/v2rayL/ncurrent", "wb") as jf:
                self.auto = True
                pickle.dump((self.current, self.url, self.auto, self.check,
                             self.http, self.socks), jf)
        else:
            with open("/etc/v2rayL/ncurrent", "wb") as jf:
                self.auto = False
                pickle.dump((self.current, self.url, self.auto, self.check,
                             self.http, self.socks), jf)

    def connect(self, region, flag):
        if not flag:
            self.subs.setconf(region, self.http, self.socks)
        try:
            output = subprocess.getoutput(["sudo systemctl status v2rayL.service"])
            if "Active: active" in output:
                subprocess.call(["sudo systemctl restart v2rayL.service"], shell=True)
            else:
                subprocess.call(["sudo systemctl start v2rayL.service"], shell=True)
                output = subprocess.getoutput(["sudo systemctl status v2rayL.service"])
                if "Active: active" not in output:
                    raise MyException("v2rayL.service 启动失败")
        except:
            raise MyException("连接失败，请尝试更新订阅后再次连接或检查v2rayL.service是否正常运行")
        else:
            self.current = region
            with open("/etc/v2rayL/ncurrent", "wb") as jf:
                pickle.dump((self.current, self.url, self.auto, self.check,
                             self.http, self.socks), jf)

    def disconnect(self):
        try:
            output = subprocess.getoutput(["sudo systemctl status v2rayL.service"])
            if "Active: active" in output:
                subprocess.call(["sudo systemctl stop v2rayL.service"], shell=True)
                self.current = "未连接至VPN"
                with open("/etc/v2rayL/ncurrent", "wb") as jf:
                    pickle.dump((self.current, self.url, self.auto, self.check,
                                 self.http, self.socks), jf)
            else:
                if self.current != "未连接至VPN":
                    self.current = "未连接至VPN"
                    with open("/etc/v2rayL/ncurrent", "wb") as jf:
                        pickle.dump((self.current, self.url, self.auto, self.check,
                                     self.http, self.socks), jf)
                else:
                    raise MyException("服务未开启，无需断开连接.")
        except Exception as e:
            raise MyException(e.args[0])

    def update(self, url):
        if url:  # 如果存在订阅地址
            self.subs = Sub2Conf(subs_url=url)
            self.subs.update()
            with open("/etc/v2rayL/ncurrent", "wb") as jf:
                pickle.dump((self.current, url, self.auto, self.check,
                             self.http, self.socks), jf)

        else:
            if self.current in self.subs.saved_conf["subs"]:
                try:
                    self.disconnect()
                except:
                    pass

                with open("/etc/v2rayL/ncurrent", "wb") as jf:
                    pickle.dump(("未连接至VPN", None, False, False,
                                 self.http, self.socks), jf)

            else:
                with open("/etc/v2rayL/ncurrent", "wb") as jf:
                    pickle.dump((self.current, None, False, False,
                                 self.http, self.socks), jf)

            with open("/etc/v2rayL/data", "wb") as f:
                pickle.dump({"local": self.subs.saved_conf["local"], "subs": {}}, f)

    def addconf(self, uri):
        self.subs = Sub2Conf(conf_url=uri)
        self.subs.add_conf_by_uri()

    def delconf(self, region):
        self.subs.delconf(region)

    def ping(self):
        try:
            proxy = {
                "http": "127.0.0.1:{}".format(self.http),
                "https": "127.0.0.1:{}".format(self.http)
            }
            req = requests.get("http://www.google.com", proxies=proxy, timeout=10)
            if req.status_code == 200:
                return int(req.elapsed.total_seconds()*1000)
            return req.reason
        except:
            raise MyException("测试超时")


if __name__ == '__main__':
    def ping():
        try:
            proxy = {
                "http": "127.0.0.1:1081",
                "https": "127.0.0.1:1081"
            }
            req = requests.get("http://www.google.com", proxies=proxy, timeout=10)
            if req.status_code == 200:
                return req.elapsed.total_seconds()*1000
        except:
            print(11)