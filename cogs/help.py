import discord
from discord.ext import commands
from discord.ext.menus import MenuPages, ListPageSource

def syntax(command):
  cmd_and_aliases = "|".join([str(command), *command.aliases])
  params = []

  for key, value in command.params.items():
    if key not in ("self", "ctx"):
      params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

  params = " ".join(params)
  
  return f"`{cmd_and_aliases} {params}`"

class HelpMenu(ListPageSource):
  def __init__(self, ctx, data):
    self.ctx = ctx
    super().__init__(data, per_page=5)

  async def write_page(self, menu, fields=[]):
    offset = (menu.current_page*self.per_page) + 1
    len_data = len(self.entries)
    embed = discord.Embed(title="Help", description="Welcome to the help dialog!", colour=self.ctx.author.colour)
    embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
    embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands")
    for name, value in fields:
      embed.add_field(name=name, value=value, inline=False)
    return embed

  async def format_page(self, menu, entries):
    fields = []
    for entry in entries:
      fields.append((entry.description or "None", syntax(entry)))

    return await self.write_page(menu, fields)

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.remove_command("help")

  async def cmd_help(self, ctx, command):
    embed = discord.Embed(title=f"Help with `{command}`", description=syntax(command), colour=ctx.author.colour)
    if command.description == "":
      desc = "None"
    else:
      desc = command.description
    embed.add_field(name="Command description", value=desc)
    await ctx.send(embed=embed)

  @commands.Cog.listener()
  async def on_ready(self):
    print("help cog ready!")

  @commands.command(name="help", description="Shows this message")
  async def show_help(self, ctx, cmd: str=None):
    try:
      if cmd is None:
        menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)), clear_reactions_after=True, timeout=60.0)
        await menu.start(ctx)
      else:
        if (command := discord.utils.get(self.bot.commands, name=cmd)):
          await self.cmd_help(ctx, command)
        else:
          await ctx.send(f"There is no command called {cmd}")
    except Exception as e:
      await ctx.send(e)

def setup(bot):
  bot.add_cog(Help(bot))