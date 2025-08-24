import requests,re,json,time
from bs4 import BeautifulSoup
from serverchan_sdk import sc_send

# 全局变量:读取config.json才能获取
listen_tid = []
listen_log = []
sendkey = ""
isLog = True
cookies = {}

# 全局变量:默认值，请勿修改
send_text = ""
send_check = 0
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X TESTLXC) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Referer": "https://bbs.nga.cn/",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Host": "bbs.nga.cn"
}

# ========== 通用函数:获取网页数据 ==========
def get_page(url):
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"请求失败: {e}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# ========== 功能函数1:获取帖子最后一页页码 ========== 
def get_lastpage(tid):
    soup = get_page("https://bbs.nga.cn/read.php?tid=" + str(tid))
    script_tag = soup.select_one('#pagebtop script')
    if script_tag and script_tag.string:
        match = re.search(r'__PAGE\s*=\s*{.*?1:\s*(\d+),', script_tag.string)
        if match:
            return int(match.group(1))
    # print(f"无法获取帖子 {tid} 的最后一页页码，可能是页面结构发生变化或请求失败。")
    return 1
    # soup = get_page("https://bbs.nga.cn/read.php?tid="+str(tid))
    # return int(re.search(r'__PAGE\s*=\s*{.*?1:\s*(\d+),', soup.select_one('#pagebtop script').string).group(1))
    
# ========== 功能函数2:获取当前页的最新一层楼 ==========
def get_lastfloornum(tid,page):
    soup = get_page("https://bbs.nga.cn/read.php?tid="+str(tid)+"&page="+str(page))
    floors = soup.select('.postrow td.c1 span.posterinfo')
    return int(floors[-1]['id'].split('posterinfo')[-1])

# ========== 功能函数3:读取配置文件 ==========
def get_config():
    # 修改全局变量
    global listen_tid,sendkey,cookies,isLog
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        listen_tid = data["listen_tid"]
        sendkey = data["sendkey"]
        cookies = data["cookies"]
        isLog = data["isLog"]
    except Exception as e:
        print(f"变量不存在或者其他错误: {e}")
        return []
    
# ========== 功能函数4:读取监听记录 ==========
def get_listen_log():
    global listen_log
    try:
        with open("listen_log.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            listen_log = data["listen_log"]
    except Exception as e:
        print(f"读取错误: {e}")
        return []
            
# ========== 功能函数5:发送通知到sc3 ==========
def send_notification(info):
    try:
        if send_check != 0 and sendkey:
            sc_send(sendkey, "帖子回复更新提醒",info,{"tags": "NGA监测"})
    except Exception as e:
        print(f"发送出错: {e}")
        
# ========== 功能函数6:写入日志 ==========
def write_log():
    if isLog:
        with open("log.txt", 'a') as file:
            file.write("====================\n日志写入时间:"+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n" + re.sub(r'\n+', '\n', send_text) + "====================\n")

# ========== 核心函数:遍历监测并更新listen_log.json ==========
def check_tid():
    new_listen_log =[]
    # 将listen_log转换为tid为键的字典
    log_dict = {item["tid"]: item for item in listen_log}
    # 遍历listen_tid作为基准数组
    for tid in listen_tid:
        if tid in log_dict:
            # 更新log
            new_f = monitor_update(tid, log_dict[tid]["f"])
            new_listen_log.append({"tid": tid,"f": new_f})
        else:
            # 新增log
            new_listen_log.append({"tid": tid, "f": 1})
    
    # 更新new_listen_log到listen_log.json中
    with open('listen_log.json', 'w', encoding='utf-8') as f:
        json.dump({"listen_log":new_listen_log}, f, ensure_ascii=False, indent=4)
    

# ========== 核心函数:监测帖子更新 ==========
def monitor_update(tid,record_floor):
    global send_text,send_check
    last_floor = get_lastfloornum(tid,get_lastpage(tid))
    if last_floor == record_floor:
        send_text = send_text + "帖子TID" + str(tid)+"未更新.\n\n"
    elif last_floor > record_floor:
        send_check += 1
        send_text = send_text + "帖子TID" + str(tid)+"已更新,新增" + str(last_floor - record_floor) + "层楼,最新楼是" + str(last_floor) + ".\n\n"
    elif last_floor < record_floor:
        send_check += 1
        send_text = send_text + "帖子TID" + str(tid)+"记录错误，已重置记录楼数为" + str(last_floor) + ".\n\n"
    return last_floor
    
# ========== 执行入口 ==========
if __name__ == "__main__":
    try:
        get_config()
        get_listen_log()
        check_tid()
        print(send_text)
        # send_notification(send_text)
        write_log()
    except Exception as e:
        print(f"执行出错: {e}")
