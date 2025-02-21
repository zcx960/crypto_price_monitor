import pystray
from PIL import Image, ImageDraw, ImageFont
import ccxt
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class CryptoPriceMonitor:
    def __init__(self):
        # 初始化交易所API
        self.exchange = ccxt.binance()
        self.symbol = 'NEIRO/USDT'  # 默认币种
        self.current_price = '0'
        self.price_info = "等待更新..."
        self.available_symbols = []  # 存储可用币种列表
        
        # 创建系统托盘图标
        self.icon = self.create_icon()
        self.tray = pystray.Icon(
            "crypto_price",
            self.icon,
            self.price_info,  # 初始提示文本
            menu=self.create_menu()
        )
        
    def create_icon(self, size=(64, 64)):
        # 创建一个空白图片
        image = Image.new('RGB', size, color='black')
        draw = ImageDraw.Draw(image)
        try:
            # 尝试加载微软雅黑字体
            font = ImageFont.truetype("msyh.ttc", 36)  # 调整字体大小以更好地显示
        except:
            # 如果找不到，使用默认字体
            font = ImageFont.load_default()
            
        # 获取涨跌幅
        try:
            percentage = float(self.current_price)
            # 根据涨跌选择颜色
            color = 'red' if percentage >= 0 else 'green'
            # 格式化显示文本
            display_text = f"{'+' if percentage >= 0 else ''}{percentage:.1f}%"
        except:
            color = 'white'
            display_text = "0%"
            
        # 获取文本大小
        text_bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算文本居中位置
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
            
        # 绘制涨跌幅文本
        draw.text((x, y), display_text, font=font, fill=color)
        return image
        
    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("修改币种", lambda: threading.Thread(target=self.show_symbol_dialog, daemon=True).start()),
            pystray.MenuItem("退出", lambda: self.tray.stop())
        )
        
    def get_dynamic_precision(self, price):
        """根据价格动态调整小数点位数"""
        if price >= 1000:  # 大于1000的价格
            return 2
        elif price >= 100:  # 100-1000的价格
            return 3
        elif price >= 10:   # 10-100的价格
            return 4
        elif price >= 1:    # 1-10的价格
            return 5
        elif price >= 0.1:  # 0.1-1的价格
            return 6
        elif price >= 0.01: # 0.01-0.1的价格
            return 7
        else:              # 小于0.01的价格
            return 8

    def update_price(self):
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            self.current_price = f"{ticker['percentage']}"  # 存储涨跌幅
            
            # 获取当前价格并确定小数点位数
            current_price = ticker['last']
            precision = self.get_dynamic_precision(current_price)
            
            # 格式化详细价格信息
            update_time = datetime.fromtimestamp(ticker['timestamp']/1000).strftime('%H:%M:%S')
            self.price_info = (
                f"{self.symbol} 实时价格\n"
                f"当前价: {current_price:.{precision}f} USDT\n"
                f"24h高: {ticker['high']:.{precision}f} USDT\n"
                f"24h低: {ticker['low']:.{precision}f} USDT\n"
                f"24h涨跌: {ticker['percentage']:.2f}%\n"
                f"更新时间: {update_time}"
            )
            
            # 更新图标和提示文本
            self.tray.icon = self.create_icon()
            self.tray.title = self.price_info
            
        except Exception as e:
            print(f"获取价格出错: {e}")
            self.current_price = "0"  # 错误时显示0%
            self.price_info = f"获取价格出错: {e}"
            self.tray.title = self.price_info
            
    def price_update_loop(self):
        while True:
            self.update_price()
            time.sleep(10)  # 每10秒更新一次价格
            
    def run(self):
        # 启动价格更新线程
        update_thread = threading.Thread(target=self.price_update_loop, daemon=True)
        update_thread.start()
        
        # 运行系统托盘图标
        self.tray.run()

    def get_available_symbols(self):
        try:
            # 获取所有市场信息
            markets = self.exchange.load_markets()
            # 过滤出USDT交易对
            usdt_symbols = [symbol for symbol in markets.keys() if symbol.endswith('/USDT')]
            # 按字母顺序排序
            return sorted(usdt_symbols)
        except Exception as e:
            print(f"获取币种列表失败: {e}")
            return []

    def show_symbol_dialog(self):
        # 创建一个新的顶级窗口
        dialog = tk.Tk()
        dialog.title("选择币种")
        dialog.geometry("400x200")
        
        # 添加说明标签
        label = ttk.Label(dialog, text="请选择要监控的币种:")
        label.pack(pady=10)
        
        # 创建一个Frame来包含下拉框和刷新按钮
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.X, padx=20)
        
        # 创建下拉框
        combo = ttk.Combobox(frame, width=30)
        combo.pack(side=tk.LEFT, padx=(0, 10))
        
        def update_symbols():
            current_selection = combo.get()
            symbols = self.get_available_symbols()
            if symbols:
                combo['values'] = symbols
                # 如果之前选择的币种在列表中，保持选择
                if current_selection in symbols:
                    combo.set(current_selection)
                else:
                    combo.set(self.symbol)  # 默认显示当前币种
            else:
                messagebox.showerror("错误", "获取币种列表失败")
        
        # 添加刷新按钮
        refresh_btn = ttk.Button(frame, text="刷新列表", command=update_symbols)
        refresh_btn.pack(side=tk.LEFT)
        
        def on_submit():
            new_symbol = combo.get()
            if new_symbol:
                try:
                    # 验证币种是否存在
                    self.exchange.fetch_ticker(new_symbol)
                    self.symbol = new_symbol
                    self.update_price()  # 立即更新价格
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("错误", f"币种无效: {e}")
            
        def on_cancel():
            dialog.destroy()
        
        # 添加确定和取消按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        submit_btn = ttk.Button(button_frame, text="确定", command=on_submit)
        submit_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_btn.pack(side=tk.LEFT)
        
        # 初始化币种列表
        update_symbols()
        
        # 设置窗口为模态
        dialog.transient()
        dialog.grab_set()
        dialog.focus_set()
        
        # 居中显示窗口
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # 添加搜索功能
        def on_search(*args):
            search_text = combo.get().upper()
            all_symbols = combo['values']
            if search_text and all_symbols:
                filtered = [s for s in all_symbols if search_text in s.upper()]
                combo['values'] = filtered
            else:
                update_symbols()
                
        combo.bind('<KeyRelease>', on_search)
        
        dialog.mainloop()

if __name__ == "__main__":
    monitor = CryptoPriceMonitor()
    monitor.run() 