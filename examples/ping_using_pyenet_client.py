import time
import enet


SHUTDOWN_MSG = b"SHUTDOWN"
MSG_NUMBER = 10
host = enet.Host(None, 1, 0, 0, 0)
peer = host.connect(enet.Address(b"localhost", 54301), 1)

counter = 0
run = True
pingtime = 0
while run:
	event = host.service(1000)
	if event.type == enet.EVENT_TYPE_CONNECT:
		print("%s: CONNECT" % event.peer.address)
		event.peer.send(0, enet.Packet(b"ping"))
		pingtime = time.time()
		counter += 1
	elif event.type == enet.EVENT_TYPE_DISCONNECT:
		print("%s: DISCONNECT" % event.peer.address)
		run = False
		continue
	elif event.type == enet.EVENT_TYPE_RECEIVE:
		msg = event.packet.data.decode()
		if msg == "pong" and pingtime > 0:
			print((time.time()-pingtime)*1000)
			event.peer.send(0, enet.Packet(b"ping"))
			pingtime = time.time()
			counter += 1
	if counter == MSG_NUMBER:
		break

