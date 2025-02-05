import random
from uuid import UUID

from click import style
from fastapi import WebSocket

from anagrams.core.player import Player

from ..core.dictionary import Dictionary, same_root
from ..core.game import AnagramStrategy, Game
from .log import get_logger
from .messages import Message

GameID = str


def game_logger(game_id: str):
    return get_logger(style(game_id, fg="cyan", bold=True))


class GameManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}
        self.known_clients: list[UUID] = []
        self.games: dict[GameID, Game] = {}
        self.player_games: dict[UUID, GameID] = {}
        self.dictionary = Dictionary.load_from_file()

    async def connect(self, websocket: WebSocket, client_id: UUID):
        """Connect a client to the server."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if client_id not in self.known_clients:
            self.known_clients.append(client_id)
        if client_id in self.player_games:
            await self.broadcast_game_state(self.player_games[client_id])

    def disconnect(self, client_id: UUID):
        """Disconnect a client from the server."""
        if client_id in self.active_connections:
            self.active_connections.pop(client_id)

    def connected(self, client_id: UUID):
        """Check if a player is connected."""
        return client_id in self.active_connections

    async def send(self, message: Message, client_id: UUID):
        """Send a client a message."""
        if self.connected(client_id):
            await self.active_connections[client_id].send_json(message.content)

    async def send_err(self, client_id: UUID, err_type: str, description: str):
        """Send a client an error message."""
        await self.send(Message.error(err_type, description), client_id)

    def connected_clients_in_game(self, game_id: GameID):
        """Get a list of clients in a game that are currently connected."""
        return [
            cid
            for cid, gid in self.player_games.items()
            if gid == game_id and self.connected(cid)
        ]

    async def broadcast_game_state(self, game_id: GameID):
        """Broadcast the game state to all the clients in a game."""
        game = self.games[game_id]
        connected = self.connected_clients_in_game(game_id)
        for cid in connected:
            await self.active_connections[cid].send_json(
                Message.game_state(cid, game, connected, game_id).content,
            )

    async def handle_message(self, message: Message, client_id: UUID):
        """Handle an incoming message from a client."""
        match message.action:
            case "join":
                await self.handle_join(
                    client_id, message["game_id"].strip().upper(), message["name"]
                )
            case "start":
                await self.handle_start(client_id, message["name"])
            case "word":
                await self.handle_word(client_id, message["word"])
            case "letter":
                await self.handle_letter(client_id)
            case "kick":
                await self.handle_kick(client_id, int(message["player_index"]))

    async def handle_join(self, client_id: UUID, game_id: GameID, name: str):
        """Handle a client's request to join a game."""
        name = name.strip()
        if len(name) == 0:
            await self.send_err(client_id, "join_fail", "Please enter your name.")
            return
        game_id = game_id.strip()
        if len(game_id) == 0:
            await self.send_err(client_id, "join_fail", "Please enter a game ID.")
            return
        if game_id not in self.games:
            await self.send_err(client_id, "join_fail", f"Game {game_id} not found.")
            return

        game = self.games[game_id]

        if any(p.name == name for p in game.players.values()):
            await self.send_err(client_id, "join_fail", "That name is taken!")
            return

        self.player_games[client_id] = game_id
        player = Player(client_id, name, [])
        game.add_player(player)
        game_logger(game_id).info(f"Added {player.name} to the game")
        await self.broadcast_game_state(game_id)

    async def handle_start(self, client_id: UUID, name: str):
        """Handle a client's request to start a new game."""

        name = name.strip()
        if len(name) == 0:
            await self.send_err(client_id, "start_fail", "Please enter your name.")
            return

        def random_game_id() -> GameID:
            return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))

        game_id = random_game_id()
        while game_id in self.games:
            game_id = random_game_id()

        self.games[game_id] = Game()
        game_logger(game_id).info("Game created")
        await self.handle_join(client_id, game_id, name)

    async def handle_word(self, client_id: UUID, word: str):
        game_id = self.player_games[client_id]
        game = self.games[game_id]

        word = word.lower().strip()

        if word not in self.dictionary:
            await self.send_err(
                client_id,
                "invalid_word",
                f"{word.title()} is not in the dictionary.",
            )
            return

        strategies = game.get_anagram_strategies(word)
        if len(strategies) == 0:
            await self.send_err(
                client_id,
                "invalid_word",
                f"{word} could not be made from the current tiles.",
            )
            return

        def has_same_root(strategy: AnagramStrategy):
            for _, w in strategy:
                if len(w) > 1 and same_root(word, w):
                    return w
            return None

        while len(strategies) > 0:
            strategy = strategies[0]
            w = has_same_root(strategy)
            if w is None:
                break
            strategies.pop(0)
        else:
            await self.send_err(
                client_id,
                "invalid_word",
                f"{word} and {w} have the same root.",
            )
            return

        # TODO let the user select the strategy
        game.execute_anagram_strategy(strategy)
        player = game.players[client_id]
        player.words.append(word)
        log_message = f"{player.name} combined "
        log_message += ", ".join([w.upper() for _, w in strategy[:-1]])
        if len(strategy) > 2:  # oxford comma!
            log_message += ","
        log_message += f" and {strategy[-1][1].upper()} to make {word.upper()}"  # type: ignore -- pylance is confused??

        game_logger(game_id).info(log_message)
        await self.broadcast_game_state(game_id)

    async def handle_letter(self, client_id: UUID):
        game_id = self.player_games[client_id]
        game = self.games[game_id]

        if game.turn is not None and game.turn.id == client_id:
            game.new_letter(temperature=0.5)
            game.next_turn()
            await self.broadcast_game_state(game_id)

    async def handle_kick(self, client_id: UUID, player_index: int):
        game_id = self.player_games[client_id]
        game = self.games[game_id]

        # only the host can kick other players
        if game.turn_order[0] == client_id:
            remove_player_id = game.turn_order[player_index]
            remove_player = game.players[remove_player_id]
            game.remove_player(remove_player_id)
            game_logger(game_id).info(f"Removed {remove_player.name} from the game")
            self.player_games.pop(remove_player_id)
            if len(game.players) == 0:
                self.games.pop(game_id)
                game_logger(game_id).info("Game deleted (no more players)")
            else:
                await self.broadcast_game_state(game_id)
            await self.send(Message.leave_game(), remove_player_id)
