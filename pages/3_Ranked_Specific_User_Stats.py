# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from plotly.subplots import make_subplots
import datetime


DATA_CSV_PATH = Path("data/csv/")


@st.cache
def load_data():
    anime_songs = pd.read_csv(DATA_CSV_PATH / Path("anime_songs.csv"))
    players_answers = pd.read_csv(DATA_CSV_PATH / Path("players_answers.csv"))
    rankeds_games = pd.read_csv(DATA_CSV_PATH / Path("rankeds_games.csv"))
    return anime_songs, players_answers, rankeds_games


def pie_autopct(values):
    def tmp_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return "{p:.2f}%  ({v:d})".format(p=pct, v=val)

    return tmp_autopct


def get_player_data(player, players_answers, rankeds_games, start_date, end_date):

    player_answers = players_answers[players_answers.playerName == player]

    ranked_songs = rankeds_games[
        rankeds_games.rankedSongId.isin(player_answers.rankedSongId)
    ]

    ranked_songs = ranked_songs[ranked_songs.date >= str(start_date)]
    ranked_songs = ranked_songs[ranked_songs.date <= str(end_date)]

    player_answers = player_answers[
        player_answers.rankedSongId.isin(ranked_songs.rankedSongId.values)
    ]

    return player_answers, ranked_songs


def plot_distribution(player_answers, ranked_songs):

    st.write("## General Information")
    st.write(
        f"{player} played in **{ranked_songs.rankedId.unique().size}** ranked, and was present for **{player_answers.rankedSongId.size}** songs between **{start_date}** and **{end_date}**"
    )

    region_label_map = {
        1.0: {"label": "Asia", "color": "rgb(0,150,0)"},
        2.0: {"label": "EU", "color": "rgb(150,0,0)"},
        3.0: {"label": "NA", "color": "rgb(0,0,150)"},
    }

    col1, col2 = st.columns(2)

    values = ranked_songs.groupby(["rankedId"]).mean().region.value_counts().values
    labels = [
        region_label_map[label]["label"]
        for label in ranked_songs.groupby(["rankedId"])
        .mean()
        .region.value_counts()
        .index
    ]
    colors = [
        region_label_map[label]["color"]
        for label in ranked_songs.groupby(["rankedId"])
        .mean()
        .region.value_counts()
        .index
    ]
    explode = np.zeros(len(values))
    explode[np.argmax(values)] = 0.03

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                pull=explode,
                title="Regions Distribution",
                domain=dict(x=[0, 0.5]),
                marker=dict(colors=colors),
                hovertemplate="Region: %{label}<br>%{value} Rankeds<extra></extra>",
            ),
        ],
        layout=go.Layout(
            legend=go.layout.Legend(x=0.1, y=1.1, xanchor="right", yanchor="top")
        ),
    )

    col1.plotly_chart(fig)

    guess_label_map = {
        1: {"label": "Correct Guess", "color": "rgb(0,150,0)"},
        0: {"label": "Incorrect Guess", "color": "rgb(150,0,0)"},
    }

    values = player_answers.isCorrect.value_counts().values
    labels = [
        guess_label_map[label]["label"]
        for label in player_answers.isCorrect.value_counts().index
    ]
    colors = [
        guess_label_map[label]["color"]
        for label in player_answers.isCorrect.value_counts().index
    ]
    explode = np.zeros(len(values))
    explode[np.argmax(values)] = 0.03

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                pull=explode,
                title="Guesses Distribution",
                domain=dict(x=[0.5, 1.0]),
                marker=dict(colors=colors),
                hovertemplate="%{value} Guesses<extra></extra>",
            ),
        ]
    )

    col2.plotly_chart(fig)


def plot_top_n_low_pointers(player, player_answers, ranked_songs):

    st.write("## Low Pointers")
    st.write(f"Number of time where {player} was one of the few to answer correctly")

    nb_low = st.slider(
        "Choose what you consider the limit to a low pointer", 4, 10, value=5
    )

    x = list(
        ranked_songs[
            ranked_songs.rankedSongId.isin(
                player_answers[player_answers.isCorrect == 1].rankedSongId
            )
        ]
        .correctCount.value_counts()
        .sort_index()
        .values
    )[: nb_low + 1]

    y = list(range(1, len(x)))

    fig1 = go.Figure()
    # Draw points
    fig1.add_trace(
        go.Scatter(
            x=x,
            y=y,
            hovertemplate="%{x} Occurences<extra></extra>",
            mode="markers",
            marker_color="darkblue",
            marker_size=10,
        )
    )

    x = x[:-1]

    # Draw lines
    for i, x_ in enumerate(x):
        fig1.add_shape(
            type="line",
            x0=0,
            y0=i + 1,
            x1=x_,
            y1=i + 1,
            line=dict(color="crimson", width=3),
        )

    fig1.update_yaxes(
        title=f"Number of correct people including {player}", range=[0.8, nb_low + 1]
    )
    fig1.update_xaxes(title="Number of occurences", range=[0.9, np.max(x) + 10])
    fig1.update_layout(hovermode="y")

    st.plotly_chart(fig1)


def plot_top_n_best_ranked(player, player_answers, ranked_songs):
    st.write("## Top Rankeds")
    st.write(f"{player}'s best ranked scores.")
    st.write("In development...")
    return


def plot_performances_over_time(player, player_answers, ranked_songs):
    st.write("## Performances over time")
    st.write(f"{player}'s performances over time.")
    st.write("In development...")
    return


st.set_page_config(
    page_title="Ranked - Specific User", page_icon="📈", layout="centered"
)
st.markdown("# Ranked - Specific User")
st.sidebar.header("Ranked - Specific User")

st.write(
    """Ranked statistics are based on blissfulyoshi's ranked data. They start from October 1st 2022."""
)

anime_songs, players_answers, rankeds_games = load_data()

player = st.text_input(
    label="What is your AMQ username ? (case sensitive)",
    placeholder="AMQ Username",
    value="Rukawa11",
)

st.write("Period to check:")

today = datetime.date.today()

col1, col2 = st.columns(2)

start_date = col1.date_input(
    "Start date",
    datetime.date(2022, 10, 1),
    min_value=datetime.date(2022, 10, 1),
    max_value=today,
)

end_date = col2.date_input(
    "End date",
    today,
    min_value=datetime.date(2022, 10, 1),
    max_value=today,
)

if start_date > end_date:
    st.error("Error: End date must fall after start date.")

player_answers, ranked_songs = get_player_data(
    player, players_answers, rankeds_games, start_date, end_date
)

if player_answers.size == 0:
    st.error(f"No data for {player} in the specified time period.")
else:
    plot_distribution(player_answers, ranked_songs)
    plot_top_n_low_pointers(player, player_answers, ranked_songs)
    plot_top_n_best_ranked(player, players_answers, rankeds_games)
    plot_performances_over_time(player, players_answers, rankeds_games)
