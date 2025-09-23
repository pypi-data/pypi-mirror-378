# coding=utf-8
"""
Example script to fetch a player from the player registry
"""
from mhanndalorian_bot import Registry

mbot = Registry(api_key="YOUR_API_KEY", allycode="YOUR_ALLYCODE", discord_id="PLAYER_DISCORD_ID")

player_result = mbot.fetch_player(allycode="PLAYER_ALLYCODE")

if player_result is not None:
    print(player_result)
else:
    print("Player not found")
