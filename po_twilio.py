import struct
from poke_socket import PokeSocket
import poke_socket

def make_q_string(s):
	# QStrings are twice the size of python strings
	msg = struct.pack('>I', 2*len(s))
	msg += s.encode('utf_16_be')
	return msg

def make_py_string(s):
	size = struct.unpack('>I', s[:4])
	return s[4:4+size[0]].decode('utf_16_be')

# Poke as represented in a team
class TeamPoke(object):

	def __init__(self):
		self.poke_num = 1
		self.sub_num = 0
		self.name = "LOLZ"
		self.item = 71
		self.ability = 65
		self.nature = 0
		self.gender = 2
		self.shiny = 1
		self.happiness = 0
		self.level = 100
		self.moves = [213, 445, 204, 203]
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
		msg = struct.pack('>B', 5) # gen 5
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
		msg += make_q_string('Challenge Cup') # Default tier
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

class BattleMove(object):

	def __init__(self, msg):
		self.move_num = struct.unpack('>H', msg[:2])
		self.current_pp = struct.unpack('>B', msg[2])
		self.total_pp = struct.unpack('>B', msg[3])

# Poke used in battle
class BattlePoke(object):

	def __init__(self, msg):
		fields = struct.unpack('>HB', msg[0:3])
		self.poke_num = fields[0]
		self.sub_num = fields[1]
		self.name = make_py_string(msg[3:])
		self.offset = 7 + (len(self.name)*2) # poke_num + sub_num + name_size + name
		self.total_hp = struct.unpack('>H', msg[self.offset:self.offset+2])[0]
		self.current_hp = struct.unpack('>H', msg[self.offset+2:self.offset+4])[0]
		self.gender = struct.unpack('>B', msg[self.offset+4])[0]
		self.shiny = struct.unpack('>B', msg[self.offset+5])[0]
		self.level = struct.unpack('>B', msg[self.offset+6])[0]
		self.item = struct.unpack('>H', msg[self.offset+7:self.offset+9])[0]
		self.ability = struct.unpack('>H', msg[self.offset+9:self.offset+11])[0]
		self.happiness = struct.unpack('>B', msg[self.offset+11])[0]

		self.stats = [0,0,0,0,0]
		for i in range(5):
			self.stats[i] = struct.unpack('>H', msg[self.offset+12+(i*2):self.offset+14+(i*2)])[0]

		self.moves = []
		for i in range(4):
			self.moves.append(BattleMove(msg[22+(i*4):26+(i*4)]))

		self.EVs = [0,0,0, 0,0,0]
		for i in range(6):
			self.EVs[i] = struct.unpack('>I', msg[self.offset+38+(i*4):self.offset+42+(i*4)])[0]

		self.DVs = [0,0,0, 0,0,0]
		for i in range(6):
			self.DVs[i] = struct.unpack('>I', msg[self.offset+62+(i*4):self.offset+66+(i*4)])[0]
		self.offset += 86

# Team used for battle
class BattleTeam(object):

	def __init__(self, msg):
		self.pokes = []
		offset = 0
		for i in range(6):
			self.pokes.append(BattlePoke(msg[offset:]))
			offset += self.pokes[i].offset
			print self.pokes[i].__dict__.items()

class BattleConf(object):

	def __init__(self, msg):
		self.gen = struct.unpack('>B', msg[0])[0]
		self.mode = struct.unpack('>B', msg[1])[0]
		self.id_1 = struct.unpack('>I', msg[2:6])[0]
		self.id_2 = struct.unpack('>I', msg[6:10])[0]
		self.clauses = struct.unpack('>I', msg[10:14])[0]

s = PokeSocket('188.165.249.120', 5080)
s.send(FullPlayerInfo('Twilio Client').serialize(), poke_socket.LOGIN); 
s.recv() # Don't care about the server's response

# Find a battle
flags = 2 # Only flag we want is forceSameTier
msg = struct.pack('>I', flags)
msg = struct.pack('>B', 200) # range
msg = struct.pack('>B', 0) # Don't really know why this is needed
s.send(msg, poke_socket.FINDBATTLE)

while 1:
	msg = s.recv()
	cmd = struct.unpack('>B', msg[0])[0]
	if cmd == poke_socket.ENGAGEBATTLE:
		battle_id = struct.unpack('>I', msg[1:5])[0]
		p1_id = struct.unpack('>I', msg[5:9])[0]
		p2_id = struct.unpack('>I', msg[9:13])[0]
		if p1_id == 0: # This is us!
			print 'Battle found!'
			bc = BattleConf(msg[13:])
			team = BattleTeam(msg[27:])
s.close()
