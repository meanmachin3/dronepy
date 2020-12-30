import os
import sys
sys.path.append('..')

from djitellopy import Tello
import argparse
import cv2
import sys,tty,os,termios


class Tello:
    def __init__(self, speed, save_session, save_path):
        # Initialize Tello object
        self.tello = Tello()

        # Set starting parameters
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.send_rc_control = False

        self.speed = speed
        self.save_session = save_session
        self.save_path = save_path

        if self.save_session:
            os.makedirs(self.save_path, exist_ok=True)

    def getkey(self):
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            while True:
                b = os.read(sys.stdin.fileno(), 3).decode()
                if len(b) == 3:
                    k = ord(b[2])
                else:
                    k = ord(b)
                key_mapping = {
                    127: 'backspace',
                    10: 'return',
                    32: 'space',
                    9: 'tab',
                    27: 'esc',
                    65: 'up',
                    66: 'down',
                    67: 'right',
                    68: 'left'
                }
                return key_mapping.get(k, chr(k))
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


    def run(self):
        if not self.tello.connect():
            print("Tello not connected")
            return
        elif not self.tello.set_speed(self.speed):
            print('Not set speed to lowest possible')
            return
        elif not self.tello.streamoff():
            print("Could not stop video stream")
            return
        elif not self.tello.streamon():
            print("Could not start video stream")
            return

        self.tello.get_battery()

        # frame_read = self.tello.get_frame_read()
        imgCount = 0

        while True:
            # if frame_read.stopped:
            #     frame_read.stop()
            #     break
            
            # frame = frame_read.frame

            # if self.save_session:
            #     cv2.imwrite(f'{self.save_path}/{imgCount}.jpg', frame)
            #     imgCount += 1

            # k = cv2.waitKey(20)
            k = self.getkey()
            if k == 'esc':  # break when ESC is pressed
                break
            elif k == 't':
                self.tello.takeoff()
                self.send_rc_control = True
            elif k == 'l':
                self.tello.land()
                self.send_rc_control = False

            if self.send_rc_control:
                # fligh forward and back
                if k == 'w':
                    self.for_back_velocity = self.speed
                elif k == 's':
                    self.for_back_velocity = -self.speed
                else:
                    self.for_back_velocity = 0
                
                # fligh left & right
                if k == 'd':
                    self.left_right_velocity = self.speed
                elif k == 'a':
                    self.left_right_velocity = -self.speed
                else:
                    self.left_right_velocity = 0
    
                # fligh up & down
                if k == 'up':
                    self.up_down_velocity = self.speed
                elif k == 'down':
                    self.up_down_velocity = -self.speed
                else:
                    self.up_down_velocity = 0

                # turn right or left
                if k == 'right':
                    self.yaw_velocity = self.speed
                elif k == 'left':
                    self.yaw_velocity = -self.speed
                else:
                    self.yaw_velocity = 0

                print(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity, self.yaw_velocity)
                # Send velocities to Drone
                self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity, self.yaw_velocity)

            # cv2.putText(frame, f'Battery: {str(self.tello.get_battery())[:2]}%', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            # cv2.imshow('Tello Drone', frame)
        
        # Destroy cv2 windows and end drone connection 
        # cv2.destroyAllWindows()
        # self.tello.end()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--speed', type=int, default=40, help='Speed of drone')
    parser.add_argument('-sa', '--save_session', action='store_true', help='Record flight')
    parser.add_argument('-sp', '--save_path', type=str, default="session/", help="Path where images will get saved")
    args = parser.parse_args()

    drone = RyzeTello(args.speed, args.save_session, args.save_path)
    drone.run()
