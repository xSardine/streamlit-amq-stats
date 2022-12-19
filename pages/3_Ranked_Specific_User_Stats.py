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


def plot_distribution(players_answers, rankeds_games):

    player = st.text_input(
        label="What is your AMQ username ? (case sensitive)",
        placeholder="AMQ Username",
        value="Rukawa11",
    )

    region_labels = ["Asia", "EU", "NA"]

    player_answers = players_answers[players_answers.playerName == player]
    ranked_songs = rankeds_games[
        rankeds_games.rankedSongId.isin(player_answers.rankedSongId)
    ]

    if player_answers.size == 0:
        return

    values = ranked_songs.groupby(["rankedId"]).mean().region.value_counts().values
    labels = [
        region_labels[int(label - 1)]
        for label in ranked_songs.groupby(["rankedId"])
        .mean()
        .region.value_counts()
        .index
    ]
    explode = np.zeros(len(values))
    explode[np.argmax(values)] = 0.03

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])

    # First pie chart
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            pull=explode,
            title="Regions Distribution",
            domain=dict(x=[0, 0.5]),
            hovertemplate="Region: %{label}<br>%{value} Rankeds<extra></extra>",
            showlegend=True,  # Add this line
            legendgroup="group1",  # Add this line
        ),
        row=1,
        col=1,
    )

    correctLabels = ["Correct Guess", "Incorrect Guess"]
    values = player_answers.isCorrect.value_counts().values
    labels = [
        correctLabels[int(label - 1)]
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


st.set_page_config(page_title="Ranked - Specific User", page_icon="📈")
st.markdown("# Ranked - Specific User")
st.sidebar.header("Ranked - Specific User")

st.write(
    """Ranked statistics are based on blissfulyoshi's ranked data. They start from October 29th 2022."""
)

anime_songs, players_answers, rankeds_games = load_data()

plot_distribution(players_answers, rankeds_games)
