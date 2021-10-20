from djitellopy import Tello
import cv2
import numpy as np
import time
import pygame

s=50
FPS=120

class DroneSoftware(object):
    def __init__(self):
        self.tello=Tello()
        pygame.init()

        #pygame windrow
        pygame.display.set_caption("Py game window")
        self.screen = pygame.display.set_mode([400,300])

        #drone speeds
        self.left_right_speed = 0
        self.forward_backward_speed = 0
        self.up_down_speed = 0
        self.yaw_speed = 0

        pygame.time.set_timer(pygame.USEREVENT+1,1000//FPS)

    def keydown(self, key):
        # 방향키
        if key == pygame.K_UP:
            self.forward_backward_speed = s
        elif key == pygame.K_DOWN:
            self.forward_backward_speed = -s
        elif key == pygame.K_RIGHT:
            self.left_right_speed = s
        elif key == pygame.K_LEFT:
            self.left_right_speed = -s
        # 방향 전환
        elif key == pygame.K_w:
            self.up_down_speed = s
        elif key == pygame.K_s:
            self.up_down_speed = -s
        elif key == pygame.K_d:
            self.yaw_speed = s
        elif key == pygame.K_a:
            self.yaw_speed = -s

        elif key == pygame.K_t:
            self.tello.takeoff()
        elif key == pygame.K_l:
            self.tello.land()

    def keyup(self, key):
        if key == pygame.K_UP or key == pygame.K_DOWN:
            self.forward_backward_speed = 0
        if key == pygame.K_RIGHT or key == pygame.K_LEFT:
            self.left_right_speed = 0
        if key == pygame.K_w or key == pygame.K_s:
            self.up_down_speed = 0
        if key == pygame.K_d or key == pygame.K_a:
            self.yaw_speed = 0

    def sendcommandtodrone(self):
        self.tello.send_rc_control(self.left_right_speed,
                                   self.forward_backward_speed,
                                   self.up_down_speed,
                                   self.yaw_speed)

    def run(self):
        self.tello.connect()
        stopRunning = False
        while not stopRunning:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT+1:
                    self.sendcommandtodrone()
                if event.type == pygame.QUIT:
                    stopRunning=True
                elif event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_ESCAPE:
                        stopRunning = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            self.screen.fill([0,0,0])
            pygame.display.update()
            time.sleep(1/FPS)
        self.tello.end()


def main():
    droneObj = DroneSoftware()
    droneObj.run()

if __name__ == '__main__':
    main()