import sqlite3
import pandas as pd
import streamlit as st


def connect_to_database(database_path):

    """
    Connect to the database and return the connection's cursor
    """

    try:
        sqliteConnection = sqlite3.connect(database_path)
        cursor = sqliteConnection.cursor()
        return sqliteConnection, cursor
    except sqlite3.Error as error:
        print("\n", error, "\n")
        exit(0)


def run_sql_command(cursor, sql_command, data=None):

    """
    Run the SQL command with nice looking print when failed (no)
    """

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        record = cursor.fetchall()

        return record

    except sqlite3.Error as error:

        if data is not None:
            for param in data:
                if type(param) == str:
                    sql_command = sql_command.replace("?", '"' + str(param) + '"', 1)
                else:
                    sql_command = sql_command.replace("?", str(param), 1)

        print(
            "\nError while running this command: \n",
            sql_command,
            "\n",
            error,
            "\nData: ",
            data,
            "\n",
        )
        return None


# @st.cache()
def extract_top_user_data():

    sqliteConnection, cursor = connect_to_database("data/raw/rankedData.db")

    region_map = {1: "Asia", 2: "Europe", 3: "America"}
    command = f"SELECT date, region, playerName, isCorrect from players_answers"
    results = run_sql_command(cursor, command)
    df = pd.DataFrame(
        results,
        columns=[
            "date",
            "region",
            "playerName",
            "isCorrect",
        ],
    )
    del results
    return df.replace({"region": region_map})


# @st.cache()
def extract_top_songs_data():

    sqliteConnection, cursor = connect_to_database("data/raw/rankedData.db")

    region_map = {1: "Asia", 2: "Europe", 3: "America"}
    command = f"SELECT rankedId, songId, isCorrect from players_answers"
    results = run_sql_command(cursor, command)
    df = pd.DataFrame(
        results,
        columns=[
            "rankedId",
            "songId",
            "isCorrect",
        ],
    )
    del results
    return df.replace({"region": region_map})


# @st.cache(suppress_st_warning=True)
def extract_anime_songs():

    sqliteConnection, cursor = connect_to_database("data/raw/rankedData.db")

    command = f"SELECT * from anime_songs"
    results = run_sql_command(cursor, command)
    df = pd.DataFrame(
        results,
        columns=[
            "animeId",
            "annId",
            "animeName",
            "songId",
            "songName",
            "songArtist",
            "songType",
            "songNumber",
            "songDifficulty",
        ],
    )
    del results
    return df


@st.cache(persist=False, suppress_st_warning=True, ttl=24 * 3600, max_entries=25)
def extract_answers_username(username):

    sqliteConnection, cursor = connect_to_database("data/raw/rankedData.db")

    command = f"SELECT * from players_answers WHERE playerName='{username}'"
    results = run_sql_command(cursor, command)

    region_map = {1: "Asia", 2: "Europe", 3: "America"}

    df = pd.DataFrame(
        results,
        columns=[
            "rankedId",
            "date",
            "region",
            "rankedSongId",
            "rankedSongNumber",
            "songId",
            "startTime",
            "correctCount",
            "activePlayers",
            "playerId",
            "playerName",
            "animeId",
            "guessTime",
            "isCorrect",
        ],
    )
    del results
    return df.replace({"region": region_map})
