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
import datetime
import utils
import plotly.express as px
import plotly.graph_objects as go
import gc
import pandas as pd
from pathlib import Path
import plotly.subplots as subplots


PREPROCESSED_DATA_PATH = Path("data/preprocessed")

# Enable garbage collection
gc.enable()

color_map = {
    "Asia": "rgb(255, 171, 171)",
    "Europe": "rgb(131, 201, 255)",
    "America": "rgb(0, 104, 201)",
}


# @st.cache(ttl=24 * 3600)
def get_data(start_date, end_date):

    anime_songs = utils.extract_anime_songs()
    player_answers = utils.extract_top_user_data()

    player_answers = player_answers[player_answers.date >= str(start_date)]
    player_answers = player_answers[player_answers.date <= str(end_date)]

    return anime_songs, player_answers


# @st.cache(ttl=24 * 3600, suppress_st_warning=True)
def load_top_users_data(start_date, nbDisplay):

    topScore = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topScore_{nbDisplay}_{start_date}.csv")
    )
    topTime = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topTime_{nbDisplay}_{start_date}.csv")
    )
    topSolo = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topSolo_{nbDisplay}_{start_date}.csv")
    )

    return topScore, topTime, topSolo


# @st.cache(ttl=24 * 3600, suppress_st_warning=True)
def load_top_regions_data(start_date):

    topRegions = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topRegions_{start_date}.csv")
    )

    return topRegions


# @st.cache(ttl=24 * 3600, suppress_st_warning=True)
def load_top_anime_songs_data(start_date, nbDisplay):

    topSpamAnime = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topSpamAnime_{nbDisplay}_{start_date}.csv")
    )
    topSpamSongs = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topSpamSongs_{nbDisplay}_{start_date}.csv")
    )
    topEasySongs = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topEasySongs_{nbDisplay}_{start_date}.csv")
    )
    topHardSongs = pd.read_csv(
        PREPROCESSED_DATA_PATH / Path(f"topHardSongs_{nbDisplay}_{start_date}.csv")
    )

    return topSpamAnime, topSpamSongs, topEasySongs, topHardSongs


def plot_top_players(start_date):

    st.markdown("# Top Players")

    nbDisplay = 30

    st.markdown("### Top Players - Best Scores")

    st.caption("*Only keeping best score for each player")

    topScore, topTime, topSolo = load_top_users_data(start_date, nbDisplay)

    topScore = topScore.sort_values(by=["score"])

    col1, col2, col3 = st.columns(3)
    with col2:
        st.image(
            "static/gold.png",
            width=250,
            caption=f"👑 {topScore.iloc[-1].playerName}: {topScore.iloc[-1].score} points | {topScore.iloc[-1].date}",
        )

    del col1, col2, col3

    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(
            "static/silver.png",
            width=250,
            caption=f"⚔️ {topScore.iloc[-2].playerName}: {topScore.iloc[-2].score} points | {topScore.iloc[-2].date}",
        )
    with col3:
        st.image(
            "static/bronze.png",
            width=250,
            caption=f"🗡️ {topScore.iloc[-3].playerName}: {topScore.iloc[-3].score} points | {topScore.iloc[-3].date}",
        )

    customdata = [
        [x, y]
        for x, y in zip(
            topScore.date,
            topScore.region,
        )
    ]

    # Create the stacked bar chart
    fig = px.bar(
        topScore,
        x="score",
        y="playerName",
        height=550,
        width=730,
    )
    fig.update_traces(
        customdata=customdata,
        hovertemplate="%{y}<br>%{x} Points<br>%{customdata[0]} %{customdata[1]}",
        hoverlabel=dict(font=dict(color="blue")),
    )
    fig.update_yaxes(title="Player", dtick=1)
    fig.update_xaxes(
        title="Best Score", range=[min(topScore.score) - 2, max(topScore.score)]
    )
    fig.update_layout(hovermode="y")

    st.plotly_chart(fig)

    st.markdown("### Top Players - Most Songs Played")

    # Create the stacked bar chart
    fig2 = px.bar(
        topTime,
        x="nbSongs",
        y="playerName",
        color="region",
        color_discrete_map=color_map,
        category_orders={"playerName": topTime.playerName.unique()},
        height=600,
        width=730,
    )

    fig2.update_yaxes(title="Player", dtick=1)
    fig2.update_xaxes(title="Number of songs played")
    fig2.update_layout(hovermode="y unified")

    st.plotly_chart(fig2)

    st.markdown("### Top Players - Most Solo Points")

    # Create the stacked bar chart
    topSolo = topSolo.sort_values(by=["nbSoloPoints"])
    fig3 = go.Figure()

    fig3.add_trace(
        go.Scatter(
            x=topSolo.nbSoloPoints,
            y=topSolo.playerName,
            mode="markers",
            marker_color="darkred",
            marker_size=12,
        )
    )
    # Draw lines
    for i, x_ in enumerate(topSolo.nbSoloPoints):
        fig3.add_shape(
            type="line",
            x0=0,
            y0=i,
            x1=x_,
            y1=i,
            line=dict(color="crimson", width=3),
        )

    fig3.update_yaxes(title="Player", dtick=1)
    fig3.update_xaxes(title="Number of solo points")
    fig3.update_traces(
        hovertemplate="%{y}<br>%{x} times<extra></extra>",
        hoverlabel=dict(font=dict(color="darkred")),
    )
    fig3.update_layout(
        hovermode="y",
        height=600,
        width=730,
    )
    st.plotly_chart(fig3)

    del topScore, topTime, fig, fig2, fig3, col1, col2, col3


def plot_top_region(start_date):

    st.markdown("# Top Regions")

    topRegions = load_top_regions_data(start_date)

    st.markdown("### Top Regions - Total playerbase")

    # Create a figure with two traces: one for the bars and one for the horizontal lines
    fig = go.Figure(
        data=[
            # Create the bars using the go.Bar trace type
            go.Bar(
                name="playerCount",
                x=topRegions["region"],
                y=topRegions["playerCount"],
                marker_color=[color_map[region] for region in topRegions["region"]],
            ),
            # Create the horizontal lines using the go.Scatter trace type
            go.Scatter(
                name="playerAverage",
                x=topRegions["region"],
                y=topRegions["playerAverage"],
                mode="lines+markers",
                line=dict(color="red", width=3),
                marker=dict(size=10, color="red"),
            ),
        ]
    )

    # Set the title and axis labels
    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Total player Count",
        # Set the colors of the legend items
        legend=dict(
            title=None,
            itemsizing="constant",
            bordercolor="#E2E2E2",
            borderwidth=2,
        ),
    )

    st.plotly_chart(fig)

    st.markdown("### Top Regions - Guess Rate")

    st.caption("*Only counting the top 150 player for each region")

    fig = px.bar(
        topRegions,
        x="region",
        y="averageGuessRate",
        color="region",
        color_discrete_map=color_map,
    )
    fig.update_yaxes(
        title="Average guess rate",
        range=[
            min(topRegions.averageGuessRate) - 5,
            max(topRegions.averageGuessRate) + 5,
        ],
    )

    st.plotly_chart(fig)


def plot_top_anime_songs(start_date):

    st.markdown("# Top Anime / Songs")

    nbDisplay = 20
    topSpamAnime, topSpamSongs, topEasySongs, topHardSongs = load_top_anime_songs_data(
        start_date, nbDisplay
    )

    st.markdown("### Spamming Anime")

    topSpamAnime = topSpamAnime.sort_values(by=["playCount"], ascending=True)
    topSpamAnime["label"] = topSpamAnime.animeName.apply(
        lambda x: x[:40] + ("..." if len(x) > 25 else "")
    )
    fig = px.bar(topSpamAnime, x="playCount", y="label")
    fig.update_traces(
        hovertemplate="%{label}<br>%{x} times",
        hoverlabel=dict(font=dict(color="blue")),
    )
    fig.update_yaxes(title="Anime")
    fig.update_xaxes(title="Play count")

    st.plotly_chart(fig)

    st.markdown("### Spamming Songs")

    topSpamSongs = topSpamSongs.sort_values(by=["playCount"], ascending=True)
    topSpamSongs["label"] = topSpamSongs.songName.apply(
        lambda x: x[:40] + ("..." if len(x) > 25 else "")
    )
    fig = px.bar(topSpamSongs, x="playCount", y="label")
    fig.update_traces(
        customdata=topSpamSongs.songInfo,
        hovertemplate="%{customdata}<br>%{x} times",
        hoverlabel=dict(font=dict(color="blue")),
    )
    fig.update_yaxes(title="Songs")
    fig.update_xaxes(
        title="Play count",
        range=[topSpamSongs.playCount.min() - 2, topSpamSongs.playCount.min() + 2],
    )

    st.plotly_chart(fig)

    st.markdown("### Hardest / Easiest Songs")

    topEasySongs = topEasySongs.sort_values(by=["guessRate"], ascending=True)

    st.caption(
        "*Played at least 3 times in ranked for hardest songs, and at least twice for easiest songs"
    )

    # Create a bar chart for the bottom 20 elements
    fig_bottom = px.bar(
        topHardSongs,
        x="guessRate",
        y="songName",
        title="Bottom 20 Elements",
        height=550,
    )

    customdata = [
        [x, y, z]
        for x, y, z in zip(
            topHardSongs.songInfo, topHardSongs.playerCount, topHardSongs.animeName
        )
    ]
    fig_bottom.update_traces(
        customdata=customdata,
        hovertemplate="%{customdata[0]}<br>%{customdata[2]}<br>Guess Rate: %{x}%<br>%{customdata[1]} guesses",
        marker_color="rgb(255, 127, 127)",
        hoverlabel=dict(font=dict(color="red")),
    )

    # Create a bar chart for the top 20 elements
    fig_top = px.bar(
        topEasySongs,
        x="guessRate",
        y="songName",
        title="Top 20 Elements",
        height=550,
    )

    customdata = [
        [x, y, z]
        for x, y, z in zip(
            topEasySongs.songInfo, topEasySongs.playerCount, topEasySongs.animeName
        )
    ]
    fig_top.update_traces(
        customdata=customdata,
        hovertemplate="%{customdata[0]}<br>%{customdata[2]}<br>Guess Rate: %{x}%<br>%{customdata[1]} guesses",
        marker_color="lightgreen",
        hoverlabel=dict(font=dict(color="green")),
    )

    # Combine the two charts into a single figure with a split x-axis
    fig = subplots.make_subplots(
        rows=1, cols=2, shared_yaxes=True, specs=[[{}, {"secondary_y": True}]]
    )

    # Add the bottom 20 elements to the left y-axis
    fig.add_trace(fig_bottom["data"][0], row=1, col=1)

    # Add the top 20 elements to the right y-axis
    fig.add_trace(fig_top["data"][0], row=1, col=2, secondary_y=True)

    # Set the titles and labels for the y-axes
    fig.update_layout(
        height=550,
        yaxis1=dict(title="Songs", dtick=1),
        yaxis2=dict(dtick=1),
        xaxis1=dict(title="Hardest songs", dtick=1),
        xaxis2=dict(
            title="Easiest songs",
            dtick=2,
            range=[topEasySongs.guessRate.max() + 1, topEasySongs.guessRate.min() - 1],
        ),
        hovermode="y",
    )

    st.plotly_chart(fig)


def plot_over_time(start_date):

    st.markdown("# Stats Over Time")

    st.markdown("### Playerbase over time")
    st.write("In development...")
    st.markdown("### Average Guess Rate over time")
    st.write("In development...")


def initialize():

    st.set_page_config(
        page_title="Ranked Statistics - General",
        page_icon="🌍",
    )

    st.title("Ranked Statistics - General")
    st.sidebar.header("Ranked Statistics - General")

    st.markdown(
        "Ranked statistics are based on [blissfulyoshi](https://github.com/blissfulyoshi)'s ranked data. They start from October 1st 2022.\n\nIt is still being collected to this day, but the last update go up to December 19th 2022."
    )
    st.caption("*Data was not being collected from November 23rd to December 3rd")

    start_date = datetime.date(2022, 10, 1)

    end_date = datetime.date.today()

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return False, False, False

    # anime_songs, players_answers = get_data(start_date, end_date)

    plot_top_players(start_date)
    plot_top_region(start_date)
    plot_top_anime_songs(start_date)
    # plot_over_time(start_date)


initialize()
