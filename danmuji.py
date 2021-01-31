import asyncio
import zlib
import json
import requests
import time
from aiowebsocket.converses import AioWebSocket
import re
import socket
import threading

class Gift():
        
    def __init__(self, roomID):
        # get full roomID
        self.roomID = roomID
        if len(self.roomID) <= 3:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
            html = requests.get('https://live.bilibili.com/' + self.roomID, headers=headers).text
            for line in html.split('\n'):
                if '"roomid":' in line:
                    self.roomID = line.split('"roomid":')[1].split(',')[0]
        
        # data
        self.danmuList = []     # [(name1, pos1), (name2, pos2), ...]
        
        # thread lock
        self.lock = threading.Lock()

        
    async def startup(self):
        url = r'wss://broadcastlv.chat.bilibili.com:2245/sub'
        data_raw = '000000{headerLen}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
        data_raw = data_raw.format(headerLen=hex(27 + len(self.roomID))[2:],
                                   roomid=''.join(map(lambda x: hex(ord(x))[2:], list(self.roomID))))
        async with AioWebSocket(url) as aws:
            converse = aws.manipulator
            await converse.send(bytes.fromhex(data_raw))
            tasks = [self.recvDanmu(converse), self.sendHeartBeat(converse)]
            await asyncio.wait(tasks)

    async def sendHeartBeat(self, websocket):
        hb = '00000010001000010000000200000001'
        while True:
            await asyncio.sleep(30)
            await websocket.send(bytes.fromhex(hb))

    async def recvDanmu(self, websocket):
        while True:
            recv_text = await websocket.receive()
            self.decodeDanmu(recv_text)
            
    def decodeDanmu(self, data):
        print('decodeDanmu')
        packetLen = int(data[:4].hex(), 16)
        ver = int(data[6:8].hex(), 16)
        op = int(data[8:12].hex(), 16)

        if len(data) > packetLen:
            self.decodeDanmu(data[packetLen:])
            data = data[:packetLen]

        if ver == 2:
            data = zlib.decompress(data[16:])
            self.decodeDanmu(data)
            return

        if ver == 1:
            if op == 3:
                # print('[RENQI]  {}'.format(int(data[16:].hex(),16)))
                pass
            return

        if op == 5:
            try:
                jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
                if jd['cmd'] == 'SEND_GIFT':
                    d = jd['data']
                    giftInfo = (d['uname'], d['num'], d['giftName'])
                    #print(giftInfo)
                elif jd['cmd'] == 'COMBO_SEND':
                    d = jd['data']
                    giftInfo = (d['uname'], d['batch_combo_num'], d['gift_name'])
                    #print(giftInfo)
                elif jd['cmd'] == 'GUARD_BUY':
                    d = jd['data']
                    giftInfo = (d['username'], '1', 'captain')
                    #print(giftInfo)
                elif jd['cmd'] == 'DANMU_MSG':
                    info = jd['info'][2][1], jd['info'][1]
                    print(info)
                    m = re.match('([a-z]|[A-Z])(\d\d|\d)', info[1])
                    if m != None:
                        self.lock.acquire()
                        self.danmuList.append((info[0], (ord(m.group(1).lower())-ord('a'), int(m.group(2)))))
                        self.lock.release()
                        print('decode:', m.group())
                        
                        
            except Exception as e:
                print(e)
    
    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
    
    def run(self):
        loop = asyncio.new_event_loop()
        t = threading.Thread(target = self.startLoop, args = (loop,))
        t.setDaemon(True)
        t.start()
        asyncio.run_coroutine_threadsafe(self.startup(), loop)
            
            
         