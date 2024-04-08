import time
import simplenet


def process_event(event):
	peer = event.peer
	if event.type == simplenet.EVENT_CONNECT:
		print(f"Connection from {peer.hostname}, peer #{peer.id}")
	elif event.type == simplenet.EVENT_DISCONNECT:
		print(f"{peer.hostname} (peer #{peer.id}) just disconnected")
	elif event.type == simplenet.EVENT_RECEIVE:
		print(f"message from {peer.hostname}: {event.message}")
		if event.message.lower().startswith("hello"):
			peer.send("acknowledged. Welcome!!!")
			peer.send("bye")
			peer.disconnect_softly()


n = simplenet.Server(45530, 1, 4000)
n.enable_compression()
def loop():
	while True:
		time.sleep(0.005)
		event = n.service()
		while event.type != simplenet.EVENT_NONE:
			process_event(event)
			event = n.service()


if __name__ == "__main__":
	loop()
