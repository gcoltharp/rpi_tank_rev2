
# rpi_tank_rev2
Based on the project "A Robot called Bob" http://forum.piborg.org/bot-of-bits

The project assumes you have a working bluetooth PS3 controller connected to your Raspberry Pi using the six axis and bluez library. I purchased a 3rd party cheapee controller and paid the price. I had to tweak the bluez library to get it to work with it. If you have a legitimate Ps3 controller, your life will be a lot easier.

It also utilizez the Thunderborg motor controller hat. I used cheap Tamiya tank parts to build my tank and 3D printed my chassis. For a basic tank, you would just mount the Pi and batter on the wood plank that comes with the Tamiya chassis. The voltages for the Thunderborg are scalable, so you can port this to just about any size RC tank implementation.

My build is described below.

Parts:
  Raspberry Pi 3
  Raspberry Pi Camera with Infrared attachments (night vision) https://www.amazon.com/Makerfocus-Raspberry-Camera-Adjustable-Focus-Raspberry-pi/dp/B06XYDCN5N/ref=sr_1_6?s=electronics&ie=UTF8&qid=1518280354&sr=1-6&keywords=raspberry+pi+camera
  PiBorg Thunderborg motor conrol hat https://www.piborg.org/motor-control-1135/thunderborg
  PS3 DualShock Wireless Controller Clone 
    Don't get the clone...get a legitimate Sony controller and you won't have as many problems pairing.
  Tamiya tank body https://www.amazon.com/gp/product/B002DR3H5S/ref=oh_aui_search_detailpage?ie=UTF8&psc=1
    This tank body comes with a single drive motor, which I did not use but the parts could be useful.
  Tamiya dual drive motor https://www.amazon.com/gp/product/B001Q13BIU/ref=oh_aui_search_detailpage?ie=UTF8&psc=1
    This is the independet drive gear box. It can be geared for four different gear combinations. I went with the low speed/high torque       build.
  3S 1000 LiPo battery
  3D printed body parts for the tub, top, cap and camera mount
    STLs in the file list
    
  The forum post above has most of the details on getting things talking but the point of this git is that I am not using the majority of their python code as I wanted tank controls not an up/down left/right control.
  
    

