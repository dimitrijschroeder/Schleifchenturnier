import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from collections import defaultdict

class SchleifchenTurnier:
    def __init__(self, root):
        self.root = root
        self.root.title("Schleifchenturnier GUI")

        self.players = []
        self.rounds_played = 0
        self.scores = defaultdict(list)
        self.differentials = defaultdict(list)

        self.name_entry = tk.Text(root, height=10, width=30)
        self.name_entry.pack(pady=10)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=5)

        self.start_button = tk.Button(self.control_frame, text="Nächste Runde auslosen", command=self.next_round)
        self.start_button.grid(row=0, column=0, padx=5)

        self.submit_button = tk.Button(self.control_frame, text="Ergebnisse eintragen", command=self.submit_results)
        self.submit_button.grid(row=0, column=1, padx=5)

        self.add_button = tk.Button(self.control_frame, text="Spieler hinzufügen", command=self.add_player)
        self.add_button.grid(row=0, column=2, padx=5)

        self.remove_button = tk.Button(self.control_frame, text="Spieler entfernen", command=self.remove_player)
        self.remove_button.grid(row=0, column=3, padx=5)

        self.half_final_button = tk.Button(self.control_frame, text="Halbfinale anzeigen", command=self.show_semifinals)
        self.half_final_button.grid(row=0, column=4, padx=5)

        self.matches_frame = tk.Frame(root)
        self.matches_frame.pack(pady=10)

        self.tables_frame = tk.Frame(root)
        self.tables_frame.pack(pady=10)

    def add_player(self):
        new_player = simpledialog.askstring("Spieler hinzufügen", "Name des Spielers:")
        if new_player and new_player not in self.players:
            self.players.append(new_player)
            self.scores[new_player] = ['X'] * self.rounds_played
            self.differentials[new_player] = ['X'] * self.rounds_played
            self.render_tables()

    def remove_player(self):
        remove_player = simpledialog.askstring("Spieler entfernen", "Name des Spielers:")
        if remove_player in self.players:
            self.players.remove(remove_player)
            del self.scores[remove_player]
            del self.differentials[remove_player]
            self.render_tables()

    def next_round(self):
        if not self.players:
            self.players = [name.strip() for name in self.name_entry.get("1.0", tk.END).split("\n") if name.strip()]
            for player in self.players:
                self.scores[player] = []
                self.differentials[player] = []

        if len(self.players) < 4:
            messagebox.showwarning("Nicht genug Spieler", "Mindestens 4 Spieler werden benötigt.")
            return

        for widget in self.matches_frame.winfo_children():
            widget.destroy()

        players_with_games = sorted(self.players, key=lambda p: sum(1 for x in self.scores[p] if x != 'X'))
        games_dict = defaultdict(list)
        for p in players_with_games:
            games_played = sum(1 for x in self.scores[p] if x != 'X')
            games_dict[games_played].append(p)

        grouped_sorted_players = []
        for game_count in sorted(games_dict.keys()):
            group = games_dict[game_count]
            random.shuffle(group)
            grouped_sorted_players.extend(group)

        temp_players = grouped_sorted_players[:]
        self.current_matches = []

        while len(temp_players) >= 4:
            team1 = [temp_players.pop(0), temp_players.pop(0)]
            team2 = [temp_players.pop(0), temp_players.pop(0)]
            self.current_matches.append((team1, team2))

        self.bye_players = temp_players

        self.match_vars = []
        for i, match in enumerate(self.current_matches):
            team1, team2 = match
            var = tk.StringVar()
            lbl = tk.Label(self.matches_frame, text=f"Match {i+1}: {team1[0]} & {team1[1]} vs {team2[0]} & {team2[1]}")
            lbl.pack(anchor="w")
            entry = tk.Entry(self.matches_frame, textvariable=var, width=8)
            entry.pack(anchor="w", padx=10)
            self.match_vars.append((team1, team2, var))

        for p in self.bye_players:
            lbl = tk.Label(self.matches_frame, text=f"{p} hat spielfrei")
            lbl.pack()

    def submit_results(self):
        self.rounds_played += 1
        round_results = {}
        for team1, team2, var in self.match_vars:
            try:
                result = var.get().strip()
                score1, score2 = map(int, result.split(":"))
            except:
                messagebox.showerror("Fehler", f"Ungültiges Ergebnis für Match: {team1} vs {team2}")
                return

            if score1 > score2:
                for player in team1:
                    round_results[player] = (score1 - score2, 1)
                for player in team2:
                    round_results[player] = (score2 - score1, 0)
            else:
                for player in team1:
                    round_results[player] = (score1 - score2, 0)
                for player in team2:
                    round_results[player] = (score2 - score1, 1)

        for player in self.players:
            if player in round_results:
                diff, points = round_results[player]
                self.scores[player].append(points)
                self.differentials[player].append(diff)
            else:
                self.scores[player].append('X')
                self.differentials[player].append('X')

        self.render_tables()

    def render_tables(self):
        for widget in self.tables_frame.winfo_children():
            widget.destroy()

        def sort_by_total(data):
            return sorted(
                data.items(),
                key=lambda item: (
                    -sum(v for v in item[1] if v != 'X'),
                    -sum(self.differentials[item[0]][i] if self.differentials[item[0]][i] != 'X' else 0 for i in range(len(item[1])))
                )
            )

        def create_table(frame, data, title):
            table_frame = tk.Frame(frame)
            table_frame.pack(pady=5)
            tk.Label(table_frame, text=title, font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=25)
            tk.Label(table_frame, text="Platz").grid(row=1, column=0)
            tk.Label(table_frame, text="Spieler").grid(row=1, column=1)
            tk.Label(table_frame, text="Spiele").grid(row=1, column=2)

            max_rounds = max(len(r) for r in data.values())
            for r in range(max_rounds):
                tk.Label(table_frame, text=f"R{r+1}").grid(row=1, column=3 + r)

            tk.Label(table_frame, text="Summe").grid(row=1, column=3 + max_rounds)

            sorted_data = sort_by_total(data)
            for i, (player, results) in enumerate(sorted_data):
                tk.Label(table_frame, text=str(i+1)).grid(row=2+i, column=0)
                tk.Label(table_frame, text=player).grid(row=2+i, column=1)
                games_played = sum(1 for x in results if x != 'X')
                tk.Label(table_frame, text=str(games_played)).grid(row=2+i, column=2)
                total = 0
                for j, val in enumerate(results):
                    display = str(val)
                    if val != 'X':
                        total += val
                    tk.Label(table_frame, text=display).grid(row=2+i, column=3+j)
                tk.Label(table_frame, text=str(total)).grid(row=2+i, column=3 + max_rounds)
                if i == 7:
                    tk.Frame(table_frame, height=2, bd=1, relief="sunken").grid(row=3+i, column=0, columnspan=25, sticky="we")

        create_table(self.tables_frame, self.scores, "Schleifchen-Tabelle")
        create_table(self.tables_frame, self.differentials, "Differenz-Tabelle")

    def show_semifinals(self):
        ranking = sorted(self.players, key=lambda p: (
            -sum(v for v in self.scores[p] if v != 'X'),
            -sum(d for d in self.differentials[p] if d != 'X')
        ))
        top8 = ranking[:8]
        if len(top8) < 8:
            messagebox.showinfo("Halbfinale", "Weniger als 8 Spieler im Ranking – Halbfinale kann nicht gebildet werden.")
            return

        hf1 = f"Halbfinale 1: ({top8[0]} & {top8[4]}) vs ({top8[3]} & {top8[7]})"
        hf2 = f"Halbfinale 2: ({top8[1]} & {top8[5]}) vs ({top8[2]} & {top8[6]})"
        messagebox.showinfo("Halbfinalpaarungen", f"{hf1}\n{hf2}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchleifchenTurnier(root)
    root.mainloop()
