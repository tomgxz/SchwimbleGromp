import datetime

def currentCooldownTime(): return str(datetime.datetime.now())
def cooldownStrToObj(x): return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
def cooldownDiff(a,b): return (a-b).total_seconds()
