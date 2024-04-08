import net


host = net.Server(54301, 10, 1)
connect_count = 0
run = True
shutdown_recv = False
while run:
	event = host.service(1000)
	if event.type == net.EVENT_CONNECT:
		print("%s: CONNECT" % event.peer.address)
		connect_count += 1
	elif event.type == net.EVENT_DISCONNECT:
		print("%s: DISCONNECT" % event.peer.address)
		connect_count -= 1
		if connect_count <= 0 and shutdown_recv:
			run = False
	elif event.type == net.EVENT_RECEIVE:
		msg = event.message
		print("%s: IN:  %r" % (event.peer.address, msg))
		if msg == "ping":
			event.peer.send("pong")
		elif msg == "SHUTDOWN":
			shutdown_recv = True
		elif event.peer.send(msg) < 0:
			print("%s: Error sending echo packet!" % event.peer.address)
		else:
			print("%s: OUT: %r" % (event.peer.address, msg))
