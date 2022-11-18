class ChannelLogger():

    def __init__(self):

        import os,logging,sys,datetime
        self.os=os
        self.sys=sys
        self.datetime=datetime

        self.format="%s,%s,%s,%s\n"

        #{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}

        self.cd = f"./data/channellogs/"

    def logmsg(self,ctx):
        p=self.cd+str(ctx.guild.id)+"/"

        if not self.os.path.isdir(p):
            self.os.mkdir(p)
            with open(p+"name","w",encoding="utf-8") as f: f.write(ctx.guild.name+"\n")

        else:
            with open(p+"name","rb") as f:
                try:
                    f.seek(-2, self.os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, self.os.SEEK_CUR)
                except OSError:
                    f.seek(0)
                lastLine = f.readline().decode()
                f.close()
            if lastLine!=ctx.guild.name+"\n":
                with open(p+"name","a",encoding="utf-8") as f: f.write(ctx.guild.name+"\n")

        p=p+str(ctx.channel.id)+"/"

        if not self.os.path.isdir(p):
            self.os.mkdir(p)
            with open(p+"name","w",encoding="utf-8") as f: f.write(ctx.channel.name+"\n")

        else:
            with open(p+"name","rb") as f:
                try:
                    f.seek(-2, self.os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, self.os.SEEK_CUR)
                except OSError:
                    f.seek(0)
                lastLine = f.readline().decode()
                f.close()
            if lastLine!=ctx.channel.name+"\n":
                with open(p+"name","a",encoding="utf-8") as f: f.write(ctx.channel.name+"\n")

        p=p+"log.csv"

        if not self.os.path.exists(p):
            with open(p,"a",encoding="utf-8") as f:
                f.write("Time,Author ID,Author Name,Message")

                f.write(self.format%(self.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ctx.author.id, ctx.author.name+"#"+ctx.author.discriminator, ctx.content))

        else:
            with open(p,"a",encoding="utf-8") as f:
                f.write(self.format%(self.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ctx.author.id, ctx.author.name+"#"+ctx.author.discriminator, ctx.content))


if __name__ == "__main__":
    raise Exception(
        "This module is to be used in conjunction with the SchwimbleGromp application and not as a standalone module.")
