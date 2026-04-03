import tkinter as tk
from tkinter import ttk, messagebox
import requests
from aip import AipSpeech

# ===================== 【合并后新应用的密钥】 =====================
# 请替换为你新创建应用的真实信息（从应用列表复制）
APP_ID = '122709483'
API_KEY = 'n0L3eKW6c3M6Efz9DNEBsWFM'
SECRET_KEY = 'k7GoY8hkamOaIFpYCGDSFwiRU71eWACb'
# ==================================================================

# 1. 获取百度智能云access_token（统一鉴权，翻译+语音共用）
def get_access_token():
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        if 'access_token' in result:
            return result['access_token']
        else:
            messagebox.showerror("错误", f"获取授权失败：{result.get('error_msg', '未知错误')}")
            return None
    except Exception as e:
        messagebox.showerror("异常", f"网络请求失败：{str(e)}")
        return None

# 2. 机器翻译核心函数（文本翻译-通用版）
def translate_text():
    # 获取输入文本
    input_text = entry_input.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("提示", "请输入要翻译的内容")
        return

    # 获取access_token
    access_token = get_access_token()
    if not access_token:
        return

    # 自动判断语种（中文→英文，英文→中文）
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in input_text)
    from_lang = 'zh' if has_chinese else 'en'
    to_lang = 'en' if has_chinese else 'zh'

    # 调用文本翻译-通用版API
    url = f"https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token={access_token}"
    data = {
        'q': input_text,
        'from': from_lang,
        'to': to_lang
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()

        # 处理返回结果
        if 'result' in result and 'trans_result' in result['result']:
            translated_text = result['result']['trans_result'][0]['dst']
            entry_result.delete("1.0", tk.END)
            entry_result.insert("1.0", translated_text)
        else:
            # 打印完整错误信息，方便排查
            print("接口返回错误：", result)
            error_msg = result.get('error_msg', '未知错误')
            messagebox.showerror("错误", f"翻译失败：{error_msg}")
    except Exception as e:
        messagebox.showerror("异常", f"请求失败：{str(e)}")

# 3. 语音合成核心函数（短文本在线合成，朗读翻译结果）
speech_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
def speak_result():
    result_text = entry_result.get("1.0", tk.END).strip()
    if not result_text:
        messagebox.showwarning("提示", "请先完成翻译，再进行语音朗读")
        return

    # 自动适配语种（中文/英文都能正常朗读）
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in result_text)
    lang = 'zh' if has_chinese else 'en'

    # 调用短文本在线合成API
    audio_result = speech_client.synthesis(
        result_text,
        lang,
        1,
        {
            'vol': 5,   # 音量（0-15，默认5）
            'spd': 5,   # 语速（0-15，默认5）
            'pit': 5,   # 音调（0-15，默认5）
            'per': 0    # 发音人：0女声，1男声，3情感女声，4情感男声
        }
    )

    # 保存音频文件
    if not isinstance(audio_result, dict):
        with open("translation_voice.mp3", "wb") as f:
            f.write(audio_result)
        messagebox.showinfo("成功", "语音已保存为 translation_voice.mp3，可直接播放")
    else:
        messagebox.showerror("失败", f"语音合成错误：{audio_result}")

# ===================== GUI 界面（美化版，直接运行） =====================
if __name__ == '__main__':
    win = tk.Tk()
    win.title("中英互译 + AI语音朗读工具（合并应用版）")
    win.geometry("700x420")
    win.resizable(False, False)

    # 配置按钮样式
    style = ttk.Style()
    style.configure("TButton", font=("微软雅黑", 11), padding=6)

    # 输入区域
    tk.Label(win, text="输入内容（中文/英文）", font=("微软雅黑", 12)).place(x=30, y=15)
    entry_input = tk.Text(win, width=80, height=6, font=("微软雅黑", 11), wrap=tk.WORD)
    entry_input.place(x=30, y=50)

    # 翻译按钮
    btn_trans = ttk.Button(win, text="翻译", command=translate_text, width=12)
    btn_trans.place(x=300, y=170)

    # 结果区域
    tk.Label(win, text="翻译结果", font=("微软雅黑", 12)).place(x=30, y=210)
    entry_result = tk.Text(win, width=80, height=6, font=("微软雅黑", 11), wrap=tk.WORD)
    entry_result.place(x=30, y=240)

    # 朗读按钮
    btn_speak = ttk.Button(win, text="语音朗读", command=speak_result, width=12)
    btn_speak.place(x=300, y=350)

    win.mainloop()