import discord
from discord.ext import tasks
import asyncio
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente de um arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO ---
# O token agora é carregado da variável de ambiente 'DISCORD_TOKEN'.
TOKEN = os.getenv("DISCORD_TOKEN")
# --------------------

# Define as permissões (Intents) necessárias para o bot funcionar.
# Ele precisa ver os servidores (guilds) e o estado dos canais de voz (voice_states).
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

# Cria a instância do bot.
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    """
    Esta função é chamada quando o bot se conecta com sucesso ao Discord.
    """
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID do Bot: {bot.user.id}')
    print('-----------------------------------------')
    # Inicia a tarefa em segundo plano para verificar os canais.
    check_voice_channels.start()

@tasks.loop(seconds=10)
async def check_voice_channels():
    """
    Tarefa que roda em loop para verificar e entrar no canal de voz mais populoso.
    """
    try:
        # Itera sobre todos os servidores (guilds) em que o bot está.
        for guild in bot.guilds:
            target_channel = None
            max_members = 0

            # Encontra o canal de voz com o maior número de membros.
            # Ignora canais AFK (de inatividade).
            for channel in guild.voice_channels:
                if channel != guild.afk_channel and len(channel.members) > max_members:
                    max_members = len(channel.members)
                    target_channel = channel

            # Pega a conexão de voz atual do bot neste servidor (se houver).
            voice_client = guild.voice_client

            # Se um canal com pessoas foi encontrado...
            if target_channel:
                # Se o bot não está conectado ou está em um canal diferente...
                if voice_client is None:
                    print(f"[{guild.name}] Conectando ao canal: {target_channel.name} ({max_members} pessoa(s))")
                    await target_channel.connect()
                elif voice_client.channel != target_channel:
                    print(f"[{guild.name}] Movendo para o canal: {target_channel.name} ({max_members} pessoa(s))")
                    await voice_client.move_to(target_channel)
            # Se nenhum canal com pessoas foi encontrado e o bot está conectado...
            elif voice_client is not None:
                print(f"[{guild.name}] Todos os canais estão vazios. Desconectando.")
                await voice_client.disconnect()

    except Exception as e:
        print(f"Ocorreu um erro na tarefa de verificação: {e}")

@check_voice_channels.before_loop
async def before_check():
    """
    Espera o bot estar totalmente pronto antes de iniciar o loop.
    """
    await bot.wait_until_ready()

# Inicia a execução do bot.
if not TOKEN:
    print("ERRO: O token do bot não foi encontrado na variável de ambiente 'DISCORD_TOKEN'.")
    print("Crie um arquivo .env na mesma pasta do script e adicione a linha: DISCORD_TOKEN='seu_token_aqui'")
else:
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("\nERRO: Token do bot inválido.")
        print("Por favor, verifique se o token no seu arquivo .env está correto.")
    except Exception as e:
        print(f"Ocorreu um erro ao tentar iniciar o bot: {e}")
