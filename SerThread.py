import sys
import glob
import serial
import time

from PyQt5 import QtCore
try:
    import Queue
except:
    import queue as Queue

class SerThread(QtCore.QThread):
    """
    Thread to handle incoming &amp; outgoing app_serial data
    """

    def __init__(self, portname, baudrate):  # Initialise with app_serial port details
        QtCore.QThread.__init__(self)
        self.portname, self.baudrate = portname, baudrate
        self.txq = Queue.Queue()
        self.rxq = Queue.Queue()
        self.running = True
        self.ser = None

    @staticmethod
    def serial_port_list():
        """
        Lists app_serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the app_serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def ser_put(self, s):
        """
        Write data to app_serial port
        :param s: data to port
        :return:
        """
        self.txq.put(s)

    def ser_get(self):  # Write incoming app_serial data to screen
        """
        Read data from app_serial port
        :return: number of bytes
        """
        if not self.rxq.empty():
            return self.rxq.get_nowait()  # If Rx data in queue, write to app_serial port
        return []

    def ser_runing(self):
        return self.running

    def run(self):  # Run app_serial reader thread
        try:
            self.ser = serial.Serial(self.portname, self.baudrate, timeout=0.001)
            time.sleep(0.001)
            self.ser.flushInput()
        except:
            self.ser = None
        if not self.ser:
            print("ser Can't open port")
            self.running = False
        else:
            print("ser "+self.portname + " opened!")
        while self.running:
            try:
                s = self.ser.read_all() #read(self.ser.in_waiting or 1)
                if s:  # Get data from app_serial port
                    self.rxq.put(s)
                    if len(s) < 10:
                        print("Rx< " + SerThread.bytes_str(s))
                    else:
                        print("Rx< " + SerThread.bytes_str(s[:10]) + " ...")
                if not self.txq.empty():
                    txd = self.txq.get_nowait()  # If Tx data in queue, write to app_serial port
                    self.ser.write(txd)
                    if len(txd) < 10:
                        print("Tx> " + SerThread.bytes_str(txd))
                    else:
                        print("Tx> " + SerThread.bytes_str(txd[:10]) + " ...")
            except:
                self.ser = None
                self.running = False
        if self.ser:  # Close app_serial port when thread finished
            self.ser.close()
            print("ser " + self.portname + " closed!")
            self.ser = None

    @staticmethod
    def str_bytes(s):
        """
        Convert a string to bytes
        :param s: string
        :return: binary data
        """
        return s.encode('latin-1')

    @staticmethod
    def bytes_str(d):
        """
        Convert bytes to string
        :param d: binary data
        :return: string
        """
        return d if type(d) is str else " ".join([format(b, "02X") for b in d])


