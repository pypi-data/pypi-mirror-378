"""Controller for tournament-related operations."""

import json
import os
import logging
import random
from datetime import date
from jinja2 import Environment, PackageLoader
from chess.models.tournament import Tournament
from chess.models.round import Round
from chess.models.match import Match
from chess.views.tournament_view import TournamentView

logger = logging.getLogger(__name__)


def get_valid_result_input():
    """
    Prompt the user for a match result and return a valid score list.

    Keeps prompting until a valid input is received.
    """
    result_map = {"1": [1, 0], "2": [0, 1], "0": [0.5, 0.5]}
    user_input = ""

    while user_input not in result_map:
        user_input = input("Enter result (1 for win, 2 for loss, 0 for draw): ").strip()
        if user_input not in result_map:
            print("Invalid input. Please use '1', '2', or '0'.")

    return result_map[user_input]


class TournamentController:
    """Handles tournament operations such as creation, loading, and saving."""

    FILE_PATH = "data/tournaments.json"

    def __init__(self, player_controller):
        """Initialize the tournament controller and ensure JSON file exists."""
        self.player_controller = player_controller
        self.view = TournamentView()
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                f.write("[]")

    def load_tournaments(self) -> list[Tournament]:
        """Load tournaments from JSON file."""
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return []
                return [Tournament.from_dict(t) for t in json.loads(data)]
        except FileNotFoundError:
            return []

    def save_tournaments(self, tournaments: list[Tournament]) -> None:
        """Save tournaments to JSON file."""
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tournaments], f, indent=4)

    def create_tournament(self):
        """Prompt user and create a new tournament."""
        name = input("Tournament name: ").strip()
        location = input("Location: ").strip()
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        description = input("Description (optional): ").strip()

        tournament = Tournament(
            name=name,
            location=location,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            current_round=0,
            rounds=[],
            players=[],
            description=description,
        )

        tournaments = self.load_tournaments()
        tournaments.append(tournament)
        self.save_tournaments(tournaments)
        logger.info("Tournament '%s' created successfully.", name)

    def list_tournaments(self):
        """Show list of tournaments."""
        tournaments = self.load_tournaments()
        if not tournaments:
            self.view.display_no_tournaments()
            return
        self.view.display_tournaments(tournaments)

    def add_players(self):
        """Add players to the last created tournament."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournament exists. Please create one first.")
            return

        tournament = tournaments[-1]
        self.view.display_adding_players(tournament)
        nb_input = input("How many players do you want to add? ").strip()
        if not nb_input.isdigit() or int(nb_input) <= 0:
            self.view.display_invalid_number()
            return

        nb_to_add = int(nb_input)
        existing_ids = {p.id_national for p in tournament.players}

        for i in range(nb_to_add):
            player_id = input(f"Enter player's national ID {i+1}: ").strip()
            if not player_id:
                self.view.display_empty_id_error()
                continue
            if player_id in existing_ids:
                self.view.display_player_already_registered()
                continue

            player = self.player_controller.find_player_by_id(player_id)
            if player:
                tournament.players.append(player)
                existing_ids.add(player.id_national)
                self.view.display_player_added(player)
            else:
                self.view.display_player_not_found()

        self.save_tournaments(tournaments)
        self.view.display_total_players(tournament)

    def start_round(self):
        """Start the next round of the most recent tournament."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]
        if tournament.current_round >= tournament.number_of_rounds:
            print("All rounds have been played. The tournament is finished.")
            return

        if tournament.current_round > 0:
            prev_round = tournament.rounds[tournament.current_round - 1]
            if prev_round.end_time is None:
                print("Unable to start a new round. Enter previous results first.")
                return

        if not tournament.players:
            print("Cannot start a round. No players registered.")
            return

        if len(tournament.players) % 2 != 0:
            print("Cannot start a round. Even number of players required.")
            return

        players = tournament.players
        if tournament.current_round == 0:
            random.shuffle(players)
        else:
            players = sorted(players, key=lambda p: p.score, reverse=True)

        matches = []
        to_pair = players[:]

        while to_pair:
            player_white = to_pair.pop(0)
            for i, player_black in enumerate(to_pair):
                already_played = any(
                    player_white.id_national
                    in {m.player_white.id_national, m.player_black.id_national}
                    and player_black.id_national
                    in {m.player_white.id_national, m.player_black.id_national}
                    for r in tournament.rounds
                    for m in r.matches
                )
                if not already_played:
                    matches.append(Match(player_white, player_black, [0, 0]))
                    to_pair.pop(i)
                    break

        new_round = Round(tournament.current_round + 1)
        new_round.matches = matches
        tournament.rounds.append(new_round)
        tournament.current_round += 1
        self.save_tournaments(tournaments)
        self.view.display_rounds_and_matches(tournament)

    def enter_results(self):
        """Enter results for the current round and update player scores."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]
        if not tournament.rounds:
            print("No rounds started yet.")
            return

        current_round = tournament.rounds[-1]
        if current_round.end_time is not None:
            print("Results already entered for this round.")
            return

        if not current_round.matches:
            print("No matches to enter results for.")
            return

        for match in current_round.matches:
            score = get_valid_result_input()
            match.score = score
            if score == [1, 0]:
                match.player_white.score += 1
            elif score == [0, 1]:
                match.player_black.score += 1
            else:
                match.player_white.score += 0.5
                match.player_black.score += 0.5

        current_round.close()
        self.save_tournaments(tournaments)
        self.view.display_results(tournament)

    def show_standings(self):
        """Display current standings for the last tournament."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]
        self.view.display_standings(tournament)

    def export_full_tournament_report_html(
        self, tournament, filename="tournament_report.html"
    ):
        """Export full tournament report to HTML, including rounds and standings."""
        sorted_players = sorted(
            tournament.players,
            key=lambda p: (p.last_name.lower(), p.first_name.lower()),
        )

        scores = {p.id_national: 0.0 for p in tournament.players}
        for rnd in tournament.rounds:
            for match in rnd.matches:
                scores[match.player_white.id_national] += match.score[0]
                scores[match.player_black.id_national] += match.score[1]

        sorted_standings = sorted(
            tournament.players,
            key=lambda p: scores.get(p.id_national, 0.0),
            reverse=True,
        )

        env = Environment(loader=PackageLoader("chess", "templates"))
        template = env.get_template("tournament_report.html.j2")
        html_content = template.render(
            tournament=tournament,
            sorted_players=sorted_players,
            scores=scores,
            sorted_standings=sorted_standings,
        )

        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Full tournament HTML report exported successfully: {filepath}")

    def export_report(self):
        """Export the last created tournament to HTML."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]
        filename = f"{tournament.name.replace(' ', '_')}_report.html"
        self.export_full_tournament_report_html(tournament, filename)
