import asyncio
import random

# Implements a simple finite state machine for the game protocol.
class GameProtocol(asyncio.Protocol):
    def __init__(self, game_server):
        self.game_server = game_server
        self.transport = None
        self.word = ""
        self.hints = []
        self.current_hint_index = 0
        self.attempts = 0
        self.state = "INIT"

    def connection_made(self, transport):
        self.transport = transport
        self.game_server.register_game(self)
        self.send_message("welcome")

    def connection_lost(self, exc):
        # Let's not leak memory if the connection is closed in any way
        self.game_server.unregister_game(self)

    def data_received(self, data):
        message = data.decode().strip()
        if self.state == "INIT":
            self.handle_password(message)
        elif self.state == "PLAYING":
            self.handle_guess(message)

    def handle_password(self, password):
        if password != self.game_server.password:
            self.send_message("wrong_password")
            self.transport.close()
        else:
            self.state = "PLAYING"
            self.word, self.hints = random.choice(self.game_server.words_and_hints)
            self.send_message("authenticated")
            self.send_hint()
    
    def send_hint(self):
        if self.current_hint_index < len(self.hints):
            self.send_message(f"hint:{self.hints[self.current_hint_index]}")
            self.current_hint_index += 1
        else:
            self.send_message("hint_exhausted")

    def handle_guess(self, guess):
        self.attempts += 1
        if guess.lower() == self.word.lower():
            self.send_message(f"guess_correct")
            self.end_game()
        else:
            self.send_hint()

    def send_message(self, message):
        self.transport.write(f"{message}\n".encode())

    def end_game(self):
        self.transport.close()

    def to_dict(self):
        peername = self.transport.get_extra_info("peername")
        return {
            "word": self.word,
            "hints": self.hints,
            "current_hint_index": self.current_hint_index,
            "attempts": self.attempts,
            "state": self.state,
            "ip": peername[0] if peername else None,
            "port": peername[1] if peername else None,
        }


class GameServer:
    def __init__(self, password):
        self.active_games = set() # O(1) insertion/removal
        self.password = password
        self.words_and_hints = [
            ("pytorch", [
                "It's like TensorFlow, but if you know, you know.",
                "If you're serious about deep learning, you probably use this (unless you use Jax).",
                "Numpy but on GPUs"
            ]),
            ("Rust", [
                "It's not just iron oxide, it's also a system programming language.",
                "If you're tired of memory leaks, this might be your new best friend.",
            ])
        ]
        
    def register_game(self, game_protocol):
        self.active_games.add(game_protocol)

    def unregister_game(self, game_protocol):
        self.active_games.discard(game_protocol)

    def create_protocol(self):
        return GameProtocol(self)
