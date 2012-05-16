import struct
from poke_socket import PokeSocket
import poke_socket

def make_q_string(s):
	# QStrings are twice the size of python strings
	msg = struct.pack('>I', 2*len(s))
	msg += s.encode('utf_16_be')
	return msg

# Poke as represented in a team
class TeamPoke(object):

	def __init__(self):
		self.poke_num = 173
		self.sub_num = 0
		self.name = "LOLZ"
		self.item = 71
		self.ability = 98
		self.nature = 0
		self.gender = 1
		self.shiny = 1
		self.happiness = 127
		self.level = 100
		self.moves = [118, 227, 150, 271]
		self.DVs = [31, 31, 31, 31, 31, 31]
		self.EVs = [10, 10, 10, 10, 10, 10]
	
	def serialize(self):
		msg = struct.pack('>H', self.poke_num)
		msg += struct.pack('>B', self.sub_num)
		msg += make_q_string(self.name)
		msg += struct.pack('>H', self.item)
		msg += struct.pack('>H', self.ability)
		msg += struct.pack('>B', self.nature)
		msg += struct.pack('>B', self.gender)
		msg += struct.pack('>B', self.shiny)
		msg += struct.pack('>B', self.happiness)
		msg += struct.pack('>B', self.level)
		for i in range(4):
			msg += struct.pack('>I', self.moves[i])
		for i in range(6):
			msg += struct.pack('>B', self.DVs[i])
		for i in range(6):
			msg += struct.pack('>B', self.EVs[i])
		return msg

# The actual team (I did not design/name these classes originally)
# Going to have to extend this to be able to receive a team over the wire
class Team(object):
	def serialize(self):
		msg = ''
		for i in range(6):
			msg += TeamPoke().serialize()
		return msg

# Player as represented in the teambuilder
class PlayerTeam(object):

	def __init__(self, name):
		self.name = name
	
	# Prepare the PlayerTeam to be sent over the wire
	def serialize(self):
		msg = make_q_string(self.name)
		msg += make_q_string("Hi! I'm the Twilio PO client!") # Player info
		msg += make_q_string("Darn! I lost!") # Lose message
		msg += make_q_string("Yeah! I won!")  # Win message
		msg += struct.pack('>H', 42) # Avatar ID
		msg += Team().serialize()
		return msg

# Used for logging into the server
class FullPlayerInfo(object):
	
	def __init__(self, name):
		self.name = name
	
	def serialize(self):
		msg = PlayerTeam(self.name).serialize()
		msg += struct.pack('>B', 1) # Ladder enabled = true
		msg += struct.pack('>B', 0) # Show team = false

		# Add a QColor
		msg += struct.pack('>B', 0) # QColor.spec
		msg += struct.pack('>H', 0xffff) # QColor.alpha
		msg += struct.pack('>H', 0) # QColor.red
		msg += struct.pack('>H', 0) # QColor.green
		msg += struct.pack('>H', 0) # QColor.blue
		msg += struct.pack('>H', 0) # QColor.pad

		return msg

# Poke used in battle
class BattlePoke(object):

	def __init__(self, msg):
		self.poke_num = struct.unpack('>H', msg[0:1])
		self.sub_num = struct.unpack('>B', msg[2])

# Team used for battle
#class BattleTeam(object):

print struct.pack('>H', 3)
s = PokeSocket('188.165.249.120', 5080)
s.send(FullPlayerInfo('Twilio Client').serialize(), poke_socket.LOGIN); 
s.recv() # Don't care about the server's response

# TODO: pick challenge cup
# Find a battle
flags = 2 # Only flag we want is forceSameTier
msg = struct.pack('>I', flags)
msg = struct.pack('>B', 200) # range
msg = struct.pack('>B', 0) # Don't really know why this is needed
s.send(msg, poke_sockt.FINDBATTLE)

while 1:
	msg = s.recv()
	cmd = struct.unpack('>B', msg[0])
	print msg
	if cmd == poke_socket.ENGAGEBATTLE:
		battle_id = struct.unpack('>I', msg[1:4])
		p1_id = struct.unpack('>I', msg[5:8])
		p2_id = struct.unpack('>I', msg[9:12])
		if p1_id == 0: # This is us!
			print 'Battle found!'
			break
	else:
		print 'Unrecognized message received'

s.close()
