import uvicorn
import asyncio
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from game_server import GameServer

game_server = GameServer("secret_password")
app = FastAPI()

# Status endpoint
@app.get('/', response_class=HTMLResponse)
async def main():
    active_games_html = "<html><body><h3>Active Games</h3><ul>"
    for game in game_server.active_games:
        game_info = game.to_dict()
        active_games_html += f"<li>IP: {game_info['ip']}, Port: {game_info['port']}, Word: {game_info['word']}, Hints: {', '.join(game_info['hints'])}, Attempts: {game_info['attempts']}, State: {game_info['state']}</li>"
    active_games_html += "</ul></body></html>"
    return HTMLResponse(content=active_games_html)

async def run_game_server(host, port):
    loop = asyncio.get_event_loop()
    server = await loop.create_server(game_server.create_protocol, host, port)

    addr = server.sockets[0].getsockname()
    print(f"Game server running on {addr}")

    async with server:
        await server.serve_forever()

async def run_status_server(host, port):
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

async def main(game_host, game_port, status_host, status_port):
    game_task = asyncio.create_task(run_game_server(game_host, game_port))
    status_task = asyncio.create_task(run_status_server(status_host, status_port))
    
    await asyncio.gather(game_task, status_task)

if __name__ == "__main__":
    asyncio.run(main('localhost', 8888, 'localhost', 8000))