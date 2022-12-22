import pandas as pd
from pathlib import Path
import numpy as np
import utils
import datetime

DATA_RAW_PATH = Path("data/raw/")


def fuse_tables(cursor):

    utils.run_sql_command(cursor, "DROP VIEW IF EXISTS anime_songs")
    command = """
    CREATE VIEW anime_songs AS
    SELECT anime.id as animeId, anime.annid, anime.anime_name as animeName, songs.id as songId, songs.name as songName, songs.artist as songArtist, songs.type as songType, songs.type_number as songNumber, songs.difficulty as songDifficulty
    FROM songs
    LEFT JOIN anime ON songs.anime_id = anime.id;
    """
    utils.run_sql_command(cursor, command)

    utils.run_sql_command(cursor, "DROP VIEW IF EXISTS players_answers_tmp")
    command = """
    CREATE VIEW players_answers_tmp AS
    SELECT player_answers.id, players.id as playerId, players.name as playerName, player_answers.ranked_song_id as rankedSongId, player_answers.anime_id as animeId, player_answers.guess_time as guessTime, player_answers.if_correct as isCorrect
    FROM player_answers
    LEFT JOIN players ON players.id = player_answers.player_id;
    """
    utils.run_sql_command(cursor, command)

    utils.run_sql_command(cursor, "DROP VIEW IF EXISTS rankeds_games")
    command = """
    CREATE VIEW rankeds_games AS
    SELECT ranked_games.id as rankedId, ranked_games.date, ranked_games.region, ranked_songs.id as rankedSongId, ranked_songs.song_number as rankedSongNumber, ranked_songs.song_id as songId, ranked_songs.start_time as startTime, ranked_songs.correct_count as correctCount, ranked_songs.active_players as activePlayers
    FROM ranked_songs
    LEFT JOIN ranked_games ON ranked_games.id = ranked_songs.ranked_game_id;
    """
    utils.run_sql_command(cursor, command)

    utils.run_sql_command(cursor, "DROP VIEW IF EXISTS players_answers")
    command = """
    CREATE VIEW players_answers AS
    SELECT rankeds_games.rankedId, rankeds_games.date, rankeds_games.region, rankeds_games.rankedSongId, rankeds_games.rankedSongNumber, rankeds_games.songId, rankeds_games.startTime, rankeds_games.correctCount, rankeds_games.activePlayers,
    players_answers_tmp.playerId, players_answers_tmp.playerName, players_answers_tmp.animeId, players_answers_tmp.guessTime, players_answers_tmp.isCorrect
    FROM players_answers_tmp
    LEFT JOIN rankeds_games ON rankeds_games.rankedSongId = players_answers_tmp.rankedSongId;
    """
    utils.run_sql_command(cursor, command)


def process_top_player_df(players_answers, start_date, end_date, nbDisplay):

    players_answers = players_answers[players_answers.date >= str(start_date)]
    players_answers = players_answers[players_answers.date <= str(end_date)]

    df = (
        players_answers.groupby(["date", "region", "playerName"])
        .isCorrect.mean()
        .reset_index()
    )

    grouped_df = players_answers.groupby(["date", "region", "playerName"])

    df["score"] = grouped_df.isCorrect.sum().values
    df["total"] = grouped_df.isCorrect.count().values

    topScore = (
        df.groupby("playerName")
        .agg({"score": "max", "date": "first", "region": "first"})
        .sort_values(by=["score"], ascending=False)
        .reset_index()
        .iloc[:nbDisplay]
    )
    topScore.index = np.arange(1, len(topScore) + 1)

    # Group the data by playerName and region, and calculate the sum of the total column
    df_grouped = df.groupby(["playerName", "region"], as_index=False).total.sum()

    # Group the data by playerName and calculate the sum of the total column
    df_totals = df_grouped.groupby("playerName", as_index=False).total.sum()

    # Merge df_totals with df_grouped on the playerName column
    df_merged = df_totals.merge(df_grouped, on="playerName", how="left")

    # Sort the data by total_x in descending order and reset the index
    df_merged = df_merged.sort_values(by=["total_x"], ascending=False).reset_index(
        drop=True
    )

    # Select the top nb_display rows
    head_id = df_merged[df_merged.playerName != df_merged.playerName.shift()].index[
        nbDisplay + 2
    ]
    topTime = df_merged.iloc[3:head_id].rename(columns={"total_y": "nbSongs"})

    return topScore, topTime


def count_unique_players(x):
    return len(x.playerName.unique())


def mean_correct_guess_rate(x):

    eligible = x.groupby("playerName").isCorrect.count().reset_index(name="songCount")
    eligible = eligible[eligible.songCount >= 850]

    pGuessRate = x.groupby("playerName").isCorrect.mean().reset_index(name="guessRate")
    pGuessRate = pGuessRate[pGuessRate.playerName.isin(eligible.playerName)].apply(
        lambda x: x * 100
    )

    return (
        pGuessRate.sort_values(by=["guessRate"], ascending=False)
        .head(150)
        .guessRate.mean()
        .round(2)
    )


def process_top_regions(players_answers, start_date, end_date):

    players_answers = players_answers[players_answers.date >= str(start_date)]
    players_answers = players_answers[players_answers.date <= str(end_date)]

    # Create a dataframe with the total number of unique players per region
    top_regions = (
        players_answers.groupby("region")
        .apply(count_unique_players)
        .rename("playerCount")
        .reset_index()
    )

    # Create a dataframe with the mean number of unique players per date and region
    average_players = (
        players_answers.groupby(["date", "region"])
        .apply(count_unique_players)
        .rename("playerCount")
        .reset_index()
    )

    # Create a dataframe with the mean player count per region
    mean_player_count = (
        average_players.groupby("region")
        .playerCount.mean()
        .round()
        .reset_index(name="playerAverage")
    )

    # Create a dataframe with the mean correct guess rate for the top 100 players of each region
    mean_guess_rates = (
        players_answers.groupby("region")
        .apply(mean_correct_guess_rate)
        .reset_index(name="averageGuessRate")
    )

    # Merge the dataframes
    merged_df = pd.merge(top_regions, mean_player_count, on="region").merge(
        mean_guess_rates, on="region"
    )

    return merged_df


def process_top_anime_songs(
    players_answers, anime_songs, start_date, end_date, nbDisplay
):

    playCount = (
        players_answers.groupby(["songId"])
        .rankedId.unique()
        .apply(lambda x: len(x))
        .reset_index(name="playCount")
    )

    playerCount = (
        players_answers.groupby("songId")
        .isCorrect.count()
        .reset_index(name="playerCount")
    )

    guessRate = (
        players_answers.groupby("songId")
        .isCorrect.mean()
        .apply(lambda x: x * 100)
        .round(2)
        .reset_index(name="guessRate")
    )

    anime_songs["songInfo"] = anime_songs.songName + " by " + anime_songs.songArtist

    merged_df = (
        pd.merge(playCount, playerCount[playerCount.playerCount > 100], on="songId")
        .merge(guessRate, on="songId")
        .merge(
            anime_songs[["songId", "animeName", "songName", "songInfo"]], on="songId"
        )
    )

    topSpamAnime = (
        merged_df.groupby("animeName")
        .playCount.sum()
        .reset_index()
        .sort_values(by=["playCount"], ascending=False)
        .head(nbDisplay)
    )

    merged_df = (
        merged_df.groupby(["songInfo"])
        .agg(
            {
                "playCount": "sum",
                "playerCount": "sum",
                "guessRate": "mean",
                "songName": "first",
                "animeName": lambda x: x,
            }
        )
        .reset_index()
    )

    print(merged_df.head(5))

    topSpamSongs = merged_df.sort_values(by=["playCount"], ascending=False).head(
        nbDisplay
    )
    topEasySongs = (
        merged_df[merged_df.playCount > 1]
        .sort_values(by=["guessRate"], ascending=False)
        .head(nbDisplay)
    )
    topHardSongs = (
        merged_df[merged_df.playCount > 2].sort_values(by=["guessRate"]).head(nbDisplay)
    )

    return topSpamAnime, topSpamSongs, topEasySongs, topHardSongs


sqliteConnection, cursor = utils.connect_to_database(
    DATA_RAW_PATH / Path("rankedData.db")
)
fuse_tables(cursor)

nbDisplay = 30
start_date = datetime.date(2022, 10, 1)
end_date = datetime.date.today()

players_answers = utils.extract_top_user_data()
topScore, topTime = process_top_player_df(
    players_answers, start_date, end_date, nbDisplay
)
topRegions = process_top_regions(players_answers, start_date, end_date)

topScore.to_csv(f"data/preprocessed/topScore_{nbDisplay}_{start_date}.csv")
topTime.to_csv(f"data/preprocessed/topTime_{nbDisplay}_{start_date}.csv")
topRegions.to_csv(f"data/preprocessed/topRegions_{start_date}.csv")
del players_answers
"""
players_answers = utils.extract_top_songs_data()
anime_songs = utils.extract_anime_songs()

nbDisplay = 20
topSpamAnime, topSpamSongs, topEasySongs, topHardSongs = process_top_anime_songs(
    players_answers, anime_songs, start_date, end_date, nbDisplay
)
topSpamAnime.to_csv(f"data/preprocessed/topSpamAnime_{nbDisplay}_{start_date}.csv")
topSpamSongs.to_csv(f"data/preprocessed/topSpamSongs_{nbDisplay}_{start_date}.csv")
topEasySongs.to_csv(f"data/preprocessed/topEasySongs_{nbDisplay}_{start_date}.csv")
topHardSongs.to_csv(f"data/preprocessed/topHardSongs_{nbDisplay}_{start_date}.csv")
"""
