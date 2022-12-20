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
import plotly.express as px
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

    player_answers = player_answers.merge(
        ranked_songs[
            [
                "rankedId",
                "rankedSongId",
                "songId",
                "date",
                "region",
                "correctCount",
                "activePlayers",
            ]
        ],
        how="left",
    )

    player_answers = player_answers[player_answers.date >= str(start_date)]
    player_answers = player_answers[player_answers.date <= str(end_date)]

    return player_answers


def plot_distribution(player_answers):

    st.write("# General Information")
    st.write(
        f"{player} played in **{player_answers.rankedId.unique().size}** ranked, and was present for **{player_answers.rankedSongId.size}** songs between **{start_date}** and **{end_date}**"
    )

    color_map = {
        "Asia": "rgb(0,150,0)",
        "Europe": "rgb(150,0,0)",
        "North America": "rgb(0,0,150)",
    }

    values = player_answers.groupby("rankedId").region.unique().value_counts().values

    colors = [color_map[label] for label in player_answers.region.unique()]

    explode = np.zeros(len(values))
    explode[np.argmax(values)] = 0.03

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])

    # First pie chart
    fig.add_trace(
        go.Pie(
            labels=player_answers.region.unique(),
            values=values,
            pull=explode,
            title="Regions Distribution",
            domain=dict(x=[0, 0.5]),
            marker=dict(colors=colors),
            showlegend=True,  # Add this line
            legendgroup="group1",  # Add this line
            hovertemplate="Region: %{label}<br>%{value} Rankeds<extra></extra>",
        ),
        row=1,
        col=1,
    )

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

    # Second pie chart
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            pull=explode,
            title="Guesses Distribution",
            domain=dict(x=[0.5, 1.0]),
            marker=dict(
                colors=[
                    "rgb(0,150,0)",
                    "rgb(150,0,0)",
                ],  # specify custom colors for the pie slices
            ),
            hovertemplate="%{value} Guesses<extra></extra>",
            showlegend=True,  # Add this line
            legendgroup="group2",  # Add this line
        ),
        row=1,
        col=2,
    )

    st.plotly_chart(fig)


def plot_top_n_low_pointers(player, anime_songs, player_answers):

    st.write("# Low Pointers")
    st.write(f"Number of time where {player} was one of the few to answer correctly")
    st.write()
    nb_low = st.slider(
        "Choose what you consider the limit to a low pointer:", 4, 10, value=5
    )

    nb_low += 1

    correctCounts = (
        player_answers[player_answers.isCorrect == 1]
        .correctCount.value_counts()
        .sort_index()
    )

    x = list(
        correctCounts.reindex(
            list(range(1, nb_low)),
            fill_value=0,
        )
    )

    y = list(range(1, nb_low))

    lowPointSongs = (
        player_answers[player_answers.isCorrect == 1]
        .groupby("correctCount")
        .songId.apply(list)
    )

    lowPointSongs = lowPointSongs.reindex(
        list(range(1, nb_low)),
        fill_value=0,
    )

    z = []

    for id, rankedSongs in lowPointSongs.iteritems():

        if not rankedSongs:
            z.append("")
            continue

        z_tmp = []
        nb_display = 10
        for songId in rankedSongs[: min(nb_display, len(rankedSongs))]:
            z_tmp.append(
                " by ".join(
                    list(
                        anime_songs[anime_songs.songId == songId][
                            ["songName", "songArtist"]
                        ].values[0]
                    )
                )
            )

        if len(rankedSongs) > nb_display:
            z_tmp.append("[...]")

        z.append("<br>".join(z_tmp))

    fig1 = go.Figure()
    # Draw points
    fig1.add_trace(
        go.Scatter(
            x=x,
            y=y,
            customdata=z,
            hovertemplate="%{x} Occurences<br>%{customdata}<extra></extra>",
            mode="markers",
            marker_color="darkred",
            marker_size=18,
        )
    )

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
        title=f"Number of correct people including {player}", range=[0.8, nb_low]
    )
    fig1.update_xaxes(
        title="Number of occurences",
        range=[0.9, np.max(x) + (20 / 100 * int(np.max(x)))],
    )
    fig1.update_layout(hovermode="y")

    st.plotly_chart(fig1)


def plot_top_n_best_ranked(player, player_answers):
    st.write("# Top Rankeds")
    st.write(f"{player}'s best ranked scores.")

    nb_top = st.slider("Number of rankeds to display:", 3, 30, value=10)

    if nb_top > player_answers.rankedId.unique().size:
        st.error(
            f"{player} only played {player_answers.rankedId.unique().size} rankeds in that period."
        )
        nb_top = player_answers.rankedId.unique().size

    topRanked = (
        player_answers.groupby("rankedId").isCorrect.sum().sort_values(ascending=False)
    )

    x = list(topRanked)[:nb_top]
    y = list(range(1, nb_top + 1))

    indexes = list(topRanked.index)[:nb_top]
    z = [
        " ".join(
            [
                player_answers[player_answers.rankedId == index].date.unique()[0],
                player_answers[player_answers.rankedId == index].region.unique()[0],
            ]
        )
        for index in indexes
    ]

    fig1 = go.Figure()
    # Draw points
    fig1.add_trace(
        go.Scatter(
            x=x,
            y=y,
            customdata=z,
            hovertemplate="%{x} Points<br>%{customdata}<extra></extra>",
            mode="markers",
            marker_color="darkred",
            marker_size=18,
        )
    )

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

    fig1.update_yaxes(title=f"Top", range=[0, nb_top + 1])
    fig1.update_xaxes(
        title="Correct Guesses",
        range=[
            np.min(x) - (3 / 100 * int(np.max(x))),
            np.max(x) + (3 / 100 * int(np.max(x))),
        ],
    )
    fig1.update_layout(hovermode="y")

    st.plotly_chart(fig1)


def plot_performances_over_time(player, player_answers):

    st.write("# Play Time")
    st.write("*Data was not being collect from November 23rd to December 3rd")

    st.write(
        f"{player} spent approximately {round(player_answers.isCorrect.size / 2 / 60)} hours playing ranked between {start_date} and {end_date}"
    )

    period_map = {
        1: 10,
        2: nb_day / 4,
        3: nb_day / 2,
        4: nb_day * 2,
    }
    periodBin = st.slider(
        "Period Precision:",
        1,
        4,
        value=3,
    )
    periodBin = int(period_map[periodBin])

    fig = px.histogram(player_answers, x="date", nbins=periodBin)
    fig.update_layout(bargap=0.2, hovermode="x")
    fig.update_traces(hovertemplate="Period: %{x}<br>%{y} songs played<extra></extra>")
    fig.update_yaxes(title=f"Number of songs played")
    fig.update_xaxes(title="Date")
    st.plotly_chart(fig)

    st.write("### Score over time")

    df = (
        player_answers.groupby("date")
        .isCorrect.mean()
        .apply(lambda x: round(x, 4) * 100)
        .reset_index()
    )

    fig = px.histogram(df, x="date", y="isCorrect", nbins=periodBin, histfunc="avg")
    fig.update_layout(bargap=0.2, hovermode="x")
    fig.update_traces(
        hovertemplate="Period: %{x}<br>%{y}%<extra></extra>",
    )

    fig.update_yaxes(
        title=f"Guess rate",
        range=[max(0, np.min(df.isCorrect) - 5), min(100, np.max(df.isCorrect) + 5)],
    )

    fig.update_xaxes(title="Date")

    st.plotly_chart(fig)

    st.write("In development...")
    return


def plot_worst_songs(player, anime_songs, player_answers):
    st.write("# Songs missed more than once")
    st.write(f"Please, learn those songs already...")

    songIds = (
        player_answers[player_answers.isCorrect == 0]
        .groupby("songId")
        .isCorrect.count()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"isCorrect": "nb_miss"})
    )

    missed = anime_songs.merge(songIds, how="right")[songIds.nb_miss > 1][
        ["nb_miss", "songName", "songArtist"]
    ]

    if missed.empty:
        st.success("You never missed a song more than once")
    else:
        st.write(missed)

    return


st.set_page_config(
    page_title="Ranked Statistics - Specific User",
    page_icon="📈",
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

if not player:
    st.error("Input a player")
else:
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

    nb_day = rankeds_games.date.unique().size

    player_answers = get_player_data(
        player, players_answers, rankeds_games, start_date, end_date
    )

    if player_answers.size == 0:
        st.error(f"No data for {player} in the specified time period.")
    else:
        plot_distribution(player_answers)
        plot_top_n_low_pointers(player, anime_songs, player_answers)
        plot_top_n_best_ranked(player, player_answers)
        plot_performances_over_time(player, player_answers)
        plot_worst_songs(player, anime_songs, player_answers)
