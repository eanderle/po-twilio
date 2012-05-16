from poke_socket import PokeSocket

# Poke as represented in a team (ie, in battle)
class TeamPoke(object):

	def __init__(self):
		self.poke_num = 173
		self.sub_num = 0
		self.name = "LOLZ\0"
		self.item = 71
		self.ability = 98
		self.nature = 0
		self.gender = 1
		self.shiny = 1
		self.happiness = 127
		self.level = 100
		self.moves[0] = 118
		self.moves[1] = 227
		self.moves[2] = 150
		self.moves[3] = 271
		DVs[:5] = 31
		EVs[:5] = 10
	
	def serialize():
		msg = struct.pack('>H', self.poke_num)
		msg += struct.pack('>B', self.sub_num)
		msg += self.name
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
			msg += TeamPoke.serialize()
		return msg

# Player as represented in the teambuilder
class PlayerTeam(object):

	def __init__(self, name):
		self.name = name
	
	# Prepare the PlayerTeam to be sent over the wire
	def serialize(self):
		msg = self.name
		msg += "Hi! I'm the Twilio PO client!\0" # Player info
		msg += "Darn! I lost!\0" # Lose message
		msg += "Yeah! I won!\0"  # Win message
		msg += struct.pack('>H', 42) # Avatar ID
		msg += Team.serialize()
		return msg

# Used for logging into the server
class FullPlayerInfo(object):
	
	def __init__(self, name):
		self.name = name + '\0'
	
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

s = PokeSocket('188.165.249.120', 5080)
s.send(FullPlayerInfo('Twilio Client').serialize(), poke_socket.LOGIN); 
