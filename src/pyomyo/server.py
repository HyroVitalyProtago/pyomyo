import asyncio
from websockets import serve
import json
from pyomyo import Myo, emg_mode

m = Myo()

async def handler(websocket, path):
	def send(obj):
		asyncio.create_task(websocket.send(json.dumps(obj)))

	async for message in websocket:
		print(message)
		event = json.loads(message)
		type = event["type"]
		if (type == "connect"): # mode 0-3
			m.mode = emg_mode(int(event["mode"]))
			m.add_emg_handler(lambda emg, moving, times=[]: send({"type":"emg", "data":emg}))
			m.add_imu_handler(lambda quat, acc, gyro: send({"type":"imu", "data":quat}))
			m.add_pose_handler(lambda p: send({"type":"pose", "data":p}))
			#m.add_arm_handler(lambda arm, xdir: send({"type":"arm", "data":arm}))
			m.add_battery_handler(lambda battery_level: send({"type":"battery", "data":battery_level}))
			m.connect()
			await websocket.send(json.dumps({"type":"connect", "message":"myo connected"}))
		elif (type == "power_off"):
			m.power_off()
		elif (type == "vibrate"): # value between [1;4]
			m.vibrate(int(event["value"]))
		elif (type == "set_leds"): # logo and line as Color RGB (0-255)
			m.set_leds(event["logo"], event["line"])

async def main():
	async with serve(handler, "localhost", 9898):
		while True:
			if (m.conn != None):
				m.run()
			await asyncio.sleep(.001)
        	#await asyncio.Future()  # run forever

if __name__ == '__main__':
	asyncio.run(main())