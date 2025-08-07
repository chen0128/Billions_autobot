import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import threading
import time
import datetime
import random
import json
import os
import webbrowser
import urllib3
import tkinter as tk
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# === BillionsClaimGUI ===
class BillionsClaimGUI(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("💰 Billions 每日奖励批量签到工具")
        self.geometry("800x650")
        self.resizable(False, False)

        self.is_running = False
        self.use_proxy = tk.BooleanVar(value=False)
        self.proxies_list = []
        self.proxy_index = 0

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.102 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:116.0) Gecko/20100101 Firefox/116.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.4; rv:115.0) Gecko/20100101 Firefox/115.0",
        ]

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        style = ttk.Style()
        style.configure("TButton", font=("Microsoft YaHei", 10))
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("Title.TLabel", font=("Microsoft YaHei", 16, "bold"))

        ttk.Label(self, text="💰 Billions 批量每日签到", style="Title.TLabel").pack(pady=10)

        frame = ttk.LabelFrame(self, text="🍪 多个 Cookie（每行一个）")
        frame.pack(fill="x", padx=20, pady=10)

        promo_frame = ttk.Frame(self)
        promo_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(promo_frame, text="🎁 输入兑换码（可选）:").pack(side="left")
        self.promo_code_entry = ttk.Entry(promo_frame, width=30)
        self.promo_code_entry.pack(side="left", padx=10)

        self.cookie_text = scrolledtext.ScrolledText(frame, height=8, font=("Consolas", 10))
        self.cookie_text.pack(fill="both", padx=10, pady=10)

        proxy_frame = ttk.Frame(self)
        proxy_frame.pack(fill="x", padx=20, pady=5)

        self.proxy_checkbox = ttk.Checkbutton(proxy_frame, text="使用代理 (从 proxy.txt 读取)", variable=self.use_proxy)
        self.proxy_checkbox.pack(side="left")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        self.start_btn = ttk.Button(btn_frame, text="🚀 开始签到", command=self.start)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ttk.Button(btn_frame, text="⏹️ 停止", state=tk.DISABLED, command=self.stop)
        self.stop_btn.pack(side="left", padx=10)

        log_frame = ttk.LabelFrame(self, text="📋 日志输出")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 10),
                                                  bg="#1e1e1e", fg="white", insertbackground="white")
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, msg):
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.log_area.insert(tk.END, f"{timestamp} {msg}\n")
        self.log_area.see(tk.END)
        self.update_idletasks()

    def load_proxies(self):
        try:
            with open("proxy.txt", "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                self.proxies_list = lines
            self.log(f"🛡️ 加载代理列表，共 {len(self.proxies_list)} 个代理")
        except Exception as e:
            self.proxies_list = []
            self.log(f"⚠️ 读取 proxy.txt 失败: {e}")

    def get_next_proxy(self):
        if not self.proxies_list:
            return None
        proxy_str = self.proxies_list[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies_list)
        proxy_url = "http://" + proxy_str
        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    def start(self):
        cookies_input = self.cookie_text.get("1.0", tk.END).strip()
        if not cookies_input:
            messagebox.showwarning("缺少输入", "请输入至少一个 Cookie！")
            return

        if self.use_proxy.get():
            self.load_proxies()
            if not self.proxies_list:
                messagebox.showwarning("代理错误", "启用代理但 proxy.txt 文件无可用代理！")
                return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("🚀 开始批量签到任务...")

        cookies = [line.strip() for line in cookies_input.splitlines() if line.strip()]
        threading.Thread(target=self.claim_all, args=(cookies,), daemon=True).start()

    def stop(self):
        self.is_running = False
        self.log("🛑 用户请求停止任务...")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def claim_all(self, cookie_list):
        claim_url = "https://signup-backend.billions.network/claim-daily-reward"
        me_url = "https://signup-backend.billions.network/me"
        promo_code = self.promo_code_entry.get().strip()

        success, fail = 0, 0

        for idx, cookie_str in enumerate(cookie_list, 1):
            if not self.is_running:
                break

            self.log(f"🍪 正在处理账号 #{idx}")

            try:
                cookies = {
                    kv.split("=")[0]: "=".join(kv.split("=")[1:])
                    for kv in cookie_str.split("; ")
                }
            except Exception as e:
                self.log(f"❌ Cookie 解析失败 #{idx}：{str(e)}")
                fail += 1
                continue

            user_agent = random.choice(self.user_agents)

            headers = {
                "User-Agent": user_agent,
                "Accept": "application/json",
                "Origin": "https://signup.billions.network",
                "Referer": "https://signup.billions.network/"
            }

            proxies = self.get_next_proxy() if self.use_proxy.get() else None

            try:
                # 1. 查询签到前积分
                power_before = self.get_power(me_url, headers, cookies, proxies)
                self.log(f"👀 账号 #{idx} 签到前积分：{power_before}")

                # 2. 签到请求
                res = requests.post(claim_url, headers=headers, cookies=cookies, timeout=10, proxies=proxies)

                if res.status_code == 200:
                    # 3. 查询签到后积分
                    power_after = self.get_power(me_url, headers, cookies, proxies)
                    self.log(f"✅ 账号 #{idx} 签到成功，签到后积分：{power_after}")
                    success += 1

                    # 4. 兑换码处理
                    if promo_code:
                        redeemed = self.redeem_promo_code(promo_code, headers, cookies, proxies)
                        if redeemed:
                            self.log(f"🎁 账号 #{idx} 成功兑换邀请码奖励：{promo_code}")
                        else:
                            self.log(f"⚠️ 账号 #{idx} 兑换邀请码失败或已兑换：{promo_code}")
                else:
                    self.log(f"❌ 账号 #{idx} 签到失败: 状态码 {res.status_code} 代理: {'无' if not proxies else proxies['http']}")
                    fail += 1
            except Exception as e:
                self.log(f"❌ 网络异常 #{idx}: {str(e)} 代理: {'无' if not proxies else proxies['http']}")
                fail += 1

            time.sleep(2)

        self.log(f"🎉 批量任务完成！成功 {success} 个，失败 {fail} 个")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_running = False

    def redeem_promo_code(self, code, headers, cookies, proxies=None):
        url = "https://signup-backend.billions.network/promocode/redeem"
        try:
            res = requests.post(
                url,
                headers={**headers, "Content-Type": "application/json"},
                cookies=cookies,
                json={"code": code},
                timeout=10,
                proxies=proxies
            )
            return res.status_code == 200
        except Exception:
            return False

    def get_power(self, me_url, headers, cookies, proxies=None):
        try:
            res = requests.get(me_url, headers=headers, cookies=cookies, timeout=10, proxies=proxies)
            if res.status_code == 200:
                data = res.json()
                return data.get("power", "未知")
            else:
                return "未知"
        except Exception:
            return "未知"

    def on_close(self):
        self.is_running = False
        self.master.deiconify()
        self.destroy()


# === WalletCheckInGUI ===
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import datetime
import random
import time
import threading

API_URL = "https://app-prismax-backend-1053158761087.us-west2.run.app/api/daily-login-points"
DELAY_BETWEEN_WALLETS = 5  # 秒

class WalletCheckInGUI(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("💼 PrismaX 钱包每日签到工具")
        self.geometry("800x600")
        self.resizable(False, False)

        self.is_running = False

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)"
        ]

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        ttk.Label(self, text="💼 PrismaX 钱包每日签到", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)

        frame = ttk.LabelFrame(self, text="🧾 多个钱包地址（每行一个）")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.address_text = scrolledtext.ScrolledText(frame, height=10, font=("Consolas", 10))
        self.address_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 控制按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        self.start_btn = ttk.Button(btn_frame, text="🚀 开始签到", command=self.start)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ttk.Button(btn_frame, text="⏹️ 停止", state=tk.DISABLED, command=self.stop)
        self.stop_btn.pack(side="left", padx=10)

        # 日志输出框
        log_frame = ttk.LabelFrame(self, text="📋 日志输出")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 10),
                                                  bg="#1e1e1e", fg="white", insertbackground="white")
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, msg):
        """添加日志信息"""
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.log_area.insert(tk.END, f"{timestamp} {msg}\n")
        self.log_area.see(tk.END)
        self.update_idletasks()

    def start(self):
        """开始签到任务"""
        addresses_input = self.address_text.get("1.0", tk.END).strip()
        if not addresses_input:
            messagebox.showwarning("输入缺失", "请输入至少一个钱包地址！")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("🚀 开始批量签到任务...")

        addresses = [line.strip() for line in addresses_input.splitlines() if line.strip()]
        threading.Thread(target=self.claim_all, args=(addresses,), daemon=True).start()

    def stop(self):
        """停止任务"""
        self.is_running = False
        self.log("🛑 已请求停止任务...")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def claim_all(self, addresses):
        """批量执行签到请求"""
        success, fail = 0, 0

        for idx, address in enumerate(addresses, 1):
            if not self.is_running:
                break

            self.log(f"🔑 正在处理地址 #{idx}: {address}")

            headers = {
                "Content-Type": "application/json",
                "User-Agent": random.choice(self.user_agents)
            }

            payload = {
                "wallet_address": address,
                "user_local_date": datetime.date.today().strftime("%Y-%m-%d")
            }

            try:
                resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        detail = data.get("data", {})
                        today = detail.get("points_awarded_today", "N/A")
                        total = detail.get("total_points", "N/A")
                        self.log(f"✅ 签到成功 - 地址: {address} | 今日获得: {today} | 总积分: {total}")
                        success += 1
                    else:
                        self.log(f"❌ 签到失败 - 地址: {address} | 响应: {data.get('message', '无消息')}")
                        fail += 1
                else:
                    self.log(f"❌ HTTP错误 - 地址: {address} | 状态码: {resp.status_code}")
                    fail += 1
            except Exception as e:
                self.log(f"❌ 网络异常 - 地址: {address} | 错误: {e}")
                fail += 1

            # 等待
            if self.is_running and idx < len(addresses):
                time.sleep(DELAY_BETWEEN_WALLETS)

        self.log(f"🎉 批量签到完成！成功: {success}，失败: {fail}")
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def on_close(self):
        """关闭窗口前处理"""
        self.is_running = False
        self.master.deiconify()
        self.destroy()

# === PointClaimGUI (Warden Protocol自动工具) ===


# === Main Application Window ===
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工具箱 - 请选择功能")
        self.geometry("400x280")
        self.resizable(False, False)

        label = ttk.Label(self, text="请选择一个工具启动", font=("Microsoft YaHei", 14, "bold"))
        label.pack(pady=20)

        btn_billions = ttk.Button(self, text="💰 Billions 每日签到工具", width=30,
                                  command=self.open_billions)
        btn_billions.pack(pady=5)

        btn_prismax = ttk.Button(self, text="💼 PrismaX 钱包每日签到工具", width=30,
                                 command=self.open_prismax)
        btn_prismax.pack(pady=5)

        btn_warden = ttk.Button(self, text="🎯 Warden Protocol自动工具", width=30,
                                 command=self.open_warden)
        btn_warden.pack(pady=5)

        author_label = tk.Label(self, text="作者: @Pengchenop", fg="blue", cursor="hand2",
                                font=("Microsoft YaHei", 10, "underline"))
        author_label.pack(pady=15)
        author_label.bind("<Button-1>", lambda e: self.open_author_link())
        self.after(1000, lambda: webbrowser.open("https://x.com/Pengchenop"))

    def open_billions(self):
        self.withdraw()
        BillionsClaimGUI(self)

    def open_prismax(self):
        self.withdraw()
        WalletCheckInGUI(self)

    def open_warden(self):
        messagebox.showinfo("提示", "🎯 Warden Protocol 自动工具尚在开发中，敬请期待！")

    def open_author_link(self):
        try:
            webbrowser.open("https://x.com/Pengchenop")
        except Exception:
            messagebox.showinfo("提示", "请手动访问作者主页: https://x.com/Pengchenop")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
