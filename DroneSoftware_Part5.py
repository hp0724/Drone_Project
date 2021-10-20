# from DroneApi.VideoStreamRecorder import VideoStreamRecorder

from djitellopy import Tello
from threading import Thread
import cv2
import numpy as np
import time
import pygame


FPS = 30

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
thickness = 1
color = (0,0,255)
position = (5,580)

class DroneSoftware(object):

	def __init__(self):
		self.tello = Tello()
		pygame.init()

		# pygame Window
		pygame.display.set_caption("Drone Video Feed & Control")
		self.screen = pygame.display.set_mode([960,720])

		# Drone Speeds
		self.left_right_speed = 0 
		self.forward_backward_speed = 0
		self.up_down_speed = 0
		self.yaw_speed = 0

		# Drone Speed, [0,100] %, 8 m/sec, 2 m/sec
		self.S = 60

		# Record Video Thread and Settings
		# self.recorder_obj = VideoStreamRecorder(root="/Users/kshitizsharma/Pictures")
		self.start_recording = False
		self.stop_recording = False
		state_viderecord_thread = Thread(target=self.recordvideo, args=(), daemon=True)
		state_viderecord_thread.start()

		pygame.time.set_timer(pygame.USEREVENT+1, 1000//FPS)


	def recordvideo(self):
		while True:
			if self.start_recording:
				self.recorder_obj.record_video(videofeed = self.tello.get_frame_read())
				self.start_recording = False
			elif self.stop_recording:
				self.recorder_obj.record_stop()
				self.stop_recording=False
		

	def keydown(self, key):
		if key == pygame.K_UP:
			self.forward_backward_speed = self.S
		elif key == pygame.K_DOWN:
			self.forward_backward_speed = -self.S
		elif key == pygame.K_RIGHT:
			self.left_right_speed = self.S
		elif key == pygame.K_LEFT:
			self.left_right_speed = -self.S
		elif key == pygame.K_w:
			self.up_down_speed = self.S
		elif key == pygame.K_s:
			self.up_down_speed = -self.S
		elif key == pygame.K_d:
			self.yaw_speed = self.S
		elif key == pygame.K_a:
			self.yaw_speed = -self.S
		elif key == pygame.K_q and self.S>10:
			self.S = self.S - 10
		elif key == pygame.K_e and self.S<=90:
			self.S = self.S + 10
		elif key == pygame.K_z:
			self.start_recording=True
		elif key == pygame.K_x:
			self.stop_recording=True
			self.recorder_obj.running=False
		elif key == pygame.K_t:
			self.tello.takeoff()
		elif key == pygame.K_l:
			self.tello.land()

	def keyup(self, key):
		if key == pygame.K_UP or key == pygame.K_DOWN:
			self.forward_backward_speed = 0
		if key == pygame.K_RIGHT or key == pygame.K_RIGHT:
			self.left_right_speed = 0
		if key == pygame.K_w or key == pygame.K_s:
			self.up_down_speed = 0
		if key == pygame.K_d or key == pygame.K_a:
			self.yaw_speed = 0
								
	def sendcommandtodrone(self):
		'''
		left_right_velocity: -100~100 (left/right)
		forward_backward_velocity: -100~100 (forward/backward)
		up_down_velocity: -100~100 (up/down)
		yaw_velocity: -100~100 (yaw)
		'''
		self.tello.send_rc_control(self.left_right_speed,
			self.forward_backward_speed,
			self.up_down_speed,
			self.yaw_speed)

	def frameProcessing(self, frame):
		text = "Battery: {}% \nHeight:{} cm \nFlight Time:{} \nDrone Speed:{} \nRecording Status: {}".format(
				self.tello.get_battery(),
				self.tello.get_height(),
				self.tello.get_flight_time(),
				self.S,
				"Yes" if self.recorder_obj.running else "No")
		text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
		line_height = text_size[1]+5
		x, y0 = position
		for i, line in enumerate(text.split("\n")):
			y = y0 + i*line_height
			cv2.putText(frame,
				line, 
				(x,y),
				font, 
				font_scale, 
				color, 
				thickness)

		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frame = np.rot90(frame)
		frame = np.flipud(frame)
		frame = pygame.surfarray.make_surface(frame)
		return frame


	def run(self):
		self.tello.connect()
		self.tello.streamoff()
		self.tello.streamon()
		frameSource = self.tello.get_frame_read()
		self.screen.fill([0,0,0])

		stopRunning = False
		while not stopRunning:
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.sendcommandtodrone()
				if event.type == pygame.QUIT:
					stopRunning = True
				elif event.type == pygame.KEYDOWN:
					if event.type == pygame.K_ESCAPE:
						stopRunning = True
					else:
						self.keydown(event.key)	
				elif event.type == pygame.KEYUP:
					self.keyup(event.key)

			
			frame = self.frameProcessing(frameSource.frame)
			self.screen.blit(frame, (0,0))
			pygame.display.update()
			time.sleep(1/FPS)
		self.tello.end()
			
		
def main():
	droneobj = DroneSoftware()
	droneobj.run()

if __name__ == '__main__':
	main()