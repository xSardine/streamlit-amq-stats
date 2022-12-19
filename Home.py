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
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():

    st.set_page_config(
        page_title="Home",
        page_icon="👋",
    )

    st.write("# Welcome to AMQ Stats! 👋")

    st.sidebar.success("Select a section above.")

    st.markdown(
        """

        Welcome to my web application for statistics on Anime Music Quiz (AMQ), a popular quiz game developed by Egerod. 
        This application is not affiliated with AMQ or Egerod, but it uses data from an improved version of the AMQ database that I maintain. 
        
        I also use ranked data collected by [blissfulyoshi](https://github.com/blissfulyoshi) for anything related to ranked.

        Big thanks to Egerod and more importantly the database admins for maintaining the AMQ database and to blissfulyoshi for collecting the ranked data.
        
        If you haven't played AMQ yet, be sure to check it out at https://animemusicquiz.com. 
        It features one of the largest and most comprehensive community-driven anime song databases and many other features that make it one of the most advanced quiz games out there.

        I hope you enjoy using my web application! Please let me know if you have any questions or feedback.

        """
    )


if __name__ == "__main__":
    run()
