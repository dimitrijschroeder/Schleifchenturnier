import streamlit as st
import random
from collections import defaultdict
import pandas as pd

st.set_page_config(page_title="Fast Four Turnament", layout="wide")

# Session state initialisieren
if 'players' not in st.session_state:
    st.session_state.players = []
    st.session_state.scores = defaultdict(list)
    st.session_state.differentials = defaultdict(list)
    st.session_state.round = 0
    st.session_state.matches = []
    st.session_state.byes = []
    st.session_state.semifinals = None
    st.session_state.manual_edit = False

st.title("🎾 Fast Four")

# Spielerliste laden
st.header("📥 Spielerliste")
loaded_names = st.text_area("Spieler (ein Name pro Zeile)")
if st.button("Spielerliste übernehmen"):
    names = [n.strip() for n in loaded_names.strip().split("\n") if n.strip()]
    st.session_state.players = []
    st.session_state.scores.clear()
    st.session_state.differentials.clear()
    for n in names:
        st.session_state.players.append(n)
        st.session_state.scores[n] = ['X'] * st.session_state.round
        st.session_state.differentials[n] = ['X'] * st.session_state.round

# Spieler-Eingabe & Verwaltung
st.markdown("Liste bearbeiten")
col1, col2 = st.columns(2)
with col1:
    with st.form(key="add_player_form", clear_on_submit=True):
        new_player = st.text_input("Spieler hinzufügen", key="new_player_form_input")
        submit = st.form_submit_button("➕ Hinzufügen")
        if submit and new_player.strip():
            if new_player not in st.session_state.players:
                st.session_state.players.append(new_player)
                st.session_state.scores[new_player] = ['X'] * st.session_state.round
                st.session_state.differentials[new_player] = ['X'] * st.session_state.round

with col2:
    remove_player = st.selectbox("Spieler entfernen", [p for p in st.session_state.players])
    if st.button("❌ Entfernen") and remove_player:
        st.session_state.players.remove(remove_player)
        del st.session_state.scores[remove_player]
        del st.session_state.differentials[remove_player]

st.markdown("---")

# Neue Runde auslosen & manuelle Bearbeitung
st.header("🌀 Auslosung")
col1, col2 = st.columns(2)
if col1.button("Runde auslosen"):
    grouped = defaultdict(list)
    for p in st.session_state.players:
        played = sum(1 for x in st.session_state.scores[p] if x != 'X')
        grouped[played].append(p)

    grouped_players = []
    for k in sorted(grouped):
        grp = grouped[k]
        random.shuffle(grp)
        grouped_players.extend(grp)

    matches, byes = [], grouped_players[:]
    st.session_state.matches = []
    st.session_state.byes = []

    while len(byes) >= 4:
        t1 = [byes.pop(0), byes.pop(0)]
        t2 = [byes.pop(0), byes.pop(0)]
        matches.append((t1, t2))

    st.session_state.matches = matches
    st.session_state.byes = byes
    st.session_state.results_input = {}
    st.session_state.manual_edit = False

if col2.button("✏️ Manuell bearbeiten"):
    st.session_state.manual_edit = not st.session_state.manual_edit

if st.session_state.manual_edit:
    st.markdown("**✏️ Bearbeite die Paarungen**")
    for idx, (t1, t2) in enumerate(st.session_state.matches):
        c1, c2, c3, c4 = st.columns(4)
        all_options = sorted(st.session_state.players)
        new1 = c1.selectbox(f"Match {idx+1} – Team A Spieler 1", all_options, index=all_options.index(t1[0]), key=f"m_{idx}_0")
        new2 = c2.selectbox(f"Spieler 2", all_options, index=all_options.index(t1[1]), key=f"m_{idx}_1")
        new3 = c3.selectbox(f"Team B Spieler 1", all_options, index=all_options.index(t2[0]), key=f"m_{idx}_2")
        new4 = c4.selectbox(f"Spieler 2", all_options, index=all_options.index(t2[1]), key=f"m_{idx}_3")
        st.session_state.matches[idx] = ([new1, new2], [new3, new4])

    if st.session_state.byes:
        st.markdown("**✏️ Spielfreie Spieler bearbeiten**")
        bye_edit = st.multiselect("Spielfrei (max 3)", options=sorted(st.session_state.players), default=st.session_state.byes)
        if len(bye_edit) <= 3:
            st.session_state.byes = bye_edit

# Anzeige der Matches & Ergebnis-Eingabe
st.header(f"Runde {st.session_state.round + 1}")
st.session_state.results_input = {}
for i, (t1, t2) in enumerate(st.session_state.matches):
    col1 = st.columns(1)[0]
    with col1:
        st.markdown(f"**Match {i+1}:** {t1[0]} & {t1[1]} vs {t2[0]} & {t2[1]}")
        st.session_state.results_input[i] = st.text_input(f"Ergebnis {i+1} (z. B. 4:2)", key=f"res_{st.session_state.round}_{i}")

if st.session_state.byes:
    st.markdown("**Spielfrei:** " + ", ".join(st.session_state.byes))

if st.button("✅ Ergebnisse eintragen"):
    round_results = {}
    valid = True
    for i, (t1, t2) in enumerate(st.session_state.matches):
        result = st.session_state.results_input[i].strip()
        if not result:
            for p in t1 + t2:
                round_results[p] = ('X', 'X')
            continue
        try:
            score1, score2 = map(int, result.split(":"))
        except:
            st.error(f"Ungültiges Ergebnis bei Match {i+1}")
            valid = False
            break
        if score1 > score2:
            for p in t1:
                round_results[p] = (score1 - score2, 1)
            for p in t2:
                round_results[p] = (score2 - score1, 0)
        else:
            for p in t1:
                round_results[p] = (score1 - score2, 0)
            for p in t2:
                round_results[p] = (score2 - score1, 1)

    if valid:
        for p in st.session_state.players:
            if p in round_results:
                d, s = round_results[p]
                st.session_state.scores[p].append(s)
                st.session_state.differentials[p].append(d)
            else:
                st.session_state.scores[p].append('X')
                st.session_state.differentials[p].append('X')
        st.session_state.round += 1
        st.success("Runde erfolgreich gespeichert!")

# Rangliste anzeigen
st.markdown("---")
st.header("📊 Rangliste")
def sorted_ranking():
    return sorted(
        st.session_state.players,
        key=lambda p: (
            -sum(x for x in st.session_state.scores[p] if x != 'X'),
            -sum(d for d in st.session_state.differentials[p] if d != 'X')
        )
    )

def render_table(data_dict, title, bold_top8=False):
    st.subheader(title)
    ranking = sorted_ranking()
    max_r = max((len(v) for v in data_dict.values()), default=0)
    table = []
    for i, p in enumerate(ranking):
        row = {
            "Spieler": f"**{p}**" if bold_top8 and i < 8 else p,
            "Spiele": sum(1 for x in data_dict[p] if x != 'X')
        }
        for r in range(max_r):
            row[f"R{r+1}"] = data_dict[p][r] if r < len(data_dict[p]) else 'X'
        row["Summe"] = sum(x for x in data_dict[p] if x != 'X')
        table.append(row)

    df = pd.DataFrame(table)
    df.index = [i+1 for i in range(len(df))]  # Start index at 1
    st.dataframe(df)

render_table(st.session_state.scores, "Siege", bold_top8=True)
render_table(st.session_state.differentials, "Spiele")

# Halbfinale anzeigen
st.markdown("---")
st.header("🏆 Halbfinale")
if st.button("Halbfinale anzeigen"):
    top8 = sorted_ranking()[:8]
    if len(top8) < 8:
        st.warning("Nicht genug Spieler für das Halbfinale")
    else:
        hf1 = f"Halbfinale 1: {top8[0]} & {top8[4]} vs {top8[3]} & {top8[7]}"
        hf2 = f"Halbfinale 2: {top8[1]} & {top8[5]} vs {top8[2]} & {top8[6]}"
        st.session_state.semifinals = (hf1, hf2)

if st.session_state.semifinals:
    st.success(st.session_state.semifinals[0])
    st.success(st.session_state.semifinals[1])
