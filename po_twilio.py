import struct
from poke_socket import PokeSocket
import poke_socket
import random

SENDOUT = 0
SENDBACK = 1
USEATTACK = 2
OFFERCHOICE = 3
BEGINTURN = 4
CHANGEPP = 5
CHANGEHP = 6
KO = 7
EFFECTIVE = 8
MISS = 9
CRITICALHIT = 10
HIT = 11
STATCHANGE = 12
STATUSCHANGE = 13
STATUSMESSAGE = 14
FAILED = 15
BATTLECHAT = 16
MOVEMESSAGE = 17
ITEMMESSAGE = 18
NOOPPONENT = 19
FLINCH = 20
RECOIL = 21
WEATHERMESSAGE = 22
STRAIGHTDAMAGE = 23
ABILITYMESSAGE = 24
ABSSTATUSCHANGE = 25
SUBSTITUTE = 26
BATTLEEND = 27
BLANKMESSAGE = 28
CANCELMOVE = 29
CLAUSE = 30
DYNAMICINFO = 31
DYNAMICSTATS = 32
SPECTATING = 33
SPECTATORCHAT = 34
ALREADYSTATUSMESSAGE = 35
TEMPPOKECHANGE = 36
CLOCKSTART = 37
CLOCKSTOP = 38
RATED = 39
TIERSECTION = 40
ENDMESSAGE = 41
POINTESTIMATE = 42
MAKEYOURCHOICE = 43
AVOID = 44
REARRANGETEAM = 45
SPOTSHIFT = 46

def make_q_string(s):
	# QStrings are twice the size of python strings
	msg = struct.pack('>I', 2*len(s))
	msg += s.encode('utf_16_be')
	return msg

def make_py_string(s):
	size = struct.unpack('>I', s[:4])
	return s[4:4+size[0]].decode('utf_16_be')

class ShallowBattlePoke(object):

	def __init__(self, is_me, msg=None):
		if msg != None:
			# First time the poke was sent out
			self.poke_num = struct.unpack('>H', msg[:2])
			self.sub_num = struct.unpack('>B', msg[2])
			self.name = make_py_string(msg[3:])
			self.offset = 7 + len(self.name) # poke_num + sub_num + name_size + name
			if not is_me:
				self.name = "the foe's " + self.name
			self.hp_percent = struct.unpack('>B', msg[self.offset])
			self.full_status = struct.unpack('>I', msg[self.offset+1:self.offset+5])
			self.gender = struct.unpack('>B', msg[self.offset+5])
			self.shiny = struct.unpack('>B', msg[self.offset+6])
			self.level = struct.unpack('>B', msg[self.offset+7])
			self.offset += 8

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

class BattleConf(object):

	def __init__(self, msg):
		self.gen = struct.unpack('>B', msg[0])[0]
		self.mode = struct.unpack('>B', msg[1])[0]
		self.id_1 = struct.unpack('>I', msg[2:6])[0]
		self.id_2 = struct.unpack('>I', msg[6:10])[0]
		self.clauses = struct.unpack('>I', msg[10:14])[0]

def notify(msg):
	print msg

def construct_attack(attack):
	notify('Sent attack ' + str(attack))
	return struct.pack('>IBBBB', battle_id, me, 1, attack, opp)

def construct_switch(slot):
	return struct.pack('>IBBB', battle_id, me, 2, slot)

def construct_draw():
	return struct.pack('>IBB', battle_id, me, 5)

def recv_battle_cmd(msg):
	cmd = struct.unpack('>B', msg[0])[0]
	player = struct.unpack('>B', msg[1])[0]
	if cmd == SENDOUT:
		silent = struct.unpack('>B', msg[2])[0]
		from_spot = struct.unpack('>B', msg[3])[0]
		if (player == me):
			temp = my_team.pokes[0] # current poke is always in pos 0
			my_team.pokes[0] = my_team.pokes[from_spot]
			my_team.pokes[from_spot] = temp

		temp_poke = pokes[player][0]
		pokes[player][0] = pokes[player][from_spot]
		pokes[player][from_spot] = temp_poke
		if len(msg[4:]):
			# this is the first time you've seen it
			pokes[player][0] = ShallowBattlePoke((player == me), msg[4:])
		if not silent:
			notify('Player ' + str(player) + ' sent out ' + pokes[player][0].name + '!')
	elif cmd == SENDBACK:
		silent = struct.unpack('>B', msg[2])[0]
		if not silent:
			notify('Player ' + str(player) + ' called ' + pokes[player][0].name + ' back!')
	elif cmd == USEATTACK:
		attack = struct.unpack('>H', msg[2:4])[0]
		silent = struct.unpack('>B', msg[4])[0]
		if not silent:
			notify(pokes[player][0].name + ' used attack ' + str(attack) + '!')
	elif cmd == BEGINTURN:
		turn = struct.unpack('>I', msg[2:6])[0]
		notify('Start of turn ' + str(turn))
	elif cmd == KO:
		notify(pokes[player][0] + ' fainted!')
	elif cmd == HIT:
		num = struct.unpack('>B', msg[2])
		notify('Hit ' + str(num) + ' time' + 's!' if num > 1 else '!')
	elif cmd == EFFECTIVE:
		eff = struct.unpack('>B', msg[2])[0]
		if eff == 0:
			notify('It had no effect!')
		elif eff == 1 or eff == 2:
			notify("It's not very effective...")
		elif eff == 8 or eff == 16:
			notify("It's super effective!")
	elif cmd == CRITICALHIT:
		notify('A critical hit!')
	elif cmd == MISS:
		notify('The attack of ' + pokes[player][0].name + ' missed!')
	elif cmd == AVOID:
		notify(pokes[player][0].name + ' avoided the attack!')
	elif cmd == STATCHANGE:
		stat = struct.unpack('>B', msg[2])[0]
		boost = struct.unpack('>B', msg[3])[0]
		silent = struct.unpack('>B', msg[4])[0]
		if not silent:
			notify(pokes[player][0].name + "'s stat number " + str(stat) + \
			(' sharply ' if abs(boost) > 1 else '') + ('rose!' if boost > 0 else 'fell!'))
	elif cmd == FAILED:
		silent = struct.unpack('>B', msg[2])[0]
		if not silent:
			notify('But it failed!')
	elif cmd == NOOPPONENT:
		notify('But there was no target...')
	elif cmd == FLINCH:
		notify(pokes[player][0].name + ' flinched!')
	elif cmd == RECOIL:
		damaging = struct.unpack('>B', msg[2])[0]
		notify(pokes[player][0].name + ' is hit with recoil!' if damaging else ' had its energy drained!')
	elif cmd == STRAIGHTDAMAGE:
		damage = struct.unpack('>H', msg[2:4])[0]
		if player == me:
			notify(pokes[player][0].name + ' lost ' + str(damage) + ' HP!' + \
					' (' + str(damage * 100 / my_team.pokes[0].total_hp) + '% of its health)')
		else:
			notify(pokes[player][0].name + ' lost ' + str(damage) + '% of its health!')
	elif cmd == BATTLEEND:
		result = struct.unpack('>B', msg[2])[0]
		if result == 2: # It was a tie
			notify('The battle ended in a tie!')
		else:
			notify('Player ' + str(player) + ' won the battle!')
	elif cmd == MAKEYOURCHOICE:
		notify('Choose your destiny')
		s.send(construct_attack(random.randint(0,3)), poke_socket.BATTLEMESSAGE) # random attack!
	elif cmd == CHANGEHP:
		new_hp = struct.unpack('>H', msg[2:4])[0]
		if player == me:
			my_team.pokes[0].current_hp = new_hp
			pokes[player][0].hp_percent = new_hp * 100 / my_team.pokes[0].total_hp
		else:
			pokes[player][0].hp_percent = new_hp
		notify(pokes[player][0].name + "'s new hp " + ('percentage ' if player != me else '') + 'is ' + str(new_hp) + '!')
	elif cmd == CHANGEPP:
		move_num = struct.unpack('>B', msg[2])[0]
		new_pp = struct.unpack('>B', msg[3])[0]
		my_team.pokes[0].moves[move_num] = new_pp
		notify('Move ' + str(move_num) + 's new PP is ' + str(new_pp) + '!')
	else:
		print 'Command unimplemented: ' + str(cmd)
	

s = PokeSocket('188.165.249.120', 5080)
s.send(FullPlayerInfo('Twilio Client').serialize(), poke_socket.LOGIN); 

# Find a battle
while 1:
	flags = 2 # Only flag we want is forceSameTier
	msg = struct.pack('>I', flags)
	msg = struct.pack('>B', 200) # range
	msg = struct.pack('>B', 0) # Don't really know why this is needed
	s.send(msg, poke_socket.FINDBATTLE)

	while 1:
		msg = s.recv()
		cmd = struct.unpack('>B', msg[0])[0]
		if cmd == poke_socket.LOGIN:
			my_id = struct.unpack('>I', msg[1:5])[0]
		if cmd == poke_socket.ENGAGEBATTLE:
			battle_id = struct.unpack('>I', msg[1:5])[0]
			p1_id = struct.unpack('>I', msg[5:9])[0]
			p2_id = struct.unpack('>I', msg[9:13])[0]
			if p1_id == 0: # This is us!
				print 'Battle found!'
				print 'p1_id: ' + str(p1_id) + ' p2_id: ' + str(p2_id)
				bc = BattleConf(msg[13:])
				print 'my_id: ' + str(my_id) + ' bc.id_1: ' + str(bc.id_1) + ' bc.id_2: ' + str(bc.id_2)
				my_team = BattleTeam(msg[27:])
				battle = True
				pokes = []
				my_pokes = []
				opp_pokes = []
				pokes.append(my_pokes)
				pokes.append(opp_pokes)
				for i in range(6):
					pokes[0].append(ShallowBattlePoke(True))
					pokes[1].append(ShallowBattlePoke(False))
				if bc.id_1 == my_id:
					me = 0
					opp = 1
				else:
					me = 1
					opp = 0
		elif cmd == poke_socket.BATTLEMESSAGE:
			# Discard the first two ints, unneeded
			recv_battle_cmd(msg[9:])
	s.close()
