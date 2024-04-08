import time
import simplenet


SHUTDOWN_MSG = b"SHUTDOWN"
MSG_NUMBER = 10
host = simplenet.Client(channels=1)
peer = host.connect("localhost", 54301)

counter = 0
run = True
pingtime = 0
while run:
	event = host.service(1000)
	if event.type == simplenet.EVENT_CONNECT:
		print("%s: CONNECT" % event.peer.address)
		event.peer.send("ping")
		pingtime = time.time()
		counter += 1
	elif event.type == simplenet.EVENT_DISCONNECT:
		print("%s: DISCONNECT" % event.peer.address)
		break
	elif event.type == simplenet.EVENT_RECEIVE:
		msg = event.message
		if msg == "pong" and pingtime > 0:
			print((time.time()-pingtime)*1000)
			event.peer.send("ping")
			pingtime = time.time()
			counter += 1
	if counter == MSG_NUMBER:
		break

