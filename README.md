# pc-components-arduino-tracker-I2C16X2
Small project on arduino, idea is to display usage of PC components like CPU/GPU/RAM on 16x2 I2C display. Project contains code for arduino, and deliver app which is delivering the data from PC. It was created during learning the Arduino environment.

# Arduino code
Arduino code is handling the cycle through three screens that are displaying informations about:

 - CPU (Load & Temp)
 - GPU (Load & Temp)
 - RAM (Max size &  Load)
 

> It's using the address of device 0x27 and it's hardcoded feel free to
> change it (line: 5),

 
Also it's handling communication through the serial port, it's sending the message "init" when the Arduino succesfuly booted and turned on the display. At this step it's also displaying the message on screen: "Waiting for deliver app", it changed to displaying info about components after getting first batch of infromation about them.

Every handled request by arduino is sending the "handled" message, the purpose of it to sync the operations a little, and python deliver application (script) will wait with sending next batch of information untill it will recieve this message.

**Actions**
Actions are the possible requests through the serial port communication that will be handled by arduino code.

 - update - updates the data about the component
 - stop - stop the cycling, and will display the init message again
 - changeInterval - will change the interval after which arduino will change the screen. It must be at least 500ms.
# Deliver app (python script)
It will work only on windows, it's using the Open Hardware Monitor as a dependency that will be gathering the informations about the components. You need to put the file **OpenHardwareMonitorLib.dll** inside deliver-py directory before starting the app. You can download it from https://openhardwaremonitor.org/

Python application is establishing the connection on port provided in .env file on the baud rate also from .env file. You can specify also the interval in the .env file and it will change the time between changing screens. 

You need two dependency to start the app: 

 - pyserial==3.5
 - pythonnet==3.0.2


Application is establishing the connection, and then work in infinite loop getting the infromation about the components and sending the data to arduino, and repeating it after every 'handled' message from Arduino, or any other message but with the additional log that something unexpected happened. 
