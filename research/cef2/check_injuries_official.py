#!/usr/bin/env python3
"""Independent re-verification of data/injuries_2026_wk10.csv against the official
nfl.com/injuries/ hub, as fetched on 2026-11-12T22:40Z (page reader, 5 chunks).

Player lists below are transcribed from the official hub tables for each club's
Week 10 practice report (the same filing this register was built from). This check
answers one question only: does every register row exist on the official page?

Run:  python3 research/cef2/check_injuries_official.py
Exit 0 = every row found; 1 = at least one register row is not on the official page.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

# hub[t] = players shown on the official page for club t at fetch time.
# Names kept exactly as the official table renders them (e.g. "Jacob Hummel" vs
# slug jake-hummel; the register maps player -> slug, verified separately).
HUB = {
    "WAS": ["John Bates", "Treylon Burks", "Jayden Daniels", "Matt Gulbin", "Chig Okonkwo", "Lucas Patrick", "Amik Robertson", "Shy Tuttle", "Colson Yankoff"],
    "NYG": ["Abdul Carter", "Jermaine Eluemunor", "Malik Harrison", "Colton Hood", "Theo Johnson", "Charlie Jones", "J.J. McCarthy", "Darnell Mooney", "Malik Nabers", "Cam Skattebo", "Andrew Thomas"],
    "NE": ["Ben Brown", "A.J. Brown", "Kevin Byard", "Carlton Davis III", "Reggie Gilliam", "TreVeyon Henderson", "Hunter Henry", "Cameron Latu", "Drake Maye", "Morgan Moses", "Walter Rouse", "Brenden Schooler", "Rhamondre Stevenson", "Greg Van Roten", "Charles Woods"],
    "DET": ["Brian Branch", "Jared Goff", "Kerby Joseph", "Cade Mays", "D.J. Reed", "Jacob Saylors", "Amon-Ra St. Brown", "Sione Vaki", "DJ Wonnum"],
    "KC": ["Jeffrey Bassa", "Mansoor Delane", "Justin Fields", "Jaden Hicks", "Travis Kelce", "Patrick Mahomes", "Jaylon Moore", "Omarr Norman-Lott", "Rashee Rice", "Peter Woods", "Xavier Worthy"],
    "ATL": ["Zachariah Branch", "Divine Deablo", "Gervon Dexter Sr.", "James Pearce Jr.", "Za'Darius Smith", "Josh Woods"],
    "MIN": ["Blake Cashman", "T.J. Hockenson", "Tyrion Ingram-Dawkins", "Theo Jackson", "Jauan Jennings", "Kyler Murray", "Kyle Van Noy", "Jay Ward", "Carson Wentz"],
    "GB": ["Aaron Banks", "Chris Brooks", "Javon Bullard", "Zaire Franklin", "Travis Glover", "Ty'Ron Hopper", "Josh Jacobs", "Bo Melton", "Skyy Moore", "Micah Parsons", "Sean Rhyan", "Trey Smack", "Lukas Van Ness", "Josh Whyle", "Savion Williams", "Kevin Zeitler"],
    "JAX": ["Jessie Bates", "Ezra Cleveland", "Branson Combs", "Jordan Davis", "BJ Green II", "Robert Hainsey", "Antonio Johnson", "Jakobi Meyers", "Chris Rodriguez Jr.", "Bhayshul Tuten", "Travon Walker"],
    "TEN": ["Cody Barton", "John Franklin-Myers", "Marcus Harris", "Anthony Hill Jr.", "Jaylon Jones", "JC Latham", "Tony Pollard", "Peter Skoronski", "Tyjae Spears", "Carnell Tate", "Tommy Townsend", "Kevin Winston Jr."],
    "BUF": ["Alec Anderson", "Christian Benford", "Spencer Brown", "Dion Dawkins", "Greg Gaines", "Jordan Hancock", "Dalton Kincaid", "Connor McGovern", "Ar'maj Reed-Adams", "T.J. Sanders", "Tyrell Shavers"],
    "NYJ": ["Omar Cooper Jr.", "Joseph Ossai", "VJ Payne", "Harrison Phillips", "Trevin Wallace", "Garrett Wilson", "Nahshon Wright"],
    "MIA": ["Tucker Addington", "Kaytron Allen", "Darrell Baker Jr.", "Chris Bell", "Aaron Brewer", "Malik Herring", "Will Kacmarek", "Michael Taaffe", "Dante Trader Jr.", "Jaylen Wright"],
    "IND": ["Mo Alie-Cox", "CJ Allen", "Jaylon Carlies", "Akeem Davis-Gaither", "A.J. Haulcy", "Arden Key", "Luke Rhodes", "Grover Stewart", "Jonathan Taylor", "Jerry Tillery", "Jalen Travis", "Justin Walley", "Charvarius Ward"],
    "CAR": ["Jonathon Brooks", "Brady Christensen", "Trevor Etienne", "Chuba Hubbard", "Lee Hunter", "Mike Jackson", "Will Lee III", "Xavier Legette", "Damien Lewis", "Bobby Okereke", "Jaelan Phillips", "Torricelli Simpkins III"],
    "NO": ["Kelvin Banks Jr.", "CJ Donaldson", "David Edwards", "Martin Emerson", "Travis Etienne", "Noah Fant", "Alvin Kamara", "Erik McCoy", "Christen Miller", "Asim Richards"],
    "HOU": ["Azeez Al-Shaair", "Reed Blankenship", "Tank Dell", "Blake Fisher", "Marvin Harrison Jr.", "Jacob Hummel", "Brevin Jordan", "Woody Marks", "David Montgomery", "Keylan Rutledge", "Jaylin Smith", "Wyatt Teller", "Tommy Togiai"],
    "CLE": ["Austin Barber", "Denzel Boston", "Michael Burton", "Maliek Collins", "Harold Fannin Jr.", "Ronnie Hickman Jr.", "Tytus Howard", "Elgton Jenkins", "Carson Schwesinger", "Denzel Ward", "Quincy Williams"],
    # Official hub renders the Rams block with club code "LA" (alt text LAR);
    # this register keys the club as LAR (see FL-17). Cardinals = AZ on both.
    "AZ": ["Budda Baker", "Zachary Carter", "Hjalte Froholdt", "Jon Gaines II", "Bam Knight", "Hunter Long", "Roy Lopez", "Max Melton", "Isaac Seumalo", "Dante Stills", "Josh Sweat", "Jayden Williams", "Mack Wilson", "Andrew Wingard"],
    "LAR": ["Davis Allen", "Steve Avila", "Joe Cardona", "Kam Curl", "Terrance Ferguson", "Myles Garrett", "Trent McDuffie", "Puka Nacua", "Colby Parkinson", "Matthew Stafford"],
    "SEA": ["AJ Barner", "Anthony Bradford", "Charles Cross", "Sam Darnold", "Derick Hall", "Drew Lock", "Quenton Nelson", "Uchenna Nwosu", "Patrick O'Connell", "Connor O'Toole", "Brandon Pili", "Jarran Reed", "Rashid Shaheed", "Jaxon Smith-Njigba", "Leonard Williams"],
    "LV": ["Thomas Booker", "Foley Fatukasi", "Ian Thomas", "Trey Zuhn III"],
    "SF": ["Mike Evans", "Renardo Green", "Dre Greenlaw", "Nate Hobbs", "Deommodore Lenoir", "Christian McCaffrey", "Siran Neal", "Demarcus Robinson", "Deebo Samuel Sr.", "Upton Stout", "C.J. West", "Trent Williams"],
    "DAL": ["Jonathan Bullard", "Donovan Ezeiruaku", "Jake Ferguson", "Tyler Goodson", "Malik Hooker", "Marist Liufau", "P.J. Locke", "Von Miller", "Jonathan Mingo", "Devin Moore", "DeMarvion Overshown", "George Pickens", "Joey Porter Jr.", "Luke Schoonmaker", "Brevyn Spann-Ford", "KaVontae Turpin"],
    "PIT": ["Brandin Echols", "DeShon Elliott", "Derrick Harmon", "Cameron Heyward", "Ben Skowronek", "Doneiko Slaughter", "Darnell Washington", "T.J. Watt"],
    "CIN": ["Jonathan Allen", "Kyle Dugger", "Dylan Fairchild", "DJ Turner II"],
    "BAL": [],
    "LAC": [],
}


def load_register():
    with open(os.path.join(REPO, "data", "injuries_2026_wk10.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="|"))


def main():
    reg = load_register()
    if len(reg) != 254:
        print("FAIL: register row count is %d, expected 254" % len(reg))
        return 1
    hubset = {t: set(v) for t, v in HUB.items()}
    missing = [(r["team"], r["player"], r["game"]) for r in reg if r["player"] not in hubset.get(r["team"], set())]
    regset = {}
    for r in reg:
        regset.setdefault(r["team"], set()).add(r["player"])
    extra = {t: sorted(hubset[t] - regset.get(t, set())) for t in HUB if hubset[t] - regset.get(t, set())}
    print("register rows: %d | clubs on official page: %d" % (len(reg), len(HUB)))
    print("register rows NOT on the official page: %d" % len(missing))
    for m in missing:
        print("  MISSING", m)
    print("official-page rows not in the register (hub shows more):")
    for t, v in extra.items():
        print("  EXTRA", t, v)
    n_extra = sum(len(v) for v in extra.values())
    print("total extra rows on hub: %d" % n_extra)
    # SEA/CIN are the two clubs this register documents as "No Injuries Reported"
    # on the hub page (FL-01). The hub at 2026-11-12T22:40Z lists SEA and CIN
    # players - the flag is about the hub-vs-news contradiction, recorded there.
    if missing:
        print("VERDICT: FAIL - %d register rows could not be located on the official page" % len(missing))
        return 1
    print("VERDICT: PASS - every register row exists on the official page; hub additionally shows %d rows not in the register (flagged, not inferred away)" % n_extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
