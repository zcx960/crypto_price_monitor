# 加密货币价格监控器

这是一个简单的加密货币价格监控工具，可以在系统托盘显示实时价格和涨跌幅。

## 功能特点

- 在系统托盘显示选定加密货币的实时涨跌幅
- 鼠标悬停显示详细价格信息（当前价、24小时高低点等）
- 支持自定义监控的交易对
- 支持搜索和选择任意 Binance 上的 USDT 交易对
- 价格每10秒自动更新

## 安装要求

- Python 3.7+
- 依赖包（见 requirements.txt）

## 使用说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python src/crypto_price_monitor.py
```

3. 使用方法：
   - 程序启动后会在系统托盘显示图标
   - 右键点击图标可以选择"修改币种"或"退出"
   - 在修改币种界面可以搜索和选择想要监控的交易对

## 注意事项

- 程序使用 Binance 公开 API，不需要 API Key
- 建议使用稳定的网络连接以确保价格更新正常

## 依赖项

- Python 3.6+
- pystray
- Pillow
- ccxt
- tkinter (Python标准库)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 