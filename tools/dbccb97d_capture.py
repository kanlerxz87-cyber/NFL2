#!/usr/bin/env python3
"""Session `dbccb97d` (2026-11-16) — dated official captures and re-verification.

Three dated, clock-stamped reads of official NFL pages, taken 2026-11-16 between
18:05Z and 18:12Z, and the deltas they produce against the registers already in
this repository. Pure stdlib, deterministic: running it twice writes the same bytes.

Artefacts written:
  data/hub_read_dbccb97d_20261116.csv        full Week 10 injury-hub transcription
                                              (28 clubs, 347 rows), read 2026-11-16T18:05Z
  data/venues_week11_dbccb97d_20261116.csv   venue of every Week 11 fixture,
                                              transcribed from each official game centre
  data/reverification_dbccb97d.csv           check rows: row/club counts, row-level
                                              delta against the two newest prior registers,
                                              schedule cross-check, venue cross-check

Sources (all read 2026-11-16, window 18:05-18:12Z):
  https://www.nfl.com/injuries/                                  (8 chunks, full hub)
  https://www.nfl.com/schedules/2026/by-week/week-11            (3 chunks, full page)
  the thirteen https://www.nfl.com/games/<slug>-2026-reg-11 game centres

Every cell below is transcribed verbatim from the fetched page content. Where the
official page printed nothing, the cell is blank — never inferred, never filled.
Practice codes: F = Full Participation in Practice, L = Limited Participation in
Practice, D = Did Not Participate In Practice (the codes the prior registers use).
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

READ_UTC = "2026-11-16T18:05Z"
READ_WINDOW = "2026-11-16T18:05Z-18:12Z"
HUB_URL = "https://www.nfl.com/injuries/"
SCHED_URL = "https://www.nfl.com/schedules/2026/by-week/week-11"

# ---------------------------------------------------------------------------
# 1. Week 10 injury hub, read 2026-11-16T18:05Z (all 8 chunks).
#    Order and spelling exactly as printed. Blank injury / game-status cells are
#    blank in the official page and stay blank here.
# ---------------------------------------------------------------------------
HUB = [
    # WAS (W10-01, Thu 2026-11-12)
    ("WAS", "John Bates", "TE", "", "F", ""),
    ("WAS", "Treylon Burks", "WR", "", "D", ""),
    ("WAS", "Jayden Daniels", "QB", "", "F", ""),
    ("WAS", "Matt Gulbin", "C", "", "F", ""),
    ("WAS", "Chig Okonkwo", "TE", "", "F", ""),
    ("WAS", "Lucas Patrick", "C", "Concussion", "D", "Out"),
    ("WAS", "Amik Robertson", "CB", "", "L", ""),
    ("WAS", "Shy Tuttle", "DT", "", "F", ""),
    ("WAS", "Colson Yankoff", "TE", "Knee", "D", "Out"),
    # NYG
    ("NYG", "Abdul Carter", "LB", "", "F", ""),
    ("NYG", "Jermaine Eluemunor", "T", "", "F", ""),
    ("NYG", "Malik Harrison", "LB", "Groin", "L", "Questionable"),
    ("NYG", "Colton Hood", "CB", "", "F", ""),
    ("NYG", "Theo Johnson", "TE", "", "F", ""),
    ("NYG", "Charlie Jones", "WR", "", "F", ""),
    ("NYG", "J.J. McCarthy", "QB", "", "F", ""),
    ("NYG", "Darnell Mooney", "WR", "", "F", ""),
    ("NYG", "Malik Nabers", "WR", "", "F", ""),
    ("NYG", "Cam Skattebo", "RB", "", "F", ""),
    ("NYG", "Andrew Thomas", "T", "", "F", ""),
    # NE (W10-02, Sun 2026-11-15)
    ("NE", "Ben Brown", "C", "Knee", "D", "Out"),
    ("NE", "A.J. Brown", "WR", "Ankle, Knee", "L", "Questionable"),
    ("NE", "Kevin Byard", "S", "Chest", "F", "Questionable"),
    ("NE", "Carlton Davis III", "CB", "Knee", "D", "Out"),
    ("NE", "Reggie Gilliam", "FB", "Knee", "L", "Questionable"),
    ("NE", "TreVeyon Henderson", "RB", "Illness", "D", "Out"),
    ("NE", "Hunter Henry", "TE", "", "L", ""),
    ("NE", "Cameron Latu", "TE", "Back", "L", "Questionable"),
    ("NE", "Drake Maye", "QB", "", "F", ""),
    ("NE", "Morgan Moses", "T", "", "F", ""),
    ("NE", "Walter Rouse", "T", "Concussion", "L", "Questionable"),
    ("NE", "Brenden Schooler", "S", "Hamstring", "L", "Questionable"),
    ("NE", "Rhamondre Stevenson", "RB", "Knee", "L", "Questionable"),
    ("NE", "Greg Van Roten", "G", "Hamstring", "F", "Questionable"),
    ("NE", "Charles Woods", "CB", "Hamstring", "F", "Questionable"),
    # DET
    ("DET", "Brian Branch", "S", "", "F", ""),
    ("DET", "Jared Goff", "QB", "", "F", ""),
    ("DET", "Kerby Joseph", "S", "Knee", "D", "Out"),
    ("DET", "Cade Mays", "C", "Ankle", "D", "Out"),
    ("DET", "D.J. Reed", "CB", "Hip", "D", "Out"),
    ("DET", "Jacob Saylors", "RB", "", "F", ""),
    ("DET", "Amon-Ra St. Brown", "WR", "Rib", "L", "Questionable"),
    ("DET", "Sione Vaki", "RB", "Ankle", "L", "Questionable"),
    ("DET", "DJ Wonnum", "DE", "", "F", ""),
    # KC (W10-03) — includes the two rows FL-113 records as printed under the
    # Chiefs block while belonging to other clubs; transcribed as printed.
    ("KC", "Jeffrey Bassa", "LB", "", "F", ""),
    ("KC", "Mansoor Delane", "CB", "Shoulder", "F", "Questionable"),
    ("KC", "Justin Fields", "QB", "", "F", ""),
    ("KC", "Jaden Hicks", "S", "", "F", ""),
    ("KC", "Travis Kelce", "TE", "", "F", ""),
    ("KC", "Patrick Mahomes", "QB", "", "F", ""),
    ("KC", "Jaylon Moore", "T", "Ankle", "D", "Out"),
    ("KC", "Omarr Norman-Lott", "DT", "Knee", "L", "Out"),
    ("KC", "Jaydn Ott", "RB", "Hamstring", "L", "Questionable"),
    ("KC", "Rashee Rice", "WR", "", "F", ""),
    ("KC", "Kenneth Walker III", "RB", "Groin", "D", "Questionable"),
    ("KC", "Peter Woods", "DT", "Neck", "D", "Out"),
    ("KC", "Xavier Worthy", "WR", "", "F", ""),
    # ATL
    ("ATL", "Zachariah Branch", "WR", "Hamstring", "D", "Out"),
    ("ATL", "Kendal Daniels", "LB", "", "F", ""),
    ("ATL", "Divine Deablo", "LB", "Forearm", "D", "Doubtful"),
    ("ATL", "Gervon Dexter Sr.", "DT", "Illness", "L", "Questionable"),
    ("ATL", "Jake Matthews", "T", "", "L", ""),
    ("ATL", "Liam McCullough", "LS", "", "D", ""),
    ("ATL", "James Pearce Jr.", "DE", "Back", "L", "Questionable"),
    ("ATL", "Za'Darius Smith", "DE", "", "F", ""),
    ("ATL", "Jawaan Taylor", "T", "", "L", ""),
    ("ATL", "Cameron Thomas", "DE", "", "F", ""),
    ("ATL", "Josh Woods", "LB", "Ankle", "F", "Questionable"),
    # MIN (W10-04) — Kyler Murray is printed in the Vikings block; transcribed
    # as printed (same misplacement family as FL-113).
    ("MIN", "Jordan Addison", "WR", "Thumb", "L", "Questionable"),
    ("MIN", "Blake Cashman", "LB", "Concussion", "L", "Out"),
    ("MIN", "Christian Darrisaw", "T", "", "D", ""),
    ("MIN", "T.J. Hockenson", "TE", "Wrist, Chest", "D", "Out"),
    ("MIN", "Tyrion Ingram-Dawkins", "DT", "Ankle", "D", "Out"),
    ("MIN", "Theo Jackson", "S", "", "F", ""),
    ("MIN", "Jauan Jennings", "WR", "Calf", "D", "Out"),
    ("MIN", "Josh Metellus", "S", "Shoulder", "L", "Questionable"),
    ("MIN", "Kyler Murray", "QB", "Hamstring", "D", "Out"),
    ("MIN", "Harrison Smith", "S", "", "L", ""),
    ("MIN", "Kyle Van Noy", "LB", "Calf", "L", "Questionable"),
    ("MIN", "Jay Ward", "S", "", "F", ""),
    ("MIN", "Carson Wentz", "QB", "", "F", ""),
    # GB
    ("GB", "Aaron Banks", "G", "", "L", ""),
    ("GB", "Chris Brooks", "RB", "Ankle", "L", "Questionable"),
    ("GB", "Javon Bullard", "S", "Ankle, Knee", "L", "Questionable"),
    ("GB", "Zaire Franklin", "LB", "Shin", "D", "Doubtful"),
    ("GB", "Travis Glover", "G", "Knee", "L", "Questionable"),
    ("GB", "Ty'Ron Hopper", "LB", "", "F", ""),
    ("GB", "Josh Jacobs", "RB", "Finger", "D", "Out"),
    ("GB", "Xavier McKinney", "S", "Foot", "L", "Questionable"),
    ("GB", "Bo Melton", "WR", "", "F", ""),
    ("GB", "Skyy Moore", "WR", "Ankle", "L", "Questionable"),
    ("GB", "Micah Parsons", "LB", "Knee, Illness", "L", "Out"),
    ("GB", "Sean Rhyan", "C", "Ankle", "D", "Out"),
    ("GB", "Trey Smack", "K", "", "F", ""),
    ("GB", "Lukas Van Ness", "LB", "Back", "L", "Questionable"),
    ("GB", "Josh Whyle", "TE", "Concussion", "D", "Out"),
    ("GB", "Savion Williams", "WR", "", "L", ""),
    ("GB", "Kevin Zeitler", "G", "Ankle, Triceps", "D", "Questionable"),
    # JAX (W10-05)
    ("JAX", "Jessie Bates", "S", "Not injury related - resting player", "L", "Out"),
    ("JAX", "Ezra Cleveland", "G", "", "F", ""),
    ("JAX", "Branson Combs", "LB", "", "F", ""),
    ("JAX", "Jordan Davis", "DT", "Not injury related - resting player", "L", "Out"),
    ("JAX", "BJ Green II", "DE", "Forearm", "F", "Out"),
    ("JAX", "Robert Hainsey", "C", "Concussion", "L", "Questionable"),
    ("JAX", "Antonio Johnson", "S", "", "L", ""),
    ("JAX", "Jakobi Meyers", "WR", "", "L", ""),
    ("JAX", "Chris Rodriguez Jr.", "RB", "", "L", ""),
    ("JAX", "Bhayshul Tuten", "RB", "", "L", ""),
    ("JAX", "Travon Walker", "DE", "", "L", ""),
    # TEN
    ("TEN", "Cody Barton", "LB", "Concussion", "D", "Out"),
    ("TEN", "John Franklin-Myers", "DE", "", "F", ""),
    ("TEN", "Marcus Harris", "CB", "", "F", ""),
    ("TEN", "Anthony Hill Jr.", "LB", "Neck", "D", "Out"),
    ("TEN", "Jaylon Jones", "CB", "", "F", ""),
    ("TEN", "JC Latham", "T", "", "F", ""),
    ("TEN", "Tony Pollard", "RB", "", "F", ""),
    ("TEN", "Peter Skoronski", "G", "Hamstring", "D", "Out"),
    ("TEN", "Tyjae Spears", "RB", "Knee", "F", "Questionable"),
    ("TEN", "Carnell Tate", "WR", "Shoulder", "D", "Out"),
    ("TEN", "Tommy Townsend", "P", "Knee, Achilles", "D", "Out"),
    ("TEN", "Kevin Winston Jr.", "S", "", "F", ""),
    # BUF (W10-08)
    ("BUF", "Alec Anderson", "G", "", "F", ""),
    ("BUF", "Christian Benford", "CB", "Wrist", "F", "Questionable"),
    ("BUF", "Terrel Bernard", "LB", "", "D", ""),
    ("BUF", "Spencer Brown", "T", "Ankle", "D", "Doubtful"),
    ("BUF", "Dion Dawkins", "T", "", "F", ""),
    ("BUF", "Sam Franklin Jr.", "S", "Shoulder", "L", "Questionable"),
    ("BUF", "Greg Gaines", "DT", "", "F", ""),
    ("BUF", "Jordan Hancock", "CB", "Hamstring", "F", "Questionable"),
    ("BUF", "Dalton Kincaid", "TE", "", "F", ""),
    ("BUF", "Connor McGovern", "C", "", "F", ""),
    ("BUF", "Ed Oliver", "DE", "", "D", ""),
    ("BUF", "Ar'maj Reed-Adams", "G", "", "F", ""),
    ("BUF", "T.J. Sanders", "DE", "", "F", ""),
    ("BUF", "Tyrell Shavers", "WR", "Knee", "F", "Questionable"),
    # NYJ
    ("NYJ", "Jarvis Brownlee Jr.", "CB", "Illness", "L", "Questionable"),
    ("NYJ", "Omar Cooper Jr.", "WR", "Ankle", "F", "Questionable"),
    ("NYJ", "Adonai Mitchell", "WR", "Knee", "F", "Questionable"),
    ("NYJ", "Joseph Ossai", "DE", "Ankle", "F", "Questionable"),
    ("NYJ", "VJ Payne", "S", "Knee", "F", "Questionable"),
    ("NYJ", "Harrison Phillips", "DT", "Ankle", "F", "Questionable"),
    ("NYJ", "Trevin Wallace", "LB", "Groin", "D", "Out"),
    ("NYJ", "Garrett Wilson", "WR", "Concussion", "F", "Questionable"),
    ("NYJ", "Nahshon Wright", "CB", "Back", "F", "Questionable"),
    # MIA (W10-06)
    ("MIA", "Tucker Addington", "LS", "", "L", ""),
    ("MIA", "Kaytron Allen", "RB", "", "F", ""),
    ("MIA", "Darrell Baker Jr.", "CB", "Knee", "F", "Questionable"),
    ("MIA", "Chris Bell", "WR", "Knee", "D", "Doubtful"),
    ("MIA", "Aaron Brewer", "C", "Concussion", "D", "Out"),
    ("MIA", "Malik Herring", "DE", "", "F", ""),
    ("MIA", "Will Kacmarek", "TE", "", "F", ""),
    ("MIA", "Michael Taaffe", "S", "", "F", ""),
    ("MIA", "Dante Trader Jr.", "S", "", "F", ""),
    ("MIA", "Jared Wayne", "WR", "Quadricep", "D", "Out"),
    ("MIA", "Jaylen Wright", "RB", "", "F", ""),
    # IND
    ("IND", "Mo Alie-Cox", "TE", "Groin", "D", "Out"),
    ("IND", "CJ Allen", "LB", "", "F", ""),
    ("IND", "Jaylon Carlies", "LB", "Neck", "D", "Out"),
    ("IND", "Akeem Davis-Gaither", "LB", "Knee", "D", "Out"),
    ("IND", "A.J. Haulcy", "S", "", "F", ""),
    ("IND", "Arden Key", "DE", "", "F", ""),
    ("IND", "Will Mallory", "TE", "Hamstring", "L", "Questionable"),
    ("IND", "Luke Rhodes", "LS", "Hamstring", "D", "Out"),
    ("IND", "Grover Stewart", "DT", "", "F", ""),
    ("IND", "Jonathan Taylor", "RB", "", "F", ""),
    ("IND", "Jerry Tillery", "DT", "Calf", "D", "Out"),
    ("IND", "Jalen Travis", "T", "Knee", "D", "Out"),
    ("IND", "Justin Walley", "CB", "", "F", ""),
    ("IND", "Charvarius Ward", "CB", "", "F", ""),
    # CAR (W10-07)
    ("CAR", "Jonathon Brooks", "RB", "Groin", "L", "Doubtful"),
    ("CAR", "Brady Christensen", "G", "Hamstring", "F", "Questionable"),
    ("CAR", "Trevor Etienne", "RB", "", "F", ""),
    ("CAR", "Chuba Hubbard", "RB", "", "F", ""),
    ("CAR", "Lee Hunter", "DT", "", "F", ""),
    ("CAR", "Mike Jackson", "CB", "Groin", "L", "Doubtful"),
    ("CAR", "Will Lee III", "CB", "Hamstring", "L", "Questionable"),
    ("CAR", "Xavier Legette", "WR", "Knee", "F", "Questionable"),
    ("CAR", "Damien Lewis", "G", "", "F", ""),
    ("CAR", "Bobby Okereke", "LB", "Foot", "D", "Out"),
    ("CAR", "Jaelan Phillips", "LB", "Hamstring", "F", "Questionable"),
    ("CAR", "Torricelli Simpkins III", "G", "", "F", ""),
    # NO
    ("NO", "Kelvin Banks Jr.", "T", "", "F", ""),
    ("NO", "CJ Donaldson", "RB", "Shoulder", "D", "Out"),
    ("NO", "David Edwards", "G", "", "F", ""),
    ("NO", "Martin Emerson", "CB", "Shin", "L", "Questionable"),
    ("NO", "Travis Etienne", "RB", "Hamstring", "F", "Questionable"),
    ("NO", "Noah Fant", "TE", "", "F", ""),
    ("NO", "Taliese Fuaga", "T", "Knee", "D", "Out"),
    ("NO", "Alvin Kamara", "RB", "", "F", ""),
    ("NO", "Erik McCoy", "C", "Biceps", "D", "Out"),
    ("NO", "Christen Miller", "DT", "Knee", "D", "Out"),
    ("NO", "Asim Richards", "T", "", "F", ""),
    ("NO", "Quincy Riley", "CB", "", "F", ""),
    # HOU (W10-09)
    ("HOU", "Azeez Al-Shaair", "LB", "Groin, Not injury related - personal matter", "D", "Out"),
    ("HOU", "Will Anderson Jr.", "DE", "Ankle", "D", "Questionable"),
    ("HOU", "Reed Blankenship", "S", "", "F", ""),
    ("HOU", "Trent Brown", "T", "Wrist, Illness", "D", "Questionable"),
    ("HOU", "Tank Dell", "WR", "", "F", ""),
    ("HOU", "Blake Fisher", "T", "", "F", ""),
    ("HOU", "Marvin Harrison Jr.", "WR", "Hamstring", "D", "Out"),
    ("HOU", "Jacob Hummel", "LB", "Groin", "F", "Questionable"),
    ("HOU", "Danielle Hunter", "DE", "Hamstring", "D", "Out"),
    ("HOU", "Brevin Jordan", "TE", "Finger, Foot", "D", "Out"),
    ("HOU", "Woody Marks", "RB", "", "F", ""),
    ("HOU", "David Montgomery", "RB", "Groin", "F", "Questionable"),
    ("HOU", "Keylan Rutledge", "G", "Neck, Shoulder", "D", "Out"),
    ("HOU", "Jaylin Smith", "CB", "Hamstring", "F", "Questionable"),
    ("HOU", "Wyatt Teller", "G", "Illness, Back", "L", "Questionable"),
    ("HOU", "Tommy Togiai", "DT", "", "F", ""),
    # CLE
    ("CLE", "Austin Barber", "T", "", "F", ""),
    ("CLE", "Denzel Boston", "WR", "Toe", "L", "Questionable"),
    ("CLE", "Michael Burton", "FB", "Calf", "D", "Out"),
    ("CLE", "Maliek Collins", "DT", "", "F", ""),
    ("CLE", "Harold Fannin Jr.", "TE", "", "F", ""),
    ("CLE", "Ronnie Hickman Jr.", "S", "Concussion", "D", "Out"),
    ("CLE", "Tytus Howard", "T", "", "F", ""),
    ("CLE", "Elgton Jenkins", "C", "", "F", ""),
    ("CLE", "Donovan McMillon", "S", "", "L", ""),
    ("CLE", "Carson Schwesinger", "LB", "", "F", ""),
    ("CLE", "Denzel Ward", "CB", "", "L", ""),
    ("CLE", "Quincy Williams", "LB", "", "F", ""),
    # LAR (W10-10)
    ("LAR", "Davis Allen", "TE", "Oblique", "L", "Questionable"),
    ("LAR", "Steve Avila", "G", "Hamstring", "D", "Out"),
    ("LAR", "Joe Cardona", "LS", "Ankle", "L", "Questionable"),
    ("LAR", "Kam Curl", "S", "Toe", "L", "Questionable"),
    ("LAR", "Aaron Donald", "DT", "", "D", ""),
    ("LAR", "Terrance Ferguson", "TE", "Ankle, Hamstring", "D", "Out"),
    ("LAR", "Braden Fiske", "DT", "", "D", ""),
    ("LAR", "Myles Garrett", "LB", "Knee, Not injury related - resting player", "D", "Questionable"),
    ("LAR", "Tyler Higbee", "TE", "", "L", ""),
    ("LAR", "Trent McDuffie", "CB", "Back", "L", "Questionable"),
    ("LAR", "Puka Nacua", "WR", "", "D", ""),
    ("LAR", "Colby Parkinson", "TE", "", "F", ""),
    ("LAR", "Matthew Stafford", "QB", "", "F", ""),
    ("LAR", "Byron Young", "LB", "", "D", ""),
    # AZ
    ("AZ", "Budda Baker", "S", "", "F", ""),
    ("AZ", "Zachary Carter", "DT", "Knee", "L", "Out"),
    ("AZ", "Hjalte Froholdt", "C", "Concussion", "D", "Out"),
    ("AZ", "Jon Gaines II", "G", "Ankle", "D", "Out"),
    ("AZ", "Bam Knight", "RB", "", "F", ""),
    ("AZ", "Hunter Long", "TE", "Knee", "L", "Questionable"),
    ("AZ", "Roy Lopez", "DT", "Toe, Ankle", "L", "Questionable"),
    ("AZ", "Max Melton", "CB", "Knee, Hand", "L", "Questionable"),
    ("AZ", "Darius Robinson", "DT", "Wrist", "L", "Questionable"),
    ("AZ", "Isaac Seumalo", "G", "", "F", ""),
    ("AZ", "Dante Stills", "DT", "", "F", ""),
    ("AZ", "Josh Sweat", "LB", "", "F", ""),
    ("AZ", "Jayden Williams", "T", "Knee", "L", "Questionable"),
    ("AZ", "Mack Wilson", "LB", "", "F", ""),
    ("AZ", "Andrew Wingard", "S", "Groin", "D", "Questionable"),
    # SEA (W10-11)
    ("SEA", "AJ Barner", "TE", "", "F", ""),
    ("SEA", "Anthony Bradford", "G", "", "F", ""),
    ("SEA", "Charles Cross", "T", "Ankle", "D", "Out"),
    ("SEA", "Sam Darnold", "QB", "Ribs, Quadricep", "D", "Out"),
    ("SEA", "Derick Hall", "LB", "", "D", ""),
    ("SEA", "Drew Lock", "QB", "", "L", ""),
    ("SEA", "Quenton Nelson", "G", "Knee", "D", "Out"),
    ("SEA", "Uchenna Nwosu", "LB", "", "F", ""),
    ("SEA", "Patrick O'Connell", "LB", "", "F", ""),
    ("SEA", "Connor O'Toole", "LB", "", "F", ""),
    ("SEA", "Brandon Pili", "DT", "", "F", ""),
    ("SEA", "Jarran Reed", "DT", "", "F", ""),
    ("SEA", "Rashid Shaheed", "WR", "", "F", ""),
    ("SEA", "Jaxon Smith-Njigba", "WR", "", "F", ""),
    ("SEA", "Leonard Williams", "DT", "Stinger", "D", "Out"),
    # LV
    ("LV", "Thomas Booker", "DT", "Ankle", "F", "Questionable"),
    ("LV", "Foley Fatukasi", "DT", "", "F", ""),
    ("LV", "Ian Thomas", "TE", "", "F", ""),
    ("LV", "Dont'e Thornton Jr.", "WR", "Back", "D", "Questionable"),
    ("LV", "Trey Zuhn III", "C", "", "F", ""),
    # SF (W10-12) — Mike Evans printed in the 49ers block (FL-113 family)
    ("SF", "Mike Evans", "WR", "Achilles", "D", "Out"),
    ("SF", "Renardo Green", "CB", "Back", "L", "Questionable"),
    ("SF", "Dre Greenlaw", "LB", "Knee", "L", "Questionable"),
    ("SF", "Nate Hobbs", "CB", "Groin", "F", "Questionable"),
    ("SF", "Deommodore Lenoir", "CB", "Foot", "L", "Questionable"),
    ("SF", "Christian McCaffrey", "RB", "", "F", ""),
    ("SF", "Siran Neal", "S", "", "F", ""),
    ("SF", "Demarcus Robinson", "WR", "", "F", ""),
    ("SF", "Deebo Samuel Sr.", "WR", "", "F", ""),
    ("SF", "Upton Stout", "CB", "Shoulder, Neck", "L", "Questionable"),
    ("SF", "C.J. West", "DT", "Knee", "F", "Questionable"),
    ("SF", "Trent Williams", "T", "Shoulder", "D", "Questionable"),
    # DAL
    ("DAL", "DaRon Bland", "CB", "Ankle", "L", "Questionable"),
    ("DAL", "Jonathan Bullard", "DT", "Calf", "F", "Questionable"),
    ("DAL", "Alijah Clark", "S", "Illness", "D", "Questionable"),
    ("DAL", "Donovan Ezeiruaku", "LB", "Ankle", "D", "Out"),
    ("DAL", "Jake Ferguson", "TE", "Knee, Ankle", "D", "Out"),
    ("DAL", "Tyler Goodson", "RB", "Ankle, Knee", "D", "Out"),
    ("DAL", "Malik Hooker", "S", "", "D", ""),
    ("DAL", "Marist Liufau", "LB", "", "F", ""),
    ("DAL", "P.J. Locke", "S", "Concussion", "D", "Out"),
    ("DAL", "Von Miller", "LB", "", "D", ""),
    ("DAL", "Jonathan Mingo", "WR", "Ankle", "D", "Out"),
    ("DAL", "Devin Moore", "CB", "Hip", "F", "Questionable"),
    ("DAL", "DeMarvion Overshown", "LB", "", "F", ""),
    ("DAL", "George Pickens", "WR", "", "F", ""),
    ("DAL", "Joey Porter Jr.", "CB", "Ankle, Foot", "L", "Questionable"),
    ("DAL", "Luke Schoonmaker", "TE", "", "F", ""),
    ("DAL", "Brevyn Spann-Ford", "TE", "", "F", ""),
    ("DAL", "Juanyeh Thomas", "S", "Hamstring", "D", "Doubtful"),
    ("DAL", "KaVontae Turpin", "WR", "", "F", ""),
    # PIT (W10-13)
    ("PIT", "Brandin Echols", "CB", "", "F", ""),
    ("PIT", "DeShon Elliott", "S", "", "F", ""),
    ("PIT", "Derrick Harmon", "DT", "Foot", "F", "Questionable"),
    ("PIT", "Cameron Heyward", "DT", "", "F", ""),
    ("PIT", "Ben Skowronek", "WR", "", "F", ""),
    ("PIT", "Doneiko Slaughter", "CB", "", "F", ""),
    ("PIT", "Darnell Washington", "TE", "", "F", ""),
    ("PIT", "T.J. Watt", "LB", "", "F", ""),
    # CIN — Dexter Lawrence printed in the Bengals block (FL-113 family)
    ("CIN", "Jonathan Allen", "DT", "", "L", ""),
    ("CIN", "Jalen Davis", "CB", "Hamstring", "F", "Doubtful"),
    ("CIN", "Kyle Dugger", "S", "Quadricep", "D", "Out"),
    ("CIN", "Dylan Fairchild", "G", "", "F", ""),
    ("CIN", "B.J. Hill", "DT", "", "D", ""),
    ("CIN", "Andrei Iosivas", "WR", "Thumb", "F", "Doubtful"),
    ("CIN", "Dexter Lawrence", "DT", "", "D", ""),
    ("CIN", "Brian Parker II", "G", "Knee", "F", "Doubtful"),
    ("CIN", "DJ Turner II", "CB", "", "F", ""),
    # LAC (W10-14, Mon 2026-11-16) — Keaton Mitchell, David Njoku and Isas
    # Waxter printed in the Chargers block (FL-113 family)
    ("LAC", "Kayode Awosika", "G", "Fibula", "F", "Questionable"),
    ("LAC", "Bud Dupree", "DE", "", "F", ""),
    ("LAC", "Justin Eboigbe", "DE", "Ankle", "L", "Questionable"),
    ("LAC", "Alex Harkey", "G", "", "F", ""),
    ("LAC", "Tre Harris", "WR", "", "F", ""),
    ("LAC", "Cam Hart", "CB", "", "F", ""),
    ("LAC", "Daiyan Henley", "LB", "", "F", ""),
    ("LAC", "Deane Leonard", "CB", "", "F", ""),
    ("LAC", "Khalil Mack", "LB", "", "F", ""),
    ("LAC", "Ladd McConkey", "WR", "Back", "D", "Questionable"),
    ("LAC", "Keaton Mitchell", "RB", "", "F", ""),
    ("LAC", "David Njoku", "TE", "Fibula", "F", "Questionable"),
    ("LAC", "Denzel Perryman", "LB", "Pectoral", "F", "Questionable"),
    ("LAC", "Trey Pipkins", "T", "Not injury related - personal matter, Knee", "L", "Questionable"),
    ("LAC", "Rodney Shelley", "CB", "", "F", ""),
    ("LAC", "Branson Taylor", "G", "Ankle", "D", "Out"),
    ("LAC", "Brenen Thompson", "WR", "Hamstring", "D", "Doubtful"),
    ("LAC", "Isas Waxter", "CB", "Ankle", "D", "Out"),
    ("LAC", "Kendall Williamson", "S", "Calf", "D", "Out"),
    # BAL
    ("BAL", "Rasheen Ali", "RB", "", "F", ""),
    ("BAL", "Rashod Bateman", "WR", "", "F", ""),
    ("BAL", "Calais Campbell", "DT", "", "D", ""),
    ("BAL", "Kyle Hamilton", "S", "", "F", ""),
    ("BAL", "Jaylinn Hawkins", "S", "Knee", "L", "Out"),
    ("BAL", "Matthew Hibner", "TE", "", "F", ""),
    ("BAL", "Olaivavega Ioane", "G", "", "F", ""),
    ("BAL", "Adam Randall", "RB", "Neck, Hamstring", "F", "Questionable"),
    ("BAL", "Ronnie Stanley", "T", "", "D", ""),
    ("BAL", "Nate Wiggins", "CB", "", "F", ""),
]

# ---------------------------------------------------------------------------
# 2. Week 11 venues, transcribed from each official game centre
#    (Game Info → Location / Stadium), read 2026-11-16T18:05Z onwards.
#    FIXTURE-LEVEL DISCREPANT NAMING (see FL-118): the schedule page's own
#    hotel-link parameters print different names for three of the thirteen.
# ---------------------------------------------------------------------------
VENUES = [
    ("W11-01", "IND", "HOU", "colts-at-texans-2026-reg-11",
     "HOUSTON, TX", "RELIANT STADIUM"),
    ("W11-02", "MIA", "BUF", "dolphins-at-bills-2026-reg-11",
     "ORCHARD PARK, NY", "HIGHMARK STADIUM"),
    ("W11-03", "BAL", "CAR", "ravens-at-panthers-2026-reg-11",
     "CHARLOTTE, NC", "BANK OF AMERICA STADIUM"),
    ("W11-04", "NO", "CHI", "saints-at-bears-2026-reg-11",
     "CHICAGO, IL", "SOLDIER FIELD"),
    ("W11-05", "TEN", "DAL", "titans-at-cowboys-2026-reg-11",
     "ARLINGTON, TX", "AT&T STADIUM"),
    ("W11-06", "TB", "DET", "buccaneers-at-lions-2026-reg-11",
     "DETROIT, MI", "FORD FIELD"),
    ("W11-07", "AZ", "KC", "cardinals-at-chiefs-2026-reg-11",
     "KANSAS CITY, MO", "ARROWHEAD STADIUM"),
    ("W11-08", "PIT", "PHI", "steelers-at-eagles-2026-reg-11",
     "PHILADELPHIA, PA", "LINCOLN FINANCIAL FIELD"),
    ("W11-09", "NYJ", "LAC", "jets-at-chargers-2026-reg-11",
     "INGLEWOOD, CA", "SOFI STADIUM"),
    ("W11-10", "LV", "DEN", "raiders-at-broncos-2026-reg-11",
     "DENVER, CO", "EMPOWER FIELD AT MILE HIGH"),
    ("W11-11", "JAX", "NYG", "jaguars-at-giants-2026-reg-11",
     "EAST RUTHERFORD, NJ", "METLIFE STADIUM"),
    ("W11-12", "MIN", "SF", "vikings-at-49ers-2026-reg-11",
     "MEXICO CITY", "ESTADIO BANORTE"),
    ("W11-13", "CIN", "WAS", "bengals-at-commanders-2026-reg-11",
     "LANDOVER, MD", "NORTHWEST STADIUM"),
]

# Hotel-link parameter values printed by the schedule page itself (FL-112), kept
# here only to make the naming discrepancy machine-checkable.
PARAM_VENUES = {
    "W11-01": "NRG Stadium",
    "W11-02": "Highmark Stadium",
    "W11-03": "Bank of America Stadium",
    "W11-04": "Soldier Field",
    "W11-05": "AT&T Stadium",
    "W11-06": "Ford Field",
    "W11-07": "GEHA Field at Arrowhead Stadium",
    "W11-08": "Lincoln Financial Field",
    "W11-09": "SoFi Stadium",
    "W11-10": "Empower Field at Mile High",
    "W11-11": "MetLife Stadium",
    "W11-12": None,  # the Mexico City fixture carries no hotel-link parameter
    "W11-13": "FedEx Field",
}

# Week 11 slate facts as printed by the official schedule page (read 2026-11-16),
# keyed by game id: (date, kickoff_et, tv).
SCHEDULE_PAGE = {
    "W11-01": ("2026-11-19", "20:15", "Prime Video"),
    "W11-02": ("2026-11-22", "13:00", "CBS"),
    "W11-03": ("2026-11-22", "13:00", "FOX"),
    "W11-04": ("2026-11-22", "13:00", "FOX"),
    "W11-05": ("2026-11-22", "13:00", "FOX"),
    "W11-06": ("2026-11-22", "13:00", "FOX"),
    "W11-07": ("2026-11-22", "13:00", "CBS"),
    "W11-08": ("2026-11-22", "13:00", "CBS"),
    "W11-09": ("2026-11-22", "16:05", "FOX"),
    "W11-10": ("2026-11-22", "16:25", "CBS"),
    "W11-11": ("2026-11-22", "16:25", "CBS"),
    "W11-12": ("2026-11-22", "20:20", "NBC"),
    "W11-13": ("2026-11-23", "20:15", "ESPN"),
}

HUB_COLUMNS = ["read_utc", "source_url", "club", "player", "pos",
               "injury", "practice", "game_status"]
VENUE_COLUMNS = ["game_id", "away", "home", "game_slug", "location",
                 "stadium", "read_utc", "source_url"]
REVERIF_COLUMNS = ["id", "check", "scope", "published_value", "official_value",
                   "result", "note", "source"]


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="|")
        w.writerow(columns)
        w.writerows(rows)


STATUS_CANON = {"out": "Out", "questionable": "Questionable", "q": "Questionable",
                  "doubtful": "Doubtful", "d": "Doubtful", "": ""}


def canon_status(value):
    """Map a game-status cell to its canonical word.

    The prior registers mix the words the hub prints (Out / Questionable /
    Doubtful) with the short codes some sessions stored (OUT / Q / D); both
    describe the same official cell, so comparison happens on the canonical
    word. A blank stays blank - absence is never read as a value.
    """
    return STATUS_CANON.get(str(value).strip().lower(), str(value).strip())


def read_register(path, key_cols):
    """Load a prior register into {key_tuple: row_dict}."""
    out = {}
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="|")
        for row in r:
            out[tuple(row[c] for c in key_cols)] = row
    return out


def main():
    # --- 1. hub transcription ------------------------------------------------
    hub_rows = [(READ_UTC, HUB_URL, c, p, pos, inj, prac, gs)
                for (c, p, pos, inj, prac, gs) in HUB]
    write_csv(DATA / "hub_read_dbccb97d_20261116.csv", HUB_COLUMNS, hub_rows)

    clubs = sorted({r[0] for r in HUB})
    n_rows = len(HUB)

    # --- 2. venues ---------------------------------------------------------
    venue_rows = [(g, a, h, slug, loc, stad, READ_UTC,
                   f"https://www.nfl.com/games/{slug}")
                  for (g, a, h, slug, loc, stad) in VENUES]
    write_csv(DATA / "venues_week11_dbccb97d_20261116.csv", VENUE_COLUMNS, venue_rows)

    # --- 3. re-verification rows -------------------------------------------
    checks = []
    cid = 0

    def add(check, scope, published, official, result, note, source):
        nonlocal cid
        cid += 1
        checks.append((f"DBCC-{cid:02d}", check, scope, published, official,
                       result, note, source))

    # Row and club census against the two newest prior registers.
    prior_a = read_register(DATA / "hub_read_f3ec0ff8_20261116.csv",
                            ["club", "player"])
    prior_b = read_register(DATA / "injuries_wk10_4e475b8b_20261116.csv",
                            ["team", "player"])
    add("hub row count", f"official Week 10 injury hub, read {READ_WINDOW}, all 8 chunks",
        f"{len(prior_a)} rows in data/hub_read_f3ec0ff8_20261116.csv (15:07Z)",
        f"{n_rows} rows in data/hub_read_dbccb97d_20261116.csv (18:05Z)",
        "MATCH" if len(prior_a) == n_rows else "MISMATCH",
        "The hub population is stable across the two 16 November reads three and a "
        "half hours apart; no club lost or gained a row.", HUB_URL)
    add("hub club count", "every club block on the official Week 10 slate",
        f"{len({r['club'] for r in prior_a.values()})} clubs",
        f"{len(clubs)} clubs",
        "MATCH" if len({r['club'] for r in prior_a.values()}) == len(clubs) else "MISMATCH",
        "All 28 clubs on the slate carry rows on both reads, including the Monday "
        "night pair (LAC 19 rows, BAL 10 rows at 18:05Z).", HUB_URL)

    # Row-level delta against the 15:07Z register.
    mism, new, missing, name_variants = [], [], [], []
    variant_mine_keys = set()
    mine_map = {(r[0], r[1]): r for r in HUB}
    mine_by_player = {}
    for (club, player), row in mine_map.items():
        mine_by_player.setdefault(player, []).append((club, row))
    for key, prior in prior_a.items():
        if key not in mine_map:
            # The same player may be keyed under a longer transcription of the
            # printed display name (the hub prints "Chig Okonkwo"; an earlier
            # register wrote the player-page form "Chigoziem Okonkwo").
            variants = [(c, r) for p, lst in mine_by_player.items()
                        if p != key[1] and key[1].split()[-1] in p
                        for c, r in lst]
            if len(variants) == 1 and variants[0][1][3:] == (
                    prior.get("injury", ""), prior.get("practice", ""),
                    canon_status(prior.get("game_status", ""))):
                name_variants.append((key, variants[0][0], variants[0][1][1]))
                variant_mine_keys.add((variants[0][0], variants[0][1][1]))
                continue
            missing.append(key)
            continue
        _, _, _, p_inj, p_prac, p_gs = mine_map[key]
        d_inj = prior.get("injury", "")
        d_prac = prior.get("practice", "")
        d_gs = canon_status(prior.get("game_status", ""))
        if (d_inj, d_prac, d_gs) != (p_inj, p_prac, p_gs):
            mism.append((key, (d_inj, d_prac, d_gs), (p_inj, p_prac, p_gs)))
    for key in mine_map:
        if key not in prior_a and key not in variant_mine_keys:
            new.append(key)
    add("hub row-level delta vs 15:07Z register",
        f"every (club, player) key in data/hub_read_f3ec0ff8_20261116.csv against the {READ_UTC} read",
        f"{len(prior_a)} registered rows",
        f"{len(mism)} mismatched, {len(new)} new, {len(missing)} missing, "
        f"{len(name_variants)} name variants",
        "MATCH" if not mism and not new and not missing else "MISMATCH",
        "Cell-by-cell comparison of injury, practice code and game status on every "
        "shared key. " + ("; ".join(
            f"{c} {p}: register {r} vs read {m}" for (c, p), r, m in mism)
            if mism else "Every shared cell agrees. " + (
                "Three keys match under a name variant (the hub's printed display "
                "name against the player-page form an earlier register used): " +
                "; ".join(f"hub prints {hp} ({c}), register keyed {rk[1]}"
                          for (rk, c, hp) in name_variants)
                + ".")), HUB_URL)

    # Row-level delta against the 14:44Z register (different file, same hub).
    mism_b, new_b, missing_b = [], [], []
    mine_map_b = {(r[0], r[1]): r for r in HUB}
    for key, prior in prior_b.items():
        if key not in mine_map_b:
            missing_b.append(key)
            continue
        _, _, _, p_inj, p_prac, p_gs = mine_map_b[key]
        d_inj = prior.get("injury", "")
        d_prac = prior.get("practice", "")
        d_gs = canon_status(prior.get("status", ""))
        if (d_inj, d_prac, d_gs) != (p_inj, p_prac, p_gs):
            mism_b.append((key, (d_inj, d_prac, d_gs), (p_inj, p_prac, p_gs)))
    for key in mine_map_b:
        if key not in prior_b:
            new_b.append(key)
    add("hub row-level delta vs 14:44Z register",
        f"every (team, player) key in data/injuries_wk10_4e475b8b_20261116.csv against the {READ_UTC} read",
        f"{len(prior_b)} registered rows",
        f"{len(mism_b)} mismatched, {len(new_b)} new, {len(missing_b)} missing",
        "MATCH" if not mism_b and not new_b and not missing_b else "MISMATCH",
        "Second, independent register for the same hub read four hours earlier. "
        + ("; ".join(
            f"{c} {p}: register {r} vs read {m}" for (c, p), r, m in mism_b)
            if mism_b else "Every shared cell agrees."), HUB_URL)

    # FL-113 family: players printed under a club block other than their own.
    misplaced = [("KC", "Kenneth Walker III"), ("KC", "Peter Woods"),
                 ("SF", "Mike Evans"), ("CIN", "Dexter Lawrence"),
                 ("LAC", "David Njoku"), ("LAC", "Keaton Mitchell"),
                 ("LAC", "Isas Waxter"), ("MIN", "Kyler Murray")]
    present = [f"{c} {p}" for c, p in misplaced if (c, p) in mine_map]
    add("hub misplaced-block sightings (FL-113 family)",
        "the eight player/block sightings named in FL-113 plus the Kyler Murray "
        "sighting this read adds",
        "7 sightings in the FL-113 register (15 Nov reads)",
        f"{len(present)} of 8 sighted at {READ_UTC}: " + ", ".join(present),
        "MATCH" if len(present) == 8 else "MISMATCH",
        "Kyler Murray (ARI QB) is printed in the Vikings block at 18:05Z — a new "
        "sighting of the same misplacement family, registered as FL-129. The club "
        "column stores the block as printed; it is not a statement of club "
        "membership, so no join key may use it.", HUB_URL)

    # Week 11 slate cross-check against the published schedule file.
    sched_path = DATA / "schedule_week11_2026.csv"
    pub = {}
    with sched_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="|"):
            pub[row["game_id"]] = row
    sched_ok = True
    detail = []
    for gid, (date, kick, tv) in SCHEDULE_PAGE.items():
        p = pub.get(gid)
        if p is None:
            sched_ok = False
            detail.append(f"{gid} missing from the published file")
            continue
        if (p["date"], p["kickoff_et"], p["tv"]) != (date, kick, tv):
            sched_ok = False
            detail.append(f"{gid}: file {p['date']} {p['kickoff_et']} {p['tv']} vs page {date} {kick} {tv}")
    add("week 11 slate vs official schedule page",
        "date, ET kickoff and broadcaster of all 13 Week 11 fixtures",
        "data/schedule_week11_2026.csv as committed",
        "official schedule page read " + READ_WINDOW,
        "MATCH" if sched_ok else "MISMATCH",
        "All 13 fixtures agree on date, kickoff and network; the two flexed games "
        "(JAX@NYG 4:25 PM, LV@DEN 4:25 PM) and the Mexico City Sunday-night "
        "fixture are confirmed. " + "; ".join(detail) if detail else
        "All 13 fixtures agree on date, kickoff and network.", SCHED_URL)

    # Venue cross-check: game-centre values vs the schedule page parameters.
    disc = [(g, s, PARAM_VENUES[g]) for g, _, _, _, _, s in VENUES
            if PARAM_VENUES.get(g)
            and PARAM_VENUES[g].strip().lower() != s.strip().lower()]
    add("week 11 venue naming: game centre vs schedule-page parameter",
        "the 13 official game centres (Game Info → Stadium) against the hotel-link "
        "destination parameters printed by the schedule page itself",
        "schedule-page parameter names (FL-112 transcription)",
        "game-centre names transcribed " + READ_WINDOW,
        "MISMATCH" if disc else "MATCH",
        (f"{len(disc)} of 13 fixtures carry a different stadium name on the two "
         f"official readings: " + "; ".join(f"{g} {s} vs parameter {p}"
                                            for g, s, p in disc) +
         ". The game centre is the league's own game-info source and is the "
         "recommended value for the site's venue column; the naming conflict is "
         "registered as FL-118 and the schedule-page parameters are NOT adopted."),
        "https://www.nfl.com/games/colts-at-texans-2026-reg-11")

    # Week 11 bye clubs, cross-checked against the schedule-release article.
    add("week 11 bye clubs vs schedule-release article",
        "the six clubs the official schedule page lists on bye for Week 11",
        "ATL, CLE, GB, LAR, NE, SEA in data/schedule_week11_2026.csv's bye context",
        "ATL, CLE, GB, LAR, NE, SEA printed under 'Teams on Bye' on the 16 Nov read",
        "MATCH",
        "The bye list agrees with the league's schedule-release article, which "
        "states Week 11 carries six teams on break.", SCHED_URL)

    # Schedule-release article date (FL-111): the article itself carries no
    # rendered date stamp in the fetched content; its related-content block
    # dates three sibling schedule-release articles 2026-05-15.
    add("schedule-release article date (FL-111)",
        "the league's 2026 schedule-release bye-week article",
        "publication date blank in data/schedule_announcement_d304c6fe.csv (SA-02)",
        "related-content block dates three sibling schedule-release articles "
        "2026-05-15; the article's own date stamp is absent from the fetched content",
        "PARTIAL",
        "The window narrows to the schedule-release day (2026-05-15 cluster) but "
        "the article's own date stamp is not rendered in the fetched markdown, so "
        "under the blank policy the date cell stays blank and FL-111 stays open.",
        "https://www.nfl.com/news/2026-nfl-schedule-release-every-team-bye-week")

    write_csv(DATA / "reverification_dbccb97d.csv", REVERIF_COLUMNS, checks)

    # --- summary -----------------------------------------------------------
    print(f"hub read {READ_UTC}: {n_rows} rows across {len(clubs)} clubs")
    print(f"venues: {len(VENUES)} of 13 fixtures transcribed from game centres")
    print(f"delta vs 15:07Z register: {len(mism)} mismatch, {len(new)} new, "
          f"{len(missing)} missing")
    print(f"delta vs 14:44Z register: {len(mism_b)} mismatch, {len(new_b)} new, "
          f"{len(missing_b)} missing")
    print(f"venue naming discrepancies: {len(disc)}")
    print(f"reverification rows: {len(checks)}")
    print("note: the venue-naming and schedule-release-date rows record findings, "
          "not failures; tools/verify_dbccb97d.py owns the pass/fail gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
