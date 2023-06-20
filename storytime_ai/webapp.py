import asyncio
from io import StringIO
import re

import streamlit as st

from storytime_ai import Story, Dialog
from storytime_ai.utils import getfilelist

st.set_page_config(page_title="Storytime AI", page_icon="📚")

if "story" not in st.session_state:
    st.session_state["story"] = None

with open("./storytime_ai/templates/webapp.css", "r") as f:
    css = f.read()
hide_label = f"<style>\n{css}\n</style>"

st.markdown(hide_label, unsafe_allow_html=True)


# Callbacks
@st.cache_data
def load_stories():
    storyfiles = getfilelist("./storytime_ai/templates", "md", withpath=True)
    stories = [
        Story.from_markdown_file(fname=f) for f in storyfiles if f.name != "README.md" and f.parent.name != "docs"
    ]
    storystats = {s.title + " (" + str(len(s.dialogs)) + " dialogues)": s for s in stories}
    return storystats


def uploadstory():
    upload = st.session_state["upload"]
    if upload is not None:
        stringio = StringIO(upload.getvalue().decode("utf-8"))
        string_data = stringio.read()
        st.session_state["story"] = Story.from_markdown(string_data)


def switch_story():
    st.session_state["story"] = storystats[st.session_state.templates]


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

with st.sidebar.expander("Select template stories"):
    option = st.selectbox(
        "Select a story",
        storystats,
        on_change=switch_story,
        key="templates",
        label_visibility="collapsed",
    )

    # for r in storystats[["title", "number_of_dialogs", "filename"]].itertuples():
    #     st.markdown(
    #         f"""<div style='display:inline-block; color:lightblue; width:70%; font-size:0.8em'>{r.title}</div>
    #                 <div style='display:inline-block; text-align:right; width:20%; font-size:0.7em'>{r.number_of_dialogs} dialogs</div>
    #                 <div style='color:grey;font-size:0.7em; margin-bottom:12px'>{r.filename}</div>
    #                 """,
    #         unsafe_allow_html=True,
    #     )


# Main page
if st.session_state.story is None:
    st.session_state["story"] = list(storystats.values())[0]


def menu_callback(key):
    st.write(st.session_state[key])
    st.session_state["current_menu_pressed"] = st.session_state[key]


col1, col2 = st.columns(2)

with col1:
    new_story = st.button(
        ":blue_book: &nbsp; New story",
        key="newstory",
        use_container_width=True,
    )

with col2:
    st.button(
        ":point_left: &nbsp; Back one dialogue",
        key="backdialog",
        on_click=back_dialog,
        use_container_width=True,
    )


def create_story():
    dialog = Dialog.from_markdown(
        f"## {st.session_state.newstorydialogtitle}\n" f"{st.session_state.newstorydescription}"
    )
    st.session_state["story"] = Story(
        {st.session_state.newstorydialogtitle: dialog},
        st.session_state.newstorytitle,
    )


if new_story:
    with st.form("newstory"):
        st.text_input(
            "New story title",
            value=st.session_state.story.title,
            key="newstorytitle",
        )
        st.text_input(
            "First dialogue title",
            value=st.session_state.story.currentdialog.dialogid,
            key="newstorydialogtitle",
        )
        st.text_area(
            "First dialogue description",
            value=st.session_state.story.currentdialog.text
            + st.session_state.story.currentdialog.choices_to_markdown(),
            key="newstorydescription",
        )
        st.form_submit_button("Create new story", on_click=create_story)
else:
    st.markdown("## " + st.session_state.story.title)
    t = st.empty()
    t.markdown(
        "### " + st.session_state.story.currentdialog.dialogid + "\n" + st.session_state.story.currentdialog.text
    )

    for choice, choiceobject in st.session_state.story.currentdialog.choices.items():
        st.button(
            f"__{choice}__:&nbsp; *{choiceobject.text}*",
            use_container_width=True,
            on_click=next_dialog,
            kwargs={"nextdialog": choice, "t": t},
        )
