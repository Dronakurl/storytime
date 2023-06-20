import asyncio
from io import StringIO
import re
import time
import pandas as pd
import streamlit as st

from storytime_ai import Story
from storytime_ai.utils import getfilelist

st.set_page_config(page_title="Storytime AI", page_icon="📚")


if "story" not in st.session_state:
    st.session_state["story"] = None


hide_label = """
<style>
/* Change the Upload button */
.css-9ycgxx, .css-7oyrr6 {
    display: none;
}
.css-w770g5 {
    width: 100%;
}
.css-fhd5bg {
    padding: 0px;
    margin: 0px;
}
.css-u8hs99 {
    display: none;
}
.css-w770g5::before {
    content: "Upload story - ";
    white-space: pre;
}
.css-q8sbsg p {
    font-size: 16px;
}
.uploadedFile {
    display: none;
}
.css-fis6aj {
    padding: 0px;
}

/* Hide the link button */
.stApp a:first-child {
    display: none;
}

.css-15zrgzn {display: none}
.css-eczf16 {display: none}
.css-jn99sy {display: none}

/* Hide the footer Made with */
footer {display: none; }
header, .css-1avcm0n {display: none; }
/* Make the expander smaller */
.streamlit-expanderHeader {
    padding-top: 4px;
    padding-bottom: 4px;
}
</style>
"""

st.markdown(hide_label, unsafe_allow_html=True)


# Callbacks
@st.cache_data
def load_stories():
    storyfiles = getfilelist("./storytime_ai/templates", "md", withpath=True)
    stories = [
        Story.from_markdown_file(fname=f) for f in storyfiles if f.name != "README.md" and f.parent.name != "docs"
    ]
    storystats = pd.DataFrame(
        [(s.title, len(s.dialogs), s.markdown_file, s) for s in stories],
        columns=["title", "number_of_dialogs", "filename", "storyobject"],
    )
    storystats["formatted"] = storystats["title"] + " (" + storystats["number_of_dialogs"].astype(str) + " dialogs)"
    return storystats


def uploadstory():
    upload = st.session_state["upload"]
    if upload is not None:
        stringio = StringIO(upload.getvalue().decode("utf-8"))
        string_data = stringio.read()
        st.session_state["story"] = Story.from_markdown(string_data)


def switch_story():
    st.session_state["story"] = storystats[storystats["formatted"] == st.session_state.templates].iloc[0, :].storyobject


async def aync_next_dialog(nextdialog: str = None, t=None):
    async for currentresult, _ in st.session_state.story.continue_story(nextdialog, override_existing=False):
        t.markdown(currentresult)


def next_dialog(nextdialog: str = None, t=None):
    asyncio.run(aync_next_dialog(nextdialog, t))


def back_dialog():
    st.session_state.story.back_dialog()


def set_secret():
    st.session_state.story.secretsummary = st.session_state.secretsummary


def set_custom_choice():
    choice = st.session_state.customchoice
    x = re.search(r"(.+): (.+)", choice)
    if not x:
        text = description = choice
    else:
        description, text = x.groups()
    st.session_state.story.addchoice(text, description)


def get_story() -> str:
    if st.session_state.story is None:
        return ""
    return st.session_state.story.to_markdown()


# Sidebar
# st.sidebar.write(time.time())
st.sidebar.title("Storytime AI")

storystats = load_stories()
st.sidebar.file_uploader(
    "Upload a story",
    type="md",
    on_change=uploadstory,
    accept_multiple_files=False,
    label_visibility="collapsed",
    key="upload",
)


if st.session_state.story is not None:
    title = st.session_state.story.title
else:
    title = "Story"

st.sidebar.download_button(
    "Download story",
    data=get_story(),
    mime="text/markdown",
    file_name=title + ".md",
    use_container_width=True,
)

st.sidebar.button(
    "Go back one dialog",
    use_container_width=True,
    on_click=back_dialog,
)

with st.sidebar.expander("Edit secret story plot"):
    if not st.session_state.story:
        secretsummary = ""
    else:
        secretsummary = st.session_state.story.secretsummary
    st.text_area(
        "Edit story plot",
        label_visibility="collapsed",
        value=secretsummary,
        key="secretsummary",
        on_change=set_secret,
    )

with st.sidebar.expander("Add a custom choice"):
    st.text_area(
        "Add a custom choice",
        label_visibility="collapsed",
        value="",
        key="customchoice",
        on_change=set_custom_choice,
    )

with st.sidebar.expander("Show template stories"):
    option = st.selectbox(
        "## Select a template story",
        storystats["formatted"],
        on_change=switch_story,
        key="templates",
    )

    for r in storystats[["title", "number_of_dialogs", "filename"]].itertuples():
        st.markdown(
            f"""<div style='display:inline-block; color:lightblue; width:70%; font-size:0.8em'>{r.title}</div>
                    <div style='display:inline-block; text-align:right; width:20%; font-size:0.7em'>{r.number_of_dialogs} dialogs</div>
                    <div style='color:grey;font-size:0.7em; margin-bottom:12px'>{r.filename}</div>
                    """,
            unsafe_allow_html=True,
        )


# Main page
if st.session_state.story is None:
    story = storystats[storystats["formatted"] == option].iloc[0, :].storyobject
    st.session_state["story"] = story

st.markdown("## " + st.session_state.story.title)
t = st.empty()
t.markdown("### " + st.session_state.story.currentdialog.dialogid + "\n" + st.session_state.story.currentdialog.text)


for choice, choiceobject in st.session_state.story.currentdialog.choices.items():
    st.button(
        choice + ": " + choiceobject.text,
        use_container_width=True,
        on_click=next_dialog,
        kwargs={"nextdialog": choice, "t": t},
    )
