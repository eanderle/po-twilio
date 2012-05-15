import socket

WHATAREYOU = 0
WHOAREYOU = 1
LOGIN = 2
LOGOUT = 3
SENDMESSAGE = 4
PLAYERSLIST = 5
SENDTEAM = 6
CHALLENGESTUFF = 7
ENGAGEBATTLE = 8
BATTLEFINISHED = 9
BATTLEMESSAGE = 10
BATTLECHAT = 11
KEEPALIVE = 12
ASKFORPASS = 13
REGISTER = 14
PLAYERKICK = 15
PLAYERBAN = 16
SERVNUMCHANGE = 17
SERVDESCCHANGE = 18
SERVNAMECHANGE = 19
SENDPM = 20
AWAY = 21
GETUSERINFO = 22
GETUSERALIAS = 23
GETBANLIST = 24
CPBAN = 25
CPUNBAN = 26
SPECTATEBATTLE = 27
SPECTATINGBATTLEMESSAGE = 28
SPECTATINGBATTLECHAT = 29
SPECTATINGBATTLEFINISHED = 30
LADDERCHANGE = 31
SHOWTEAMCHANGE = 32
VERSIONCONTROL = 33
TIERSELECTION = 34
SERVMAXCHANGE = 35
FINDBATTLE = 36
SHOWRANKINGS = 37
ANNOUNCEMENT = 38
CPTBAN = 39
CPTUNBAN = 40
PLAYERTBAN = 41
GETTBANLIST = 42
BATTLELIST = 43
CHANNELSLIST = 44
CHANNELPLAYERS = 45
JOINCHANNEL = 46
LEAVECHANNEL = 47
CHANNELBATTLE = 48
REMOVECHANNEL = 49
ADDCHANNEL = 50
CHANNELMESSAGE = 51
CHANNAMECHANGE = 52
HTMLMESSAGE = 53
HTMLCHANNEL = 54
SERVERNAME = 55
SPECIALPASS = 56
SERVERLISTEND = 57
SETIP = 58

class PokeSocket(object):

	def __init__(self, addr, port):
		#create an INET, STREAMing socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((addr, port))

	def send(self, msg_body, msg_type):
		size = len(msg_body) + 1 # msg_body + msg_type
		send = struct.pack('>HB', size, msg_type) + msg_body
		totalsent = 0
		while totalsent < size:
			sent = self.sock.send(send[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection error")
			totalsent = totalsent + sent
	
	def recv(self):
		msg = ''
		size_str = self.sock.recv(2)
		if size_str == ''
			raise RuntimeError("socket connection error")
		size = struct.unpack('>H', size_str)
		while len(msg) < size:
			chunk = self.sock.recv(size - len(msg))
			if chunk == '':
				raise RuntimeError("sockect connection error")
			msg = msg + chunk
		return msg
