import json
import random
from pathlib import Path
import streamlit as st
from supabase import create_client, Client


# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    """Create and cache the Supabase client."""
    supabase_url = st.secrets.get("SUPABASE_URL")
    supabase_key = st.secrets.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        # Fallback to local file storage if secrets not configured
        return None
    
    return create_client(supabase_url, supabase_key)


supabase = get_supabase_client()
data_file = Path(__file__).with_name("routines.json")


def load_data():
    """Load data from Supabase or fallback to local file."""
    if supabase:
        try:
            response = supabase.table("routines_data").select("*").eq("id", 1).execute()
            if response.data and len(response.data) > 0:
                data = response.data[0].get("data")
                if isinstance(data, dict) and "routines" in data and "next_id" in data:
                    return data
        except Exception as e:
            st.warning(f"Could not read from Supabase: {e}. Using defaults.")
    else:
        # Fallback to local file
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                if isinstance(data, dict) and "routines" in data and "next_id" in data:
                    return data
            except Exception:
                st.warning("Could not read routines.json, starting with defaults.")
    
    return None


def persist_state():
    """Persist state to Supabase or local file."""
    payload = {"routines": st.session_state.routines, "next_id": st.session_state.next_id}
    
    if supabase:
        try:
            # Upsert to Supabase
            supabase.table("routines_data").upsert({
                "id": 1,
                "data": payload,
                "updated_at": "now()"
            }).execute()
        except Exception as e:
            st.error(f"Failed to save to Supabase: {e}")
    else:
        # Fallback to local file
        data_file.write_text(json.dumps(payload, indent=2))


DEFAULT_ROUTINES = [
    {
        "id": 1,
        "name": "Warm-up Chromatics",
        "description": "5 minutes of 1-2-3-4 chromatic patterns up and down the neck",
        "category": "Warm-up",
        "in_draw": True,
        "done": False,
    },
    {
        "id": 2,
        "name": "Major Scale Positions",
        "description": "Play two-octave major scale in 5 positions with a metronome",
        "category": "Scales",
        "in_draw": True,
        "done": False,
    },
    {
        "id": 3,
        "name": "Chord Changes",
        "description": "Practice G-C-D clean switches for 3 minutes",
        "category": "Rhythm",
        "in_draw": True,
        "done": False,
    },
]


def init_state():
    if "routines" not in st.session_state:
        data = load_data()
        if data:
            st.session_state.routines = data.get("routines", [])
            st.session_state.next_id = data.get("next_id", 1)
        else:
            st.session_state.routines = DEFAULT_ROUTINES.copy()
            st.session_state.next_id = 4
            persist_state()
    if "selected_routine_id" not in st.session_state:
        st.session_state.selected_routine_id = None
    if "drawn_routine_id" not in st.session_state:
        st.session_state.drawn_routine_id = None


def get_categories():
    cats = sorted({r["category"] for r in st.session_state.routines})
    return ["All categories"] + cats if cats else ["All categories"]


def add_routine(name: str, description: str, category: str, in_draw: bool):
    new_routine = {
        "id": st.session_state.next_id,
        "name": name.strip(),
        "description": description.strip(),
        "category": category.strip() or "General",
        "in_draw": in_draw,
        "done": False,
    }
    st.session_state.routines.append(new_routine)
    st.session_state.next_id += 1
    persist_state()


def update_routine(routine_id: int, name: str, description: str, category: str, in_draw: bool):
    for r in st.session_state.routines:
        if r["id"] == routine_id:
            r.update(
                {
                    "name": name.strip(),
                    "description": description.strip(),
                    "category": category.strip() or "General",
                    "in_draw": in_draw,
                }
            )
            persist_state()
            break


def delete_routine(routine_id: int):
    st.session_state.routines = [r for r in st.session_state.routines if r["id"] != routine_id]
    if st.session_state.drawn_routine_id == routine_id:
        st.session_state.drawn_routine_id = None
    persist_state()


def mark_done(routine_id: int, value: bool):
    for r in st.session_state.routines:
        if r["id"] == routine_id:
            if r["done"] != value:
                r["done"] = value
                persist_state()
            break


def reset_done():
    for r in st.session_state.routines:
        r["done"] = False
    st.session_state.drawn_routine_id = None
    persist_state()


def draw_random(selected_category: str):
    pool = [
        r
        for r in st.session_state.routines
        if r["in_draw"]
        and not r["done"]
        and (selected_category == "All categories" or r["category"] == selected_category)
    ]
    if not pool:
        return None
    chosen = random.choice(pool)
    st.session_state.drawn_routine_id = chosen["id"]
    return chosen


def render_routines_table():
    st.subheader("Current routines")
    if not st.session_state.routines:
        st.info("No routines yet. Add one below.")
        return
    rows = []
    for r in st.session_state.routines:
        rows.append(
            {
                "Name": r["name"],
                "Category": r["category"],
                "In draw": "Yes" if r["in_draw"] else "No",
                "Done": "Yes" if r["done"] else "No",
                "Description": r["description"],
                "ID": r["id"],
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


init_state()
st.set_page_config(page_title="Guitar Practice Picker", layout="wide")
st.title("Guitar Practice Picker")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("Random draw")
    selected_category = st.selectbox("Limit draw to", get_categories())
    if st.button("Draw a routine", type="primary"):
        picked = draw_random(selected_category)
        if picked:
            st.success(f"You should practice: {picked['name']} ({picked['category']})")
        else:
            st.warning("No available routines in this category. Try resetting done flags or adding more.")

    if st.session_state.drawn_routine_id:
        drawn = next((r for r in st.session_state.routines if r["id"] == st.session_state.drawn_routine_id), None)
        if drawn:
            st.markdown("---")
            st.write(f"**Selected:** {drawn['name']} — {drawn['category']}")
            st.caption(drawn["description"])
            done_now = st.checkbox("Mark as done", value=drawn["done"], key="mark_done_checkbox")
            mark_done(drawn["id"], done_now)
            if st.button("Reset all done flags"):
                reset_done()
                st.success("All routines marked as not done.")
    else:
        st.info("Click 'Draw a routine' to pick from the available pool.")

with col_right:
    st.header("Manage routines")
    render_routines_table()

    st.subheader("Add a routine")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name")
        description = st.text_area("Description")
        category = st.text_input("Category", placeholder="e.g. Scales, Technique, Songs")
        in_draw = st.checkbox("Include in draw", value=True)
        submitted = st.form_submit_button("Add routine")
        if submitted:
            if name.strip():
                add_routine(name, description, category, in_draw)
                st.success("Routine added.")
            else:
                st.error("Name is required.")

    st.subheader("Edit or delete a routine")
    if st.session_state.routines:
        options = {f"{r['name']} ({r['category']})": r["id"] for r in st.session_state.routines}
        selection = st.selectbox("Choose a routine to edit/delete", list(options.keys()))
        selected_id = options[selection]
        routine = next(r for r in st.session_state.routines if r["id"] == selected_id)
        with st.form("edit_form"):
            name_edit = st.text_input("Name", routine["name"])
            desc_edit = st.text_area("Description", routine["description"])
            cat_edit = st.text_input("Category", routine["category"])
            in_draw_edit = st.checkbox("Include in draw", value=routine["in_draw"])
            col_a, col_b = st.columns(2)
            with col_a:
                save = st.form_submit_button("Save changes", type="primary")
            with col_b:
                delete = st.form_submit_button("Delete", type="secondary")
            if save:
                if name_edit.strip():
                    update_routine(selected_id, name_edit, desc_edit, cat_edit, in_draw_edit)
                    st.success("Routine updated.")
                else:
                    st.error("Name is required.")
            if delete:
                delete_routine(selected_id)
                st.warning("Routine deleted.")
    else:
        st.info("No routines to edit yet.")
