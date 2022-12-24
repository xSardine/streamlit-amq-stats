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
import numpy as np, pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime, re
import utils


color_map = {
    "Asia": "rgb(255, 171, 171)",
    "Europe": "rgb(131, 201, 255)",
    "America": "rgb(0, 104, 201)",
}

PREPROCESSED_DATA_PATH = Path("data/preprocessed")


def get_username_data(username, start_date, end_date):

    anime_songs = utils.extract_anime_songs()
    player_answers = utils.extract_answers_username(username)

    player_answers = player_answers[player_answers.date >= str(start_date)]
    player_answers = player_answers[player_answers.date <= str(end_date)]

    rankings = pd.read_csv(PREPROCESSED_DATA_PATH / Path(f"allTop_{start_date}.csv"))
    rankings = rankings[["playerName", "nbSongs", "score", "nbSoloPoints"]]

    userRankings = rankings[rankings.playerName == username]

    if userRankings.empty:
        return anime_songs, pd.DataFrame(), {}

    rankings_output = {}
    tmp = rankings.sort_values(by=["score"], ascending=False).reset_index(drop=True)
    tmp = tmp[tmp.score == userRankings.score.values[0]].index.values
    rankings_output["score"] = [min(tmp) + 1, max(tmp) + 1]

    tmp = rankings.sort_values(by=["nbSongs"], ascending=False).reset_index(drop=True)
    tmp = tmp[tmp.nbSongs == userRankings.nbSongs.values[0]].index.values
    rankings_output["time"] = [min(tmp) + 1, max(tmp) + 1]

    tmp = rankings.sort_values(by=["nbSoloPoints"], ascending=False).reset_index(
        drop=True
    )

    tmp = tmp[tmp.nbSoloPoints == userRankings.nbSoloPoints.values[0]].index.values
    rankings_output["solo"] = [min(tmp) + 1, max(tmp) + 1]

    return anime_songs, player_answers, rankings_output


def get_ranking_particle(ranking):

    number = int(str(ranking)[-1])

    if number == 1:
        return "st"
    elif number == 2:
        return "nd"
    elif number == 3:
        return "rd"
    else:
        return "th"


def plot_distribution(username, anime_songs, player_answers, start_date, end_date):

    st.markdown(
        f"""
    # General Information

    :orange[{username}] played in :orange[{player_answers.rankedId.unique().size} ranked], and was present for :orange[{player_answers.rankedSongId.size} songs] between :orange[{start_date}] and :orange[{end_date}].
    """
    )

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])

    # First pie chart

    values = player_answers.groupby("rankedId").region.unique().value_counts().values

    fig.add_trace(
        go.Pie(
            labels=player_answers.region.unique(),
            values=values,
            title="Regions Distribution",
            domain=dict(x=[0, 0.5]),
            hole=0.5,
            marker=dict(
                colors=[color_map[label] for label in player_answers.region.unique()]
            ),
            showlegend=True,
            legendgroup="group1",
            hovertemplate="Region: %{label}<br>%{value} Ranked<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Second pie chart

    guess_label_map = {
        1: {"label": "Correct Guess", "color": "lightgreen"},
        0: {"label": "Incorrect Guess", "color": "rgb(255, 127, 127)"},
    }

    values = player_answers.isCorrect.value_counts()

    fig.add_trace(
        go.Pie(
            labels=[
                guess_label_map[label]["label"]
                for label in player_answers.isCorrect.value_counts().index
            ],
            values=values,
            title="Guesses Distribution",
            domain=dict(x=[0.5, 1.0]),
            hole=0.5,
            marker=dict(
                colors=[
                    guess_label_map[label]["color"]
                    for label in player_answers.isCorrect.value_counts().index
                ]
            ),
            hovertemplate="%{label}<br>%{value} Guesses<extra></extra>",
            showlegend=True,
            legendgroup="group2",
        ),
        row=1,
        col=2,
    )

    st.plotly_chart(fig)


def plot_top_n_low_pointers(username, anime_songs, player_answers, rankingSolo):

    st.write("# Low Pointers")
    st.caption(
        f"Number of time when :orange[{username}] was one of the few to answer correctly."
    )

    st.write("")
    nb_low = st.slider(
        ":blue[Choose what you consider the limit to a low pointer:]", 4, 10, value=5
    )

    nb_low += 1

    x = (
        player_answers[player_answers.isCorrect == 1]
        .correctCount.value_counts()
        .sort_index()
        .reindex(list(range(1, nb_low)), fill_value=0)
    )

    top = (
        f"the top {rankingSolo[0]}-{rankingSolo[1]}{get_ranking_particle(rankingSolo[1])}"
        if rankingSolo[0] != rankingSolo[1]
        else f"top {rankingSolo[0]}"
    )
    st.write(
        f":orange[{username}] got :orange[{x[1]} solo point{'s' if x[1] > 1 else ''}]. This place them in :orange[{top}] compared to everyone else!"
    )

    y = list(range(1, nb_low))

    lowPointSongs = (
        player_answers[player_answers.isCorrect == 1]
        .groupby("correctCount")
        .songId.apply(list)
        .reindex(range(1, nb_low), fill_value=0)
    )

    z = []

    for id, rankedSongs in lowPointSongs.items():

        if not rankedSongs:
            z.append("")
            continue

        z_tmp = []
        nb_display = 10
        for songId in rankedSongs[: min(nb_display, len(rankedSongs))]:
            songName = anime_songs[anime_songs.songId == songId].songName.values[0]
            songArtist = anime_songs[anime_songs.songId == songId].songArtist.values[0]
            songInfo = f"{songName} by {songArtist}"
            songInfo = songInfo[:70] + "..." if len(songInfo) > 70 else songInfo
            z_tmp.append(songInfo)

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
        title=f"Number of correct people including {username}",
        range=[0.8, nb_low],
        dtick=1,
    )
    fig1.update_xaxes(
        title="Number of occurences",
        range=[0.9, np.max(x) + (20 / 100 * int(np.max(x)))],
    )
    fig1.update_layout(hoverlabel=dict(font=dict(color="darkred")))

    st.plotly_chart(fig1)


def plot_top_n_best_ranked(username, anime_songs, player_answers, rankingScore):

    st.write("# Top Ranked")
    st.caption(f":orange[{username}]'s best ranked scores.")

    st.write("")
    nb_top = st.slider(":blue[Number of ranked to display:]", 3, 30, value=10)

    if nb_top > player_answers.rankedId.unique().size:
        st.error(
            f"{username} only played :orange[{player_answers.rankedId.unique().size}] ranked in that period. Defaulting to :orange[{player_answers.rankedId.unique().size}]"
        )
        nb_top = player_answers.rankedId.unique().size

    topRanked = (
        player_answers.groupby("rankedId")
        .isCorrect.sum()
        .sort_values(ascending=False)
        .reset_index(name="score")
    )

    topRanked = topRanked.head(nb_top).sort_values(by=["score"], ascending=False)

    top = (
        f"the top {rankingScore[0]}-{rankingScore[1]}{get_ranking_particle(rankingScore[1])}"
        if rankingScore[0] != rankingScore[1]
        else f"top {rankingScore[0]}"
    )
    st.write(
        f":orange[{username}]'s best ranked is :orange[{topRanked.iloc[0].score} points]. This place them in :orange[{top}] compared to everyone else!"
    )

    topRanked = topRanked.merge(
        player_answers.groupby("rankedId").agg({"date": "first", "region": "first"}),
        on="rankedId",
        how="left",
    )
    customdata = [[x, y] for x, y in zip(topRanked.date, topRanked.region)]

    fig1 = px.bar(topRanked, x="score", y=list(range(1, nb_top + 1)), orientation="h")

    fig1.update_xaxes(
        title="Score",
        range=[min(topRanked.score) - 0.5, max(topRanked.score) + 0.5],
    )
    fig1.update_yaxes(title="Top", range=[nb_top + 0.5, 0.5], dtick=1)
    fig1.update_traces(
        customdata=customdata,
        hovertemplate="%{x} Points<br>%{customdata[0]} %{customdata[1]}<extra></extra>",
        hoverlabel=dict(font=dict(color="blue")),
    )
    fig1.update_layout(
        hovermode="y",
    )
    st.plotly_chart(fig1)


def plot_performances_over_time(
    username, anime_songs, player_answers, start_date, end_date, rankingTime
):

    st.write("# Play Time")

    top = (
        f"the top {rankingTime[0]}-{rankingTime[1]}{get_ranking_particle(rankingTime[1])}"
        if rankingTime[0] != rankingTime[1]
        else f"top {rankingTime[0]}"
    )

    st.write(
        f":orange[{username}] spent approximately :orange[{round(player_answers.isCorrect.size / 2 / 60)} hours] playing ranked. This place them in :orange[{top}] compared to everyone else!"
    )

    last_day = max(
        end_date,
        datetime.datetime.strptime(np.max(player_answers.date), "%Y-%m-%d").date(),
    )

    first_day = min(
        start_date,
        datetime.datetime.strptime(np.min(player_answers.date), "%Y-%m-%d").date(),
    )

    nb_day = (last_day - first_day).days

    period_map = {
        1: 10,
        2: nb_day / 4,
        3: nb_day / 2,
        4: nb_day * 1.5,
    }
    st.write("")
    periodBin = st.slider(
        ":blue[Period Precision:]",
        1,
        4,
        value=2,
    )
    periodBin = int(period_map[periodBin])

    fig = px.histogram(
        player_answers,
        x="date",
        color="region",
        color_discrete_map=color_map,
        nbins=periodBin,
    )
    fig.update_layout(bargap=0.2, hovermode="x unified")
    fig.update_yaxes(title=f"Number of songs played")
    fig.update_xaxes(title="Date")
    st.plotly_chart(fig)

    st.write("### Guess Rate over time")

    df = (
        player_answers.groupby(["date", "region"])
        .isCorrect.mean()
        .apply(lambda x: round(x, 4) * 100)
        .reset_index(name="guessRate")
    )

    fig = px.histogram(
        df,
        x="date",
        y="guessRate",
        color="region",
        color_discrete_map=color_map,
        nbins=periodBin,
        histfunc="avg",
    )
    fig.update_layout(bargap=0.3, hovermode="x unified", barmode="group")

    fig.update_yaxes(
        title=f"Guess rate",
        range=[max(0, np.min(df.guessRate) - 5), min(100, np.max(df.guessRate) + 5)],
    )

    fig.update_xaxes(title="Date")

    st.plotly_chart(fig)


def plot_worst_songs(username, anime_songs, player_answers):
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
        st.success(f":orange[{username}] never missed a song more than once")
    else:
        st.dataframe(missed, use_container_width=True)

    return


def initialize():

    st.set_page_config(
        page_title="Ranked Statistics - Specific User",
        page_icon="🤖",
    )

    st.title("Ranked Statistics - Specific User")
    st.sidebar.header("Ranked Statistics - Specific User")

    st.markdown(
        "Ranked statistics are based on [blissfulyoshi](https://github.com/blissfulyoshi)'s ranked data. They start from October 1st 2022.\n\nIt is still being collected to this day, but the last update goes up to December 19th 2022."
    )
    st.caption("*Data was not being collected from November 23rd to December 3rd")

    username = st.text_input(
        label=":blue[What is your AMQ username ? _(case sensitive)_]",
        placeholder="AMQ Username",
    )

    if not username:
        st.error("Input a valid username")
        return False, False, False

    st.write("")
    st.write(":blue[Period to check:]")

    today = datetime.date.today()

    col1, col2 = st.columns(2)

    start_date = col1.date_input(
        ":blue[Start date:]",
        datetime.date(2022, 10, 1),
        min_value=datetime.date(2022, 10, 1),
        max_value=today,
    )

    end_date = col2.date_input(
        ":blue[End date:]",
        today,
        min_value=datetime.date(2022, 10, 1),
        max_value=today,
    )

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return False, False, False

    anime_songs, player_answers, rankings = get_username_data(
        username, start_date, end_date
    )

    if player_answers.size == 0:
        swap = username if not re.match("^ +$", username) else "this username"
        st.error(f"No data for :orange[{swap}] in the specified time period.")
    else:
        plot_distribution(username, anime_songs, player_answers, start_date, end_date)
        plot_top_n_low_pointers(username, anime_songs, player_answers, rankings["solo"])
        plot_top_n_best_ranked(username, anime_songs, player_answers, rankings["score"])
        plot_performances_over_time(
            username,
            anime_songs,
            player_answers,
            start_date,
            end_date,
            rankings["time"],
        )
        plot_worst_songs(username, anime_songs, player_answers)


initialize()
