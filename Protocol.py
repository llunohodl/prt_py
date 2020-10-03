import time
import copy
from PDU import PDU

class Protocol:
    """
    Protocol class, build commands and analyse response from device
    """

    def __init__(self, serial, code_set):
        super().__init__()
        self.state = "addr"
        self.serial = serial
        self.rxPDU = PDU()
        self.code_set = code_set

    def cmd_process(self, txpdu, to) -> object:
        """
        Send command and get response from device
        :param txpdu: tx request Protocol.PDU type
        :param to: timeout in seconds
        :return: response pdu or None (if to elapsed)
        """
        if to == 0:
            to = 0.1
        step = to / 5
        if step > 0.1:
            step = 0.1

        self.send(txpdu)
        while to > 0:
            if self.parse() and self.rxPDU.code == txpdu.code:
                return copy.deepcopy(self.rxPDU)
            time.sleep(step)
            to = to - step
        print("Request TO elapsed")
        return None

    def send(self, pdu):
        """
        Send PDU
        :param pdu: tx request Protocol.PDU type
        """
        tx = []
        tx.append(pdu.addr)
        tx.append(self.code_set[pdu.code])
        tx.append(pdu.len)
        sum = ((tx[0] + tx[1] + tx[2]) ^ 0x5A) & 0xFF
        tx.append(sum)
        if pdu.len != 0:
            sum = 0
            for dataind in range(pdu.len):
                tx.append(pdu.data[dataind])
                sum = sum + pdu.data[dataind]
            sum = sum ^ 0xA5
            sum = sum & 0xFF
            tx.append(sum)
        self.state = "addr"
        self.serial.ser_put(tx)

    def parse(self):
        """
        Seek valid commands in input stream
        :return: True if correct pdu stored in self.rxPDU
        """
        s=self.serial.ser_get()
        if len(s) == 0:
            return False
        for byte in s:
            if self.state == "addr":  # get address
                self.rxPDU.addr = byte
                self.rxPDU.sum = byte
                self.rxPDU.data = []
                self.state = "code"
                # print("addr " + str(hex(byte)))
                continue
            if self.state == "code":  # decode command code
                for coden in range(len(self.code_set)):
                    if byte == self.code_set[coden]:
                        self.state = "len"
                        self.rxPDU.code = coden
                        self.rxPDU.sum = self.rxPDU.sum + byte
                        # print("code " + str(hex(byte)))
                        continue
                continue
            if self.state == "len":  # get data len
                self.rxPDU.len = byte
                self.rxPDU.sum = self.rxPDU.sum + byte
                self.state = "csumm"
                continue
            if self.state == "csumm":  # check command
                self.rxPDU.sum = self.rxPDU.sum ^ 0x5A
                self.rxPDU.sum = self.rxPDU.sum & 0xFF
                if self.rxPDU.sum == byte:
                    # print("prt found cmd: " + str(self.rxPDU.code) + " len = " + str(self.rxPDU.len))
                    if self.rxPDU.len == 0:
                        return True
                    else:
                        self.rxPDU.sum = 0
                        self.state = "data"
                        self.read_len = self.rxPDU.len
                else:
                    self.state = "addr"
                continue
            if self.state == "data":  # get data
                self.rxPDU.data.append(byte)
                self.rxPDU.sum = self.rxPDU.sum + byte
                self.read_len = self.read_len - 1
                if self.read_len == 0:
                    self.state = "dsum"
                continue
            if self.state == "dsum":  # check data
                self.rxPDU.sum = self.rxPDU.sum ^ 0xA5
                self.rxPDU.sum = self.rxPDU.sum & 0xFF
                if self.rxPDU.sum == byte:
                    # print("prt found data for: " + str(self.rxPDU.code))
                    return True
                # else:
                    # print("summ error: " + str(hex(byte)) + " must be " + str(hex(self.rxPDU.sum)))
                self.state = "addr"
                continue
        return False



