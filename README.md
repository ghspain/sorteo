# Sorteo

## Requirements

- Python 3 - any version will work.

## Instructions

1. Access the [GDG Bevy](https://gdg.community.dev/) or [Luma](https://lu.ma/) Platform and download the participant list to your event in CSV.
2. Get the file below `sorteo.py` and make sure the file is executable by `chmod +x sorteo.py`.
3. Use `./sorteo.py -f <event-participant-list>.csv -w 1` to get 1 winner.
    > You can set more winners. We recommend to go winner by winner, in case the participants have left before the giveaway.
4. Set `-c` option to use only the participants you marked as checked in at the event through Bevy or Luma platform.
    > `./sorteo.py -f <event-participant-list>.csv -w 2 -c`


## Usage

```
usage: sorteo.py [-h] [-f FILE] [-w WINNER_NUMBER] [-c]

options:
  -h, --help            show this help message and exit
  -f, --file FILE       CSV file
  -w, --winner-number WINNER_NUMBER
                        Number of winners.
  -c, --only-checkin    Only allow attendants that have checked in the event.
```
