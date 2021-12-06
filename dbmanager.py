import sqlalchemy


class DBManager:
    @staticmethod
    def __connect():
        connection_string = 'postgresql://postgres:postgres@localhost:5432/player_stats'
        return sqlalchemy.create_engine(connection_string)

    @staticmethod
    def record_win(winner: str, loser: str) -> None:
        engine = DBManager.__connect()

        query_winner = """INSERT INTO winloss.players (name, wins)
                    VALUES (:name, 1) 
                    ON CONFLICT (name) DO UPDATE SET 
                    name=EXCLUDED.name, wins = winloss.players.wins + 1"""

        query_loser = """INSERT INTO winloss.players (name, losses)
                    VALUES (:name, 1) 
                    ON CONFLICT (name) DO UPDATE SET 
                    name=EXCLUDED.name, losses = winloss.players.losses + 1"""

        engine.connect().execute(sqlalchemy.text(query_winner), name=winner)
        engine.connect().execute(sqlalchemy.text(query_loser), name=loser)

    @staticmethod
    def record_draw(p1: str, p2: str) -> None:
        engine = DBManager.__connect()

        query_winner = """INSERT INTO winloss.players (name, draws)
                            VALUES (:name, 1) 
                            ON CONFLICT (name) DO UPDATE SET 
                            name=EXCLUDED.name, draws = winloss.players.draws + 1"""

        engine.connect().execute(sqlalchemy.text(query_winner), name=p1)
        engine.connect().execute(sqlalchemy.text(query_winner), name=p2)

