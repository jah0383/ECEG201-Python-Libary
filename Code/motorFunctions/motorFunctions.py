'''
Author: James Howe

A basic class which keeps track of the current location of the stepper motor and
allows one to either set it's poistion or move it

I use CW for clockwise and CCW for counter clockwise

not using `style = stepper.DOUBLE` for the movement results in inaccuracies 

some examples are at the end
'''
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper






class ECEGMotor():
    '''
    A basic class which keeps track of the current stepper motor position
    and allows the user to move it 
    '''
    STEPS_FOR_FULL = 4096 #The number of steps for a full rotation

    def __init__(self, debug):
        """
        The intilizer for the method, finds home by moving in a full circle

        """
        self.__debug = debug
        self.__kit = MotorKit(i2c=board.I2C())
        self.__stepper = self.__kit.stepper1
        self.__find_home()
        self.__current_step = 0 #the current number of steps CW from home(step 0)


    def __find_home(self):
        """
        A private method for finding the peg on the device, just moves it CCW 1 full rotation
        """
        if self.__debug:
            print("Finding the home of the stepper moter")
        for i in range(ECEGMotor.STEPS_FOR_FULL):
           self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
        if self.__debug:
            print("Home found\n")

    def get_current_step(self):
        """
        A getter method that returns the current number of steps CW from home(step 0)    

        Returns: int, current number fo steps CW
        """
        return self.current_step

    def get_stepper(self):
        """
        A getter method for the stepper

        Returns: MotorKit.stepper1()
        """
        return self.__stepper

    def get_current_degree(self):
        """
        A method which calculates and returns the position of the arm as the number of degrees from home

        Returns: float 
        """
        return (float(self.__current_step) / float(ECEGMotor.STEPS_FOR_FULL)) * 360.0 * 2

    def set_position_degrees(self, pos):
        """
        Takes in the position in degrees from home and then moves the arm to that location

        Params: The position in degrees that you want the arm to go to, could be int or float will do nothing if its not 0-360
        """

        if(pos < 0 or pos > 360):
            print("Input not between 0 and 360, the motor will not be moved")
            return
        
        goal_pos_in_steps = int(((pos/360) * ECEGMotor.STEPS_FOR_FULL)/2)
        
        steps_to_take =  goal_pos_in_steps - self.__current_step

        for i in range(abs(steps_to_take)):

            #Move the arm CCW
            if(steps_to_take < 0):
                self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
                self.__current_step -= 2

            #Move the arm CW
            else:
                self.__stepper.onestep(style = stepper.DOUBLE)
                
    def set_position_steps(self, pos):
        """
        Takes in the position in steps from home and then moves the arm to that location

        Params: The position in steps that you want the arm to go to, could be int or float. It will do nothing if its not between 0 and STEPS_FOR_FULL(For now 4096)
        """

        if(pos < 0 or pos > ECEGMotor.STEPS_FOR_FULL):
            print("Input not between 0 and", ECEGMotor.STEPS_FOR_FULL, "the motor will not be moved")
            return
        
        
        steps_to_take =  pos - self.__current_step

        for i in range(abs(steps_to_take)):

            #Move the arm CCW
            if(steps_to_take < 0):
                self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
                self.__current_step -= 2

            #Move the arm CW
            else:
                self.__stepper.onestep(style = stepper.DOUBLE)
                self.__current_step += 2

    def reset_position(self):
        """
        Resets the position of the arm to home
        """
        
        for i in range(self.__current_step):
            self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
        self.__current_step = 0


    def move_arm_steps(self, amount):
        """
        Moves the arm amount steps, if amount is negative then the arm is moved CCW and if its positive it moves CW
        """
        for i in range(abs(amount)):
            
            if(amount < 0):
                if(self.__current_step == 0):
                    return
                
                self.__stepper.onestep(direction = stepper.BACKWARD,style = stepper.DOUBLE)
                self.__current_step -= 2
                
            else:
                if(self.current_step == ECEGMotor.STEPS_FOR_FULL):
                    return
                
                self.__stepper.onestep(style = stepper.DOUBLE)
                self.__current_step += 2

##EXAMPLES
'''
print("starting")
myMotor = ECEGMotor()



myMotor.set_position_degrees(90)
print(myMotor.get_current_degree())
myMotor.reset_position()

myMotor.set_position_degrees(180)
print(myMotor.get_current_degree())
myMotor.reset_position()
myMotor.set_position_degrees(340)
print(myMotor.get_current_degree())
myMotor.reset_position()
myMotor.stepper.release()

'''
