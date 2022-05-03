import asyncio
from websockets import serve
import json
from pyomyo import Myo, emg_mode

m = Myo()

async def handler(websocket, path):
	def raw_send(obj):
		try:
			return websocket.send(json.dumps(obj))
		except Exception as e:
			websocket.close()

	def send(obj):
		if websocket.open:
			asyncio.create_task(raw_send(obj))

	def emg_handler(emg, moving):
		send({"type":"emg", "data":emg})
	def imu_handler(quat, acc, gyro):
		send({"type":"imu", "data":{"quat":quat, "acc":acc, "gyro":gyro}})
	#def arm_handler
	def pose_handler(p):
		send({"type":"pose", "data":p})
	def battery_handler(battery_level):
		send({"type":"battery", "data":battery_level})

	async for message in websocket:
		print(message)
		event = json.loads(message)
		type = event["type"]
		if (type == "connect"): # mode 0-3
			m.mode = emg_mode(int(event["mode"]))
			m.add_emg_handler(emg_handler)
			m.add_imu_handler(imu_handler)
			m.add_pose_handler(pose_handler)
			#m.add_arm_handler(lambda arm, xdir: send({"type":"arm", "data":arm}))
			m.add_battery_handler(battery_handler)
			m.connect()
			await websocket.send(json.dumps({"type":"connect", "message":"myo connected"}))
		elif (type == "power_off"):
			m.power_off()
		elif (type == "vibrate"): # value between [1;4]
			m.vibrate(int(event["value"]))
		elif (type == "set_leds"): # logo and line as Color RGB (0-255)
			m.set_leds(event["logo"], event["line"])
	
	await websocket.wait_closed()
	print('closed')

	m.emg_handlers.remove(emg_handler)
	m.imu_handlers.remove(imu_handler)
	#m.arm_handlers.remove(arm_handler)
	m.pose_handlers.remove(pose_handler)
	m.battery_handlers.remove(battery_handler)

async def main():
	async with serve(handler, "localhost", 9898):
		while True:
			if (m.conn != None):
				m.run()
			await asyncio.sleep(.001)
        	#await asyncio.Future()  # run forever

if __name__ == '__main__':
	asyncio.run(main())