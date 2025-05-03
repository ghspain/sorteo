#!/usr/bin/env python3
import argparse
import csv
import random

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-f", "--file", help="CSV file")
arg_parser.add_argument("-w", "--winner-number", help="Number of winners.", type=int)
arg_parser.add_argument(
    "-c",
    "--only-checkin",
    help="Only allow attendants that have checked in the event.",
    action="store_true",
    default=False,
)

args = arg_parser.parse_args()

if __name__ == "__main__":

    file = args.file
    if not file:
        print("Indique un fichero")
        exit(1)

    with open(file, newline="") as csvfile:
        participants = list(csv.DictReader(csvfile))
        assistants = list(
            filter(
                lambda p: (
                    (
                        (p.get("Checkin Date (UTC)") or p.get("checked_in_at")) != ""
                        or not args.only_checkin
                    )
                    and "bevylabs" not in (p.get("Email") or p.get("email"))
                ),
                participants,
            )
        )

    if len(assistants) < args.winner_number:
        print("No hay suficientes participantes")
        exit(1)
    for i in range(1, args.winner_number + 1):
        winner = random.choice(assistants)
        assistants.remove(winner)
        print(
            f"Ganador premio {i}:",
            winner.get("First Name") or winner.get("first_name"),
            winner.get("Last Name") or winner.get("last_name"),
            winner.get("Email") or winner.get("email"),
        )
