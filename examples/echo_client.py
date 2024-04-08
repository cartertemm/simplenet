import simplenet


c = simplenet.Client(channels=1)
c.enable_compression()
peer = c.connect("localhost", 45530)
while True:
	event = c.service()
	if event.type == simplenet.EVENT_CONNECT:
		print("Connection success. Sending hello")
		c.send("Hello")
	elif event.type == simplenet.EVENT_RECEIVE:
		print(f"got {event.message}")
		if event.message == "bye":
			print("The server is about to disconnect us...")
	elif event.type == simplenet.EVENT_DISCONNECT:
		print("Disconnected")
		c.destroy()
		break
