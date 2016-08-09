#
# BLE application demo
#
import cb
import ui
from time import sleep

MLDP_SERVICE   = '00035B03-58E6-07DD-021A-08123A000300' 
MLDP_DATA      = '00035B03-58E6-07DD-021A-08123A000301'
MLDP_CONTROL   = '00035B03-58E6-07DD-021A-08123A0003FF'

class MLDPManager (object):
    def __init__(self):
        self.peripheral = None
        self.buffer = ''

    def did_discover_peripheral(self, p):
        if p.name and 'IoTBadge' in p.name and not self.peripheral:
            self.peripheral = p
            print('Connecting to IoT Badge...')
            cb.connect_peripheral(p)

    def did_connect_peripheral(self, p):
        print('Connected:', p.name)
        #print('Discovering services...')
        p.discover_services()

    def did_fail_to_connect_peripheral(self, p, error):
        print('Failed to connect: %s' % (error,))

    def did_disconnect_peripheral(self, p, error):
        print('Disconnected, error: %s' % (error,))
        self.peripheral = None
        v.close()

    def did_discover_services(self, p, error):
        for s in p.services:
            if s.uuid == MLDP_SERVICE:
                #print('Discovered MLDP service, discovering characteristitcs...')
                p.discover_characteristics(s)

    def did_discover_characteristics(self, s, error):
        #print('Did discover characteristics...')
        for c in s.characteristics:
          if '301' in c.uuid:
              #print('found DATA characteristic', c.uuid)
              self.data_char = c
              # Enable notification for MLDP input:
              #print('Enabling MLDP input notifications...')
              self.peripheral.set_notify_value(c, True)
              
    def did_update_value(self, c, error):
        #print('value updated:', c.uuid)
        self.buffer += c.value.decode('ascii')
        #print(c.value)
        if self.buffer[-1] in '\n':
          if self.buffer and self.buffer[0] == '@':
            display(self.buffer[1:])
            self.buffer = ''
            self.send_cmd(b'$')
        
    def did_write_value(self, c, error):
        pass 
        
    def send_cmd(self, cmd):
        if self.peripheral:
          self.peripheral.write_characteristic_value(self.data_char, cmd, True)
        
def display(msg):
   data = msg.rstrip('\n\r').split(',')
   for x in range(0,15,3):
       v['led'+str(int(x/3))].background_color = (float(data[x+1])/16, float(data[x])/16, float(data[x+2])/16, 1.0)
   #print('pitch =', data[15], 'roll = ', data[16])
   v['slider1'].value = float(data[15])/160+.5
   v['slider2'].value = -float(data[16])/160+.5
   #print('temp = ', data[17], 'batt = ', data[18])
   v['Temp'].text = data[17]
   v['Batt'].text = data[18]
   
def button_press(sender):
  if sender.name ==   'button1':
    mngr.send_cmd(b'%')
  elif sender.name == 'button2':
    mngr.send_cmd(b'#')

class BadgeView(ui.View):
  def will_close(self):
    cb.reset()

# main --------------------------------
v=ui.load_view('IoTBadge_searching')
v.present()

mngr = MLDPManager()
cb.set_central_delegate(mngr)
cb.scan_for_peripherals()
while not mngr.peripheral: pass
v.close()

sleep(1)
v=ui.load_view('IoTBadge')
v.background_color = '#05001d'
v.present()
mngr.send_cmd(b'$')
v.wait_modal()
cb.reset()
