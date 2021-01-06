import nonebot
import hoshino
import aiocqhttp
import asyncio
import random
import os
from datetime import datetime
from hoshino import Service, R, priv
from hoshino.typing import *
from hoshino.util import FreqLimiter, concat_pic, pic2b64, silence
from nonebot import NoneBot
from nonebot import MessageSegment as ms
from aiocqhttp import event
import time
import itertools
from datetime import datetime
import pytz
try:
    import ujson as json
except:
    import json

sv_help = '''
[会战检查] 查看会战倒计时
'''.strip()
sv = Service('clanbattle_remind', help_=sv_help, bundle='pcr查询')

from . import clanbattle_remind

I = ('会战','公会战')
J = ('什么时候','啥时候','几时','还有多久','还有几天')
i = 0
j = 0
A = []
for i in I:
	for j in J:
		a = i + j
		b = j + i
		A.append(a)
		A.append(b)
		
aliases = tuple(A)

@sv.on_prefix(aliases)
async def clanbattleTimecheck(bot, ev: CQEvent):
	check = await clanbattle_remind.clanbattle_check()
	title = check["title"]
	start = check["start"]
	end = check["end"]
	begin = int(check["begin"])
	over = int(check["over"])
	if begin > 0:
		day = int(begin/(60*60*24))
		hour = int((begin/3600)-day*24)
		minute = int((begin/60)-hour*60-day*60*24)
		second = int(begin-minute*60-hour*3600-day*24*60*60)
		msg = f'{title}\n开始于 {start}\n还剩余 {day}天{hour}时{minute}分{second}秒'
		await bot.finish(ev, msg)
	else:
		day = int(over/(60*60*24))
		hour = int((over/3600)-day*24)
		minute = int((over/60)-hour*60-day*60*24)
		second = int(over-minute*60-hour*3600-day*24*60*60)
		msg = f'{title}已经开始，大家请加油！\n本次会战将在 {end}结束\n还剩余 {day}天{hour}时{minute}分{second}秒'
		await bot.finish(ev, msg)

#这里本来想做成时间可调，但是发现没办法
#_config_file = os.path.join(os.path.dirname(__file__), 'config.json')
#remind_hour = 0
#remind_minute = 0
#time_setting = {}
#try:
	#with open(_config_file, encoding='utf8') as f:
		#time_setting = json.load(f)
#except FileNotFoundError as e:
	#sv.logger.warning('group_pool_config.json not found')
#time_setting = {'hour': 5, 'minute': 0}

#def dump_config():
	#with open(_config_file, 'w', encoding='utf8') as f:
		#json.dump(time_setting, f, ensure_ascii=False)

#remind_hour = time_setting['hour']
#remind_minute = time_setting['minute']

@sv.on_prefix('会战提醒设置')
async def clanbattle_remind_setting(bot, ev: CQEvent):
	is_admin = priv.check_priv(ev, priv.ADMIN)
	msg = ''
	group_id = ev.group_id
	uid = ev.user_id
	args = ev.message.extract_plain_text().split()
	if len(args) == 0:
		msg = f'请在后面输入指令\n提醒/不提醒会长'
	#elif args[0] == '时间':
		#if args[1] and args[1].isdigit():
			#remind_hour = int(args[1])
			#time_setting['hour'] = int(args[1])
		#else:
			#msg = f'请输入合法的参数'
		#if args[2] and args[2].isdigit():
			#remind_minute = int(args[2])
			#time_setting['minute'] = int(args[2])
		#else:
			#msg = f'请输入合法的参数'
		#msg = f'提醒时间设置完毕，将于每日{remind_hour}时{remind_minute}分提醒'
		#try:
			#with open(_config_file, 'w', encoding='utf8') as f:
				#json.dump(time_setting, f, ensure_ascii=False)
		#except:
			#traceback.print_exc()
	elif args[0] == '提醒会长':
		await clanbattle_remind.mention_leader(group_id, mention = True)
		msg = f'提醒会长已开启'
	elif args[0] == '不提醒会长':
		await clanbattle_remind.mention_leader(group_id, mention = False)
		msg = f'提醒会长已关闭'
	await bot.finish(ev, msg)

@sv.scheduled_job('cron',hour=8, minute=30)
async def clanbattleDaycall():
	check = await clanbattle_remind.clanbattle_check()
	title = check["title"]
	start = check["start"]
	end = check["end"]
	begin = int(check["begin"])
	over = int(check["over"])
	msg = ''
	if begin > 0:
		day = int(begin/(60*60*24))
		if day < 4		:
			hour = int((begin/3600)-day*24)
			minute = int((begin/60)-hour*60-day*60*24)
			second = int(begin-minute*60-hour*3600-day*24*60*60)
			bot = nonebot.get_bot()
			glist = await sv.get_enable_groups()
			for gid, selfids in glist.items():
				msg = f'今天也是充满希望的一天，大家早安，{name}在此提醒各位\n{title}\n开始于 {start}\n还剩余 {day}天{hour}时{minute}分{second}秒\n{ms.at(await clanbattle_remind.get_leader(gid))}人招齐了吗？在农场的各位回来了吗？可千万别忘记只有三天会战就开始了哦！'
				if (await clanbattle_remind.get_leader(gid) == 0 or not clanbattle_remind.mention_check(gid)):
					msg = f'今天也是充满希望的一天，大家早安，{name}在此提醒各位\n{title}\n开始于 {start}\n还剩余 {day}天{hour}时{minute}分{second}秒'
				try:
					await asyncio.sleep(0.2)
					await bot.send_group_msg(self_id=random.choice(selfids), group_id=gid, message=msg)
					l = len(glist.items())
					sv.logger.info(f"群{gid} 投递成功 共{l}条消息")
				except Exception as e:
					sv.logger.error(f"群{gid} 投递失败：{type(e)}")
					sv.logger.exception(e)
			#await sv.broadcast(msg, 'clanbattleDaycall', 0.2)
		elif day < 7:
			hour = int((begin/3600)-day*24)
			minute = int((begin/60)-hour*60-day*60*24)
			second = int(begin-minute*60-hour*3600-day*24*60*60)
			msg = f'今天也是充满希望的一天，大家早安，{name}在此提醒各位\n{title}\n开始于 {start}\n还剩余 {day}天{hour}时{minute}分{second}秒'
			await sv.broadcast(msg, 'clanbattleDaycall', 0.2)
	else:
		day = int(over/(60*60*24))
		hour = int((over/3600)-day*24)
		minute = int((over/60)-hour*60-day*60*24)
		second = int(over-minute*60-hour*3600-day*24*60*60)
		msg = f'今天也是充满希望的一天，各位辛苦了，{name}在此提醒各位\n{title}已经开始，大家请加油！\n本次会战将在 {end}结束\n还剩余 {day}天{hour}时{minute}分{second}秒'
		await sv.broadcast(msg, 'clanbattleDaycall', 0.2)

@sv.on_prefix('设置会长')
async def set_clan(bot, ev:CQEvent):
	is_admin = priv.check_priv(ev, priv.ADMIN)
	msg = ''
	uid = ev.user_id
	group_id = ev.group_id
	target_id = 0
	args = ev.message.extract_plain_text().split()
	if len(args) != 0 and args[0].isdigit() and int(args[0]) >= 10000:
		target_id = int(args[0])
	for m in ev.message:
		if m.type == 'at' and m.data['qq'] != 'all':
			target_id = int(m.data['qq'])
	if target_id == 0:
		msg = '需要附带会长QQ，请在命令后@会长'
	elif is_admin:
		await clanbattle_remind.bind_leader(group_id, target_id)
		msg = f'已成功绑定QQ：{target_id}为会长'
	else:
		msg = '权限不足'
	await bot.finish(ev, msg)

