# NGA_ListenUpdate
监听NGA帖子楼层更新并采用server酱发送通知

## 功能列表
1. 监听帖子: 支持添加并监听任意数量的NGA帖子(上限依照运行性能而定);
2. 循环运行: 运行周期可自行在云函数或者服务器触发器设定;
3. 软件通知: 监听到帖子有新回复可通过sc3酱发送通知到手机客户端(目前仅支持该方式),如无更新则不会通知;
4. 日志记录: 可在`log.txt`中查看每一次运行更新的详情.

## 使用说明书
1. 复制`config.json.default`文件并重命名为`config.json`,按照说明填写对应的内容,完成后删除所有`//中文注释`,否则运行会出错;
2. 运行`main.py`一次,生成`listen_log.json`文件和`log.txt`文件;
3. 设置周期运行`main.py`文件,周期越短,监听的频率越高.


### `config.json`事项说明书
1. listen_tid: `必须`,监听的帖子列表,要求为若干个纯数字;
2. isLog: `必须`,日志开关,必须是`true`或者`false`,true表明开启log.txt的记录每一次运行的详情,false表明不记录;
3. sendkey: `非必须`,sc3通知的密钥,请通过[Server酱3](https://sc3.ft07.com/)官网获取通知密钥,若为空则无法发送APP通知;
4. cookies: `必须`,NGA论坛的账号cookies,请打开[NGA玩家社区](https://bbs.nga.cn/),`按下F12`->`应用`->`Cookie`,找到对应值填入.