from uuid import UUID

from ..core.game import Game


class Message:
    def __init__(self, action: str, **kwargs) -> None:
        self.content = dict(action=action, **kwargs)

    def __repr__(self):
        return f"Message({', '.join(f'{k}={v}' for k, v in self.content.items())})"

    def __getitem__(self, key: str):
        return self.content[key]

    @property
    def action(self):
        return self.content["action"]

    @classmethod
    def set_cookie(cls, name: str, value: str):
        return Message(action="set_cookie", name=name, value=value)

    @classmethod
    def error(cls, err_type: str, description: str):
        return Message(action="error", err_type=err_type, description=description)

    @classmethod
    def leave_game(cls):
        return Message(action="leave_game")

    @classmethod
    def game_state(
        cls, client_id: UUID, game: Game, connected: list[UUID], game_id: str
    ):
        ordered_players = [
            (
                game.players[pid],
                pid == client_id,
                pid in connected,
            )
            for pid in game.turn_order
        ]
        return Message(
            action="game_state",
            players=[
                {
                    "name": p.name,
                    "score": p.score,
                    "words": p.words,
                    "turn": p == game.turn,
                    "you": you,
                    "connected": conn,
                }
                for p, you, conn in ordered_players
            ],
            letter_pool=game.letter_pool,
            game_id=game_id,
        )
