"""
Author: James Howe, Bucknell Computer Engineering '23
Description: This libray is for acting as a learning tool for Bucknell's ECEG 201 class, so there are an abundance of comments
Date Created: 4/5/21

<><><><><><><><><><><><><><><><><><><><><><><><><><>

If you have any questions about the code just message me via groupme

<><><><><><><><><><><><><><><><><><><><><><><><><><>
"""

"""
PINS IN USE
>NeoPixel
->board.D5

>Motor
->board.I2C

>ESP
->board.11-13
"""



#I'm importing the libraries that I'll be using for this program

#These 3 are ones that you will Definitly need to download, put the files in the lib folder in your circuit python folder
# the "as ..." syntax just lets me say how I will call these libraries sp for example I could call a function from neoPixelFunctions
# as neoFun.animate_snake() instead of neoPixelFunctions.animate_snake()
import espFunctions as espFun
import neoPixelFunctions as neoFun
import motorFunctions as motorFun


#Other imports that are needed
import board
import time


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

#-----------------

#Define Constant values here, these won't change throughout the program
#Change these for your purposes

#Wifi and Thingspeak stuff
NETWORK_NAME = secrets["ssid"]
NETWORK_PASS = secrets["password"]
THINGSPEAK_CHANNEL = 1221440
THINGSPEAK_API_KEY = secrets['thingspeak_API_token']
I2C = board.I2C()


#NeoPixel settings
NEO_BRIGHTNESS = .3


#Determines whether or not debug messages are printed out
DEBUG = True


#The min and max tempature you should expect in the Maker-E
TEMP_MIN = 40
TEMP_MAX = 90
TEMP_RANGE = [TEMP_MIN,TEMP_MAX]

#The delay between each time it pulls from the thingspeak server and gets new data, in seconds
UPDATE_PERIOD = 40 * 60


#-----------------

#Here I'm doing setup and just doing everything that only needs/should be done once


#Sets the neopixel rings brightness
neoFun.set_brightness(NEO_BRIGHTNESS)
#Tests the NeoPixel, it should animate a purple snake going around ring
#it's not neccasary that you understand the animate_snake() method, but it's commented in neoPixelFunctions
neoFun.animate_snake((100,10,255))

#It should then go green
neoFun.set_ring_color((0,20,0))

#'net_tool' will handle all of the basic function of connecting to wifi and communicating with ThingSpeak
#Calling this, automaticly makes it start connecting to the network you specify here
net_tool = espFun.ESP_Tools(NETWORK_NAME, NETWORK_PASS, THINGSPEAK_CHANNEL, THINGSPEAK_API_KEY)


#'motor_tool' handles all the motor related functions
#Calling this will automaticly make the motor try and find its home(i.e. try to make a full rotation and end up hitting the stop)
motor_tool = motorFun.ECEGMotor(I2C,DEBUG)

#Flash the neoPixel to indicate that startup it done

neoFun.set_ring_color((0,0,0))
time.sleep(.005)
neoFun.set_ring_color((0,20,0))
time.sleep(.005)
neoFun.set_ring_color((0,0,0))






#---------------------------

#This is the format for the loops below, they both follow this basic structure
"""
1.  Goes to Thingspeak and pulls down current Maker-E temp and RH
2.  Updates lights and motor accordingly
3.  Repeat infinitely 1 - 2 infinitely.
"""


#This is a pretty simple way to do the assigment
#It takes in the temp and humidty and then lights up the neopixel according to TEMP_RANGE
#And sets the motor arm to the humdity percent as a percent of a single rotation
def basic_loop():

    #The net_tool.pull_from_field() takes in 1-2 aurguments, the first being the field you want to pull from and the second being the number
    #of results you want to return, by default it will only the most recent entry in the field
    #It returns a list of Strings which are the entries from the field, so you have get the entry from the list and convert it from a string to a float
    current_makerE_temp = float(net_tool.pull_from_field(1)[0])

    if(DEBUG):
        print("Got tempature. temp =", current_makerE_temp)

    #maprange takes in 3 aurguments,
    # a: the original range of s
    # b: the range you want to map s onto
    # s: the value you want to map
    # The function maps s from its original range onto a new one
    # for eg, mapping maprange([0,10],[0,100],5) would return 50
    #In this case we are taking the tempature in the makerE which we assume will be within TEMP_RANGE
    #   and mapping it onto the new range of 0 to 255, the min and max values of a LED RBG value
    mapped_color = neoFun.maprange(TEMP_RANGE, [0,255], current_makerE_temp)
    print(mapped_color)

    #This is setting the value of the Neopixel Ring, its
    #the values are RedGreenBlue, with each going from 0-255
    #Red is set so when the temp is higher its redder
    #and blue is set that when the temp is higher its lower
    neoFun.set_ring_color((mapped_color, 0, (255-mapped_color)))



    #Same as previous pull_from_field() excetpt this time its from field 2, which is for humidity
    current_makerE_humd = float(net_tool.pull_from_field(2)[0])

    if(DEBUG):
        print("Got Humidity. hum =", current_makerE_humd)

    #The motor function takes in a degree(math not tempature) and moves the motor to that degree
    #So we need to convert the humidty which is given as a percentage, into a degree
    #You could also use the maprange function for this
    humd_as_a_degree = ((current_makerE_humd/100)*360)

    #Simply sets the motor arm to the position calculated before
    motor_tool.set_position_degrees(humd_as_a_degree)




#This is another thing that you could do, and I'm just doing this to show off more of the functions so you know whats available to you
#This loop shows how the tempature changes throughout the day by assigning each led an hour of the day
#The humidty sensing stays the same
def complex_loop():

    #This will hold all the values given to us from net_tool.pull_from_field()
    makerE_temp_entire_day = []

    #Since we are pulling so much data from ThingSpeak, sometimes it messes up
    #In the case that net_tool.pull_from_field() runs into an error, a message will be printed and
    #   it will return [0]
    #This while loop just makes sure that we get the data, so it trys to get the data, and then checks to make sure
    #   its not equal to [0]
    got_data = False
    while(not got_data):

        #Gets the last 48 entries from the first field, I think the data is taken every ~30 minutes so 48 entries for a day
        makerE_temp_entire_day = net_tool.pull_from_field(1,48)

        #Makes sure the data returned is actual data and not what's returned in an error
        if(makerE_temp_entire_day != [0]):
            got_data = True

    #A new list to hold all of the floats we will convert from makerE_temp_entire_day
        #Since net_tool.pull_from_field() returns a list of Strings
    makerE_temp_entire_day_floats = []

    #Constructing the above list
    for temp in makerE_temp_entire_day:
        makerE_temp_entire_day_floats.append(float(temp))


    if(DEBUG):
        print("Got tempature. temp =", makerE_temp_entire_day_floats)
        print()

    #This list is the color for each hour
    temp_per_hour_color = []

    #This is the range for the entire day, its defined by the min and max for that day
    day_temp_range = [min(makerE_temp_entire_day_floats), max(makerE_temp_entire_day_floats)]

    #This loop goes through the list of tempature floats 2 at a time and finds the average for the hour
    #   Then it converts it into a color in the same way as basic loop
    for i in range(0,len(makerE_temp_entire_day_floats),2):

        #Find the average for that hour
        hour_temp = (makerE_temp_entire_day_floats[i] + makerE_temp_entire_day_floats[i+1])/2

        #Same as in simple_loop()
        hour_temp_color_value = neoFun.maprange(day_temp_range, [0,255], hour_temp)
        hour_temp_color = (hour_temp_color_value, 0, (255-hour_temp_color_value))

        #Add the color to the list
        temp_per_hour_color.append(hour_temp_color)

    #And then for each LED set it to the corresponding color for that hour
    for p in range(neoFun.NUM_LEDS):#There are 24 LEDS
        neoFun.set_pixel(temp_per_hour_color[p],p)

    #This sets the first pixel to green, to indicate the start of the day, or the point between the oldest measurment
    #   and the newest
    neoFun.set_pixel((0,255,0),0)


while(True):
    ##Call either basic_loop() or complex_loop() (complex_loop isn't That much more complex)
    basic_loop()
    #complex_loop()

    #Delay for some time between updates
    time.sleep(UPDATE_PERIOD)
