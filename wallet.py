from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
import sys
from random import randint

from jsonMaker import JsonPackets
from nooCrypto import NooCrypto

import redis, json, time, os
import pycurl, random
import requests

import threading

class tranCreator(QObject):
    sendPacket = pyqtSignal(str, str, int)
    def __init__(self, slaveNodes:list):
        super().__init__()
        self.slavesNodes = slaveNodes
        self.cryptor = NooCrypto()
        #------------------------------------------------
        self.cryptor.generateKeys()

        self.redis_host = os.getenv("REDIS_PORT_6379_TCP_ADDR") or 'localhost'
        self.redis_port = os.getenv("REDIS_PORT_6379_TCP_PORT") or '6379'
        self.redis = redis.StrictRedis(self.redis_host, self.redis_port, db=1)

        self.secondKeys = []
        self.secondPKeys = []
        self.secondKeys.append("125466fda87a6c88df7222eec063a720958985e39d9e6eff5c76047e68d32c67")
        self.secondPKeys.append("0323f264fd64a684db1e36a2c97b58867e0625f797008206216576fea2114bdbca")

        self.secondKeys.append("a376bdbcca0cda0ed27c7f5a434444276b2379b25f504c3ba9c3f4f52a6a5d1c")
        self.secondPKeys.append("027426df275f98bb0f66bb4f1a92352296be233b115415f709540e8caa80d820f2")
        cryptor = NooCrypto()

        for i in range(1, 100):
            cryptor.generateKeys()
            self.secondKeys.append(cryptor.getPrivateKey())
            self.secondPKeys.append(cryptor.getPublicKey())

        self.url = "http://explorer.vinci.id:5000"
        #self.url = "http://192.168.192.42:5000"

    def sendTransactionMainAV(self):
        cryptor = NooCrypto()
        cryptor.setPrivateKey("125466fda87a6c88df7222eec063a720958985e39d9e6eff5c76047e68d32c67")

        packetAT = JsonPackets.applicantTransaction(cryptor, "127.0.0.1")
        jpacketAT = json.loads(packetAT)

        response = requests.post(self.url + "/wallet/transaction", json=jpacketAT)
        print(response.status_code)

        i = 0
        while (i < 50):
            i += 1
            receiver = "0323f264fd64a684db1e36a2c97b58867e0625f797008206216576fea2114bdbca"
            packetVT = JsonPackets.voteTransaction(cryptor, receiver, randint(1, 10))

            jpacketVT = json.loads(packetVT)
            response = requests.post(self.url + "/wallet/transaction", json=jpacketVT)
            print(response.status_code)

    def sendTransactionMain(self):
        cryptor = NooCrypto()
        cryptor.setPrivateKey("125466fda87a6c88df7222eec063a720958985e39d9e6eff5c76047e68d32c67")

        while (True):
            receiver = random.choice(self.secondPKeys)
            tcount = randint(0, 1) + randint(0,1000)/10000
            packet = JsonPackets.standartTransaction(cryptor, receiver, tcount, "VNC")
            jpacket = json.loads(packet)

            response = requests.post(self.url + "/wallet/transaction", data=packet)
            print (response.status_code)
            time.sleep(0.2)


    def sendTransactionSecond(self):
        cryptor = NooCrypto()
        cryptor.setPrivateKey(random.choice(self.secondKeys))

        while (True):
            receiver = random.choice(self.secondPKeys)
            tcount = randint(0,100)/10000
            packet = JsonPackets.standartTransaction(cryptor, receiver, tcount, "VNC")
            jpacket = json.loads(packet)

            print(packet)
            print(jpacket)

            response = requests.post(self.url + "/wallet/transaction", data=packet)
            print (response.status_code)
            time.sleep(5)

    def smartWallet(self, countOfThreads:int):
        temp = threading.Thread(target=self.sendTransactionMain)
        temp.start()

        # temp2 = threading.Thread(target=self.sendTransactionMainAV)
        # temp2.start()

        for i in range(0, countOfThreads):
            temp = threading.Thread(target=self.sendTransactionSecond)
            temp.start()

    def startFastSendTransactions(self):
        cryptor = NooCrypto()
        cryptor.setPrivateKey("125466fda87a6c88df7222eec063a720958985e39d9e6eff5c76047e68d32c67")
        sender = cryptor.getPublicKey()
        receiver = sender.replace("1", "2")
        while (True):
            tcount = randint(1, 9999) / 10000000
            packet = JsonPackets.standartTransacton2(cryptor, receiver, tcount, "VNC")

            self.redis.zadd("RAW TRANSACTIONS", 1, packet)

        return True

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    #--------------------------------------------
    wallet = tranCreator(['192.168.0.35'])
    wallet.smartWallet(3)

    # netEngine = NetEngine()
    # wallet.sendPacket.connect(netEngine.sendPacketSignal)
    # netEngine.setRemoteAddresses.emit(['192.168.0.35'])
    #--------------------------------------------
    sys.exit(app.exec())