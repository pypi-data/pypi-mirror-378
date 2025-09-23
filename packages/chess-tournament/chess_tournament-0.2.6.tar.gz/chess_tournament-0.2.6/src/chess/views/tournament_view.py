"""View for displaying tournaments and their details."""


class TournamentView:
    """View for displaying tournaments and their details."""

    def display_no_tournaments(self):
        """Display a message when no tournaments exist."""
        print("No tournaments registered.")

    def display_adding_players(self, tournament):
        """Display a message indicating players are being added to a tournament."""
        print(f"Adding players to tournament '{tournament.name}'.")

    def display_invalid_number(self):
        """Display a message indicating the entered number is invalid."""
        print("Invalid number entered.")

    def display_empty_id_error(self):
        """Display a message indicating the player ID cannot be empty."""
        print("Player ID cannot be empty.")

    def display_player_already_registered(self):
        """Display a message indicating the player is already registered."""
        print("Player is already registered in this tournament.")

    def display_player_added(self, player):
        """Display a message confirming that a player has been added."""
        print(f"Player {player.last_name} {player.first_name} added successfully.")

    def display_player_not_found(self):
        """Display a message indicating the player was not found."""
        print("Player not found in the database.")

    def display_total_players(self, tournament):
        """Display the total number of players in the tournament."""
        print(
            f"Total players in tournament '{tournament.name}': "
            f"{len(tournament.players)}"
        )

    def display_tournaments(self, tournaments):
        """Display the list of tournaments with their details."""
        if not tournaments:
            self.display_no_tournaments()
            return
        print("=== List of Tournaments ===")
        for t in tournaments:
            print(
                f"- {t.name} ({t.location}), {t.start_date} → {t.end_date}, "
                f"{t.number_of_rounds} rounds"
            )

    def display_tournament_details(self, tournament):
        """Display the details of a selected tournament."""
        print(f"\n=== Tournament Details: {tournament.name} ===")
        print(f"Location: {tournament.location}")
        print(f"Dates: {tournament.start_date} → {tournament.end_date}")
        print(f"Number of rounds: {tournament.number_of_rounds}")

        print("\nRegistered Players:")
        if tournament.players:
            for player in tournament.players:
                print(
                    f"  - {player.last_name} {player.first_name} "
                    f"({player.id_national})"
                )
        else:
            print("  No players registered.")

        print("\nRounds:")
        if tournament.rounds:
            for rnd in tournament.rounds:
                print(f"  - {rnd.name} ({rnd.start_date} → {rnd.end_date})")
        else:
            print("  No rounds recorded.")

    def display_standings(self, tournament):
        """Display the standings of players for a given tournament."""
        if not tournament.players:
            print("No players to rank.")
            return

        print(f"\n=== Tournament Standings: {tournament.name} ===")
        sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
        for idx, player in enumerate(sorted_players, 1):
            print(f"{idx}. {player.last_name} {player.first_name} - {player.score} pts")

    def display_rounds_and_matches(self, tournament):
        """Display rounds and associated matches for each round."""
        if not tournament.rounds:
            print("No rounds to display.")
            return

        print(f"\n=== Rounds and Matches: {tournament.name} ===")
        for rnd in tournament.rounds:
            print(f"\nRound: {rnd.name} ({rnd.start_date} → {rnd.end_date})")
            if rnd.matches:
                for match in rnd.matches:
                    print(
                        f"  {match.player_white.last_name} "
                        f"vs {match.player_black.last_name} : {match.score}"
                    )
            else:
                print("  No matches recorded.")

    def display_results(self, tournament):
        """Display match results and player scores."""
        if not tournament.rounds:
            print("No results to display.")
            return

        print(f"\n=== Match Results: {tournament.name} ===")
        for rnd in tournament.rounds:
            print(f"\nRound: {rnd.name}")
            if rnd.matches:
                for match in rnd.matches:
                    print(
                        f"  {match.player_white.last_name} "
                        f"vs {match.player_black.last_name} : {match.score}"
                    )
            else:
                print("  No matches recorded.")

        print("\nPlayer Scores:")
        if tournament.players:
            for player in tournament.players:
                print(f"{player.last_name} {player.first_name} : {player.score} pts")
        else:
            print("  No players registered.")
