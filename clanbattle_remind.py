import base64
import os
import time
import traceback
from collections import defaultdict

from hoshino import aiorequests, config, util

from . import sv

try:
    import ujson as json
except:
    import json

logger = sv.logger

group_data = { }

async def clanbattle_check():
	url = 'https://mahomaho-insight.info/cached/gameevents.json'
	#header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
	resp = await aiorequests.get(
		url,
		#header,
		timeout=10,
		)
	res = await resp.json()
	cn = res['cn']
	check = {}
	i = 0
	if cn:
		for i in range(len(cn)):
			now = time.time()
			startTime = int(time.mktime(time.strptime(cn[i]["start"], "%Y/%m/%d %H:%M")))
			endTime = int(time.mktime(time.strptime(cn[i]["end"], "%Y/%m/%d %H:%M")))
			if (cn[i]['category'] == "clanbattle" and endTime >= now):
				begin = startTime - now
				over = endTime - now
				check = {"title":cn[i]["title"],"start":cn[i]["start"],"end":cn[i]["end"],"begin":begin,"over":over}
				logger.debug(f"get clanbattle time {check=}")
				break
			else:
				continue
	return check

# def load_clan_setting(group_id):
	# config_file = os.path.join(os.path.dirname(__file__), 'config', f'{group_id}.json')
	# config = None
	# if not os.path.exists(config_file):
		# group_config[group_id]['info'] = '配置文件不存在'
		# return 1
	# try:
		# with open(config_file, encoding='utf8') as f:
			# config = json.load(f)
	# except:
		# traceback.print_exc()
	# if not config or len(config) == 0:
		# group_config[group_id]['info'] = '配置文件格式错误'
		# return 1
	# if not group_id in group_config:
		# group_config[group_id] = {}

def load_clan_data(group_id):
	config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
	if os.path.exists(config_file):
		try:
			with open(config_file, encoding='utf8') as f:
				group_data[group_id] = json.load(f)
		except:
			traceback.print_exc()
			
	if not group_id in group_data:
		group_data[group_id] = {}
	
	if 'leader_id' not in group_data[group_id]:
		group_data[group_id]['leader_id'] = 0
	if 'mention_leader' not in group_data[group_id]:
		group_data[group_id]['mention_leader'] = False
	

def save_clan_data(group_id):
	if group_id not in group_data:
		return
	config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
	try:
		with open(config_file, 'w', encoding='utf8') as f:
			json.dump(group_data[group_id], f, ensure_ascii=False, indent=2)
	except:
		traceback.print_exc()
	with open(config_file, 'w', encoding='utf8') as f:
		json.dump(group_data[group_id], f, ensure_ascii=False, indent=2)
		
def get_clan_list():
	group_list = []
	path = os.path.join(os.path.dirname(__file__), 'config')
	list = os.listdir(path)
	for fn in list:
		group = fn.split('.')[0]
		if group.isdigit():
			group_list.append(str(group))
	return group_list
	
def mention_check(group_id):
	if group_data[group_id]['mention_leader']:
		return True
	else:
		return False
	
async def mention_leader(group_id, mention: bool = False):
	load_clan_data(group_id)
	if 'mention_leader' not in group_data[group_id]:
		group_data[group_id]['mention_leader'] = False
	group_data[group_id]['mention_leader'] = mention
	save_clan_data(group_id)
	
async def remove_bind(group_id):
	if ('leader_id' not in group_data[group_id] or group_data[group_id]['leader_id'] == 0):
		return
	else:
		group_data[group_id]['leader_id'] = 0
	save_clan_data(group_id)

async def bind_leader(group_id, leader_id):
	load_clan_data(group_id)
	if 'leader_id' not in group_data[group_id]:
		group_data[group_id]['leader_id'] = 0
	await remove_bind(group_id)
	group_data[group_id]['leader_id'] = leader_id
	save_clan_data(group_id)
	return 0
	
async def get_leader(group_id):
	load_clan_data(group_id)
	leader_id = 0
	if 'leader_id' not in group_data[group_id]:
		return 0
	leader_id = group_data[group_id]['leader_id']
	return leader_id