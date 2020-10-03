# Master for prt on python

Minimal toolset for bulid PC application as [prt](https://github.com/llunohodl/prt) master 

### Requirements 

1. Python 3.x
2. [pyserial](https://pypi.org/project/pyserial/)

### Application example

1. Connect modules
```
from Protocol import Protocol
from SerThread import SerThread
from PDU import PDU
```
2. Create command set
```
class BusCmd:
    PRT_CMD1 = 0
    PRT_CMD2 = 1
    PRT_CMD3 = 2

    codes = [0xAA,0xBB,0xCC]
    
address = 0xAA
```
3. Startup serial port
```
serThread = SerThread('COM1',250000)              # Connect to COM1 with 250kBit/s speed 
serThread.start()
if serThread.running:
    protocol = Protocol(serial,BusCmd.codes)  # ini protocol with command codes 0xAA,0xBB,0xCC       

```
4. Process command with response
```
ret = protocol.cmd_process(PDU(address, BusCmd.PRT_CMD1), 0.3) #send PRT_CMD1 without data and wait response 0.3 sec
if ret is not None: #response received
  print(ret.data) #print recived data

```
5. Process command without  response
```
protocol.send(PDU(address,BusCmd.PRT_CMD1,[0x01,0x02,0x03])) #send PRT_CMD1 with data [0x01,0x02,0x03]
```
