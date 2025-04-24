import streamlit as st
import random
from collections import defaultdict
import pandas as pd

# Hilfsfunktionen
def team_key(t1, t2):
    return frozenset([frozenset(t1), frozenset(t2)])

def has_played_before(t1, t2):
    return team_key(t1, t2) in st.session_state.pair_history

def update_pair_history(t1, t2):
    st.session_state.pair_history.add(team_key(t1, t2))

def highlight_match(t1, t2):
    return "red" if has_played_before(t1, t2) else "black"

# 🧠 Session state initialisieren
if 'players' not in st.session_state:
    st.session_state.players = []
if 'scores' not in st.session_state:
    st.session_state.scores = defaultdict(list)
if 'differentials' not in st.session_state:
    st.session_state.differentials = defaultdict(list)
if 'round' not in st.session_state:
    st.session_state.round = 0
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'byes' not in st.session_state:
    st.session_state.byes = []
if 'semifinals' not in st.session_state:
    st.session_state.semifinals = None
if 'manual_edit' not in st.session_state:
    st.session_state.manual_edit = False
if 'pair_history' not in st.session_state:
    st.session_state.pair_history = set()
if 'history' not in st.session_state:
    st.session_state.history = []

# Titel
st.set_page_config(page_title="Fast Four Tournament", layout="wide")
st.title("🎾 Fast 4")

# Spielerliste laden
st.header("📥 Spielerliste")
loaded_names = st.text_area("Spieler (ein Name pro Zeile)")
if st.button("📂 Liste laden"):
    names = [n.strip() for n in loaded_names.strip().split("\n") if n.strip()]
    st.session_state.players = []
    st.session_state.scores.clear()
    st.session_state.differentials.clear()
    for n in names:
        st.session_state.players.append(n)
        st.session_state.scores[n] = ['X'] * st.session_state.round
        st.session_state.differentials[n] = ['X'] * st.session_state.round

# Spieler-Eingabe & Verwaltung
st.subheader("Liste bearbeiten")
col1, col2 = st.columns(2)
with col1:
    with st.form(key="add_player_form", clear_on_submit=True, border=False):
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
if col1.button("🎲 Auslosen"):
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

if col2.button("✏️ Bearbeiten"):
    st.session_state.manual_edit = not st.session_state.manual_edit

# ⚙️ Erweiterter Bearbeitungsmodus mit Validierung
if st.session_state.manual_edit:
    st.markdown("**✏️ Paarungen bearbeiten**")
    used_names = set()
    name_counts = defaultdict(int)

    def color_name(name):
        if name_counts[name] > 1:
            return f"🟥 {name}"
        return name

    for idx, (t1, t2) in enumerate(st.session_state.matches):
        c1, c2, c3, c4 = st.columns(4)
        all_players = st.session_state.players[:]

        current_names = t1 + t2
        for name in current_names:
            name_counts[name] += 1

        new1 = c1.selectbox(f"Match {idx+1} A1", all_players, index=all_players.index(t1[0]), key=f"m{idx}_a1")
        new2 = c2.selectbox(f"A2", all_players, index=all_players.index(t1[1]), key=f"m{idx}_a2")
        new3 = c3.selectbox(f"B1", all_players, index=all_players.index(t2[0]), key=f"m{idx}_b1")
        new4 = c4.selectbox(f"B2", all_players, index=all_players.index(t2[1]), key=f"m{idx}_b2")

        # Spielerzähler aktualisieren
        name_counts[new1] += 1
        name_counts[new2] += 1
        name_counts[new3] += 1
        name_counts[new4] += 1

        used_names.update([new1, new2, new3, new4])

        # Überprüfe auf doppelte Paarungen
        team_duplicate = has_played_before([new1, new2], [new3, new4])

        def label_with_flag(name, is_team_repeated):
            if name_counts[name] > 1 or is_team_repeated:
                return f"🟥 {name}"
            return name

        st.session_state.matches[idx] = ([new1, new2], [new3, new4])
        c1.markdown(label_with_flag(new1, team_duplicate))
        c2.markdown(label_with_flag(new2, team_duplicate))
        c3.markdown(label_with_flag(new3, team_duplicate))
        c4.markdown(label_with_flag(new4, team_duplicate))

    not_assigned = sorted(set(st.session_state.players) - used_names)
    st.markdown("**🛋️ Nicht eingeteilt:** " + (", ".join(not_assigned) if not_assigned else "–"))

# 📝 Anzeige der aktuellen Runde
st.subheader(f"📝 Runde {st.session_state.round + 1}")

# Anzeige der Paarungen mit Wiederholungsprüfung
for i, (t1, t2) in enumerate(st.session_state.matches):
    color = highlight_match(t1, t2)
    st.markdown(
        f"<span style='color:{color}'>Match {i+1}: {t1[0]} & {t1[1]} vs {t2[0]} & {t2[1]}</span>",
        unsafe_allow_html=True
    )

# Spielfrei anzeigen
if st.session_state.byes:
    st.markdown("**🛋️ Spielfrei:** " + ", ".join(st.session_state.byes))

# Eingabefelder für Ergebnisse
st.subheader("🎯 Ergebnisse eingeben")
if 'results_input' not in st.session_state:
    st.session_state.results_input = {}

for i, (t1, t2) in enumerate(st.session_state.matches):
    label = f"Match {i+1}: {t1[0]} & {t1[1]} vs {t2[0]} & {t2[1]}"
    st.session_state.results_input[i] = st.text_input(label, key=f"res_{st.session_state.round}_{i}")

# Ergebnisse auswerten
if st.button("✅ Ergebnisse eintragen"):
    round_results = {}
    history_entry = []
    valid = True

    for i, (t1, t2) in enumerate(st.session_state.matches):
        result = st.session_state.results_input.get(i, "").strip()
        match_text = f"{t1[0]} & {t1[1]} vs {t2[0]} & {t2[1]}"
        if not result:
            for p in t1 + t2:
                round_results[p] = ('X', 'X')
            history_entry.append(f"{match_text}: nicht gespielt")
            continue
        try:
            score1, score2 = map(int, result.split(":"))
        except:
            st.error(f"❌ Ungültiges Ergebnis bei Match {i+1}")
            valid = False
            break

        # Sieger bekommt Schleifchen (1), Verlierer 0
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

        history_entry.append(f"{match_text}: {score1}:{score2}")

        # Paarung zur Historie hinzufügen
        update_pair_history(t1, t2)

    # Ergebnisse speichern
    if valid:
        for p in st.session_state.players:
            if p in round_results:
                d, s = round_results[p]
                st.session_state.scores[p].append(s)
                st.session_state.differentials[p].append(d)
            else:
                st.session_state.scores[p].append('X')
                st.session_state.differentials[p].append('X')

        st.session_state.history.append((st.session_state.round + 1, history_entry))
        st.session_state.round += 1
        st.success("Runde erfolgreich gespeichert! ✅")

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
            "Spieler": f"{p}  (✓)" if bold_top8 and i < 8 else p,
            "Spiele": sum(1 for x in data_dict[p] if x != 'X')
        }
        for r in range(max_r):
            row[f"R{r+1}"] = data_dict[p][r] if r < len(data_dict[p]) else 'X'
        row["∑"] = sum(x for x in data_dict[p] if x != 'X')
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

# Erweiterte Match-History anzeigen
st.markdown("---")
st.subheader("📜 History aller Runden")
for rnd, matches in st.session_state.history:
    st.markdown(f"**Runde {rnd}:**")
    for m in matches:
        st.markdown(f"- {m}")
    # Spielfrei anzeigen
    eingesetzte = set()
    for m in matches:
        names = m.split(":")[0].replace(" & ", ";").replace(" vs ", ";").split(";")
        eingesetzte.update([n.strip() for n in names])
    spielfrei = sorted(set(st.session_state.players) - eingesetzte)
    if spielfrei:
        st.markdown(f"🛋️ Spielfrei: {', '.join(spielfrei)}")
