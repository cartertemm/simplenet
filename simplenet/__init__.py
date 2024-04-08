import enet
from enet import (
	EVENT_TYPE_NONE as EVENT_NONE,
	EVENT_TYPE_CONNECT as EVENT_CONNECT,
	EVENT_TYPE_DISCONNECT as EVENT_DISCONNECT,
	EVENT_TYPE_RECEIVE as EVENT_RECEIVE,
)


peer_state_map = {
	enet.PEER_STATE_DISCONNECTED: "disconnected",
	enet.PEER_STATE_CONNECTING: "connecting",
	enet.PEER_STATE_ACKNOWLEDGING_CONNECT: "acknowledging connect",
	enet.PEER_STATE_CONNECTION_PENDING: "connection pending",
	enet.PEER_STATE_CONNECTION_SUCCEEDED: "connection succeeded",
	enet.PEER_STATE_CONNECTED: "connected",
	enet.PEER_STATE_DISCONNECT_LATER: "disconnect later",
	enet.PEER_STATE_DISCONNECTING: "disconnecting",
	enet.PEER_STATE_ACKNOWLEDGING_DISCONNECT: "acknowledging disconnect",
	enet.PEER_STATE_ZOMBIE: "zombie"
}

class event:
	def __init__(self, obj):
		self.type = obj.type
		self.channel = obj.channelID
		if obj.packet.is_valid():
			self.data = obj.packet.data
			self.data_length = obj.packet.dataLength
			try:
				self.message = self.data.decode()
			except UnicodeDecodeError:
				self.message = ""
		else:
			self.data = b""
			self.data_length = 0
			self.message = ""
		self.peer = None

class peer:
	def __init__(self, host, obj):
		self.host = host
		self.id = obj.incomingPeerID
		self.hostname = obj.address.hostname
		self.address = obj.address
		self.port = obj.address.port
		self.update(obj)

	def update(self, obj):
		self.obj = obj

	def ping(self):
		return self.obj.ping()

	def disconnect(self, data=0):
		del self.host._peers[self.id]
		return self.obj.disconnect(data)

	def disconnect_softly(self, data=0):
		del self.host._peers[self.id]
		return self.obj.disconnect_later(data)

	def disconnect_forcefully(self, data=0):
		del self.host._peers[self.id]
		return self.obj.disconnect_now(data)

	def send(self, data, channel=0, reliable=True, autoflush=True):
		return self.host.send(data, channel=channel, reliable=reliable, peers=self, autoflush=autoflush)

	def send_reliable(self, data, channel=0):
		return self.host.send_reliable(self, data, channel)

	def send_unreliable(self, data, channel=0):
		return self.host.send_unreliable(self, data, channel)

	def get_state_string(self):
		return peer_state_map[self.state]

	def __repr__(self):
		return f"<ENet peer(id={self.id}, hostname={self.hostname}, port={self.port}, state={self.get_state_string()})>"

	@property
	def state(self):
		return self.obj.state

	@property
	def channels(self):
		return self.obj.channelCount

	@property
	def incoming_bandwidth(self):
		return self.obj.incomingBandwidth

	@property
	def outgoing_bandwidth(self):
		return self.obj.outgoingBandwidth

	@property
	def packets_sent(self):
		return self.obj.packetsSent

	@property
	def packets_lost(self):
		return self.obj.packetsLost

	@property
	def packet_loss(self):
		return self.obj.packetLoss

	@property
	def round_trip_time(self):
		return self.obj.roundTripTime


class ConnectionHost:
	def __init__(self, addr=None, port=0, peer_count=0, channels=0, incoming_bandwidth=0, outgoing_bandwidth=0):
		# save these so we can destroy and optionally reuse
		self._init_args = [addr, port, peer_count, channels, incoming_bandwidth, outgoing_bandwidth]
		address = None
		if addr and port > 0:
			addr = addr if isinstance(addr, bytes) else addr.encode()
			address = enet.Address(addr, port)
		self.host = enet.Host(address, peer_count, channels, incoming_bandwidth, outgoing_bandwidth)
		print(address, peer_count, channels, incoming_bandwidth, outgoing_bandwidth)
		self._peers = {}

	def __del__(self):
		return self.destroy()

	def connect(self, addr, port, data=None):
		if not isinstance(addr, bytes):
			addr = bytes(addr, "ascii")
		address = enet.Address(addr, port)
		return self.host.connect(address, self.channels)

	def destroy(self, use_again=False):
		if hasattr(self, "host") and self.host is not None:
			for id in list(self._peers):
				self.disconnect_peer_forcefully(id)
			self.host.flush()
		if use_again:
			self.__init__(**self._init_args)

	def enable_compression(self):
		return self.host.compress_with_range_coder()

	def send(self, data, channel=0, reliable=True, peers=None, autoflush=True):
		flags = enet.PACKET_FLAG_RELIABLE if reliable else enet.PACKET_FLAG_UNRELIABLE_FRAGMENT
		if not isinstance(data, bytes):
			data = data.encode()
		packet = enet.Packet(data, flags)
		if isinstance(peers, list) or isinstance(peers, tuple):
			return [peer.obj.send(channel, packet) for peer in self.peers]
		elif peers is not None:
			peer = self.find_peer(peers)
			return peer.obj.send(channel, packet)
		status = self.host.broadcast(channel, packet)
		if autoflush:
			self.flush()
		return status

	def send_reliable(self, peer, data, channel=0):
		return self.send(data, channel=channel, reliable=True, peers=peer)

	def send_unreliable(self, peer, data, channel=0):
		return self.send(data, channel=channel, reliable=False, peers=peer)

	def flush(self):
		return self.host.flush()

	def service(self, timeout=0):
		evt = self.host.service(timeout)
		if evt.type == EVENT_NONE:
			return evt
		e = event(evt)
		p = self._make_peer(evt.peer)
		e.peer = p
		if evt.type == EVENT_DISCONNECT:
			del self._peers[evt.peer.incomingPeerID]
		return e

	def find_peer(self, id):
		if isinstance(id, peer):
			return id
		elif isinstance(id, int):
			p = self._peers.get(id)
		elif isinstance(id, enet.Peer):
			p = self._peers.get(id["incomingPeerID"])
		return p

	def _make_peer(self, p):
		p2 = self._peers.get(p.incomingPeerID)
		if not p2:
			p2 = peer(self, p)
			self._peers[p.incomingPeerID] = p2
		else:
			p2.update(p)
		return p2

	def disconnect_peer(self, peer, data=0):
		peer = self.find_peer(peer)
		if not peer:
			return
		return peer.disconnect(data)

	def disconnect_peer_forcefully(self, peer, data=0):
		peer = self.find_peer(peer)
		if not peer:
			return
		return peer.disconnect_forcefully(data)

	def disconnect_peer_softly(self, peer, data=0):
		peer = self.find_peer(peer)
		if not peer:
			return
		return peer.disconnect_softly(data)

	@property
	def hostname(self):
		return self.host.address.hostname

	@property
	def port(self):
		return self.host.address.port

	@port.setter
	def port(self, value):
		self.host.address.port = value

	@property
	def channels(self):
		return self.host.channelLimit

	@channels.setter
	def channels(self, value):
		self.host.channelLimit = value

	@property
	def incoming_bandwidth(self):
		return self.host.incomingBandwidth

	@incoming_bandwidth.setter
	def incoming_bandwidth(self, value):
		self.host.incomingBandwidth = value

	@property
	def outgoing_bandwidth(self):
		return self.host.outgoingBandwidth

	@outgoing_bandwidth.setter
	def outgoing_bandwidth(self, value):
		self.host.outgoingBandwidth = value

	@property
	def peer_count(self):
		return self.host.peerCount

	@peer_count.setter
	def peer_count(self, value):
		self.host.peerCount = value

	@property
	def total_sent_data(self):
		return self.host.totalSentData

	@total_sent_data.setter
	def total_sent_data(self, value):
		self.host.totalSentData = value

	@property
	def total_sent_packets(self):
		return self.host.totalSentPackets

	@total_sent_packets.setter
	def total_sent_packets(self, value):
		self.host.totalSentPackets = value

	@property
	def total_received_data(self):
		return self.host.totalReceivedData

	@total_received_data.setter
	def total_received_data(self, value):
		self.host.totalReceivedData = value

	@property
	def total_received_packets(self):
		return self.host.totalReceivedPackets

	@total_received_packets.setter
	def total_received_packets(self, value):
		self.host.totalReceivedPackets = value

	@property
	def peers(self):
		return {i.incomingPeerID: i for i in self.host.peers}


class Client(ConnectionHost):
	def __init__(self, channels=0, max_peers=1):
		super().__init__(None, 0, max_peers, channels)


class Server(ConnectionHost):
	def __init__(self, port, channels, max_peers, addr="localhost"):
		super().__init__(addr, port, max_peers, channels)
