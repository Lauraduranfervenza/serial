# ============================================================
# Made with chatGPT and Gemini
# ============================================================
import os
import re
import pandas as pd
import pdfplumber


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FOLDER = "/Users/laura/Desktop/my_projects/serial/radford_killers/pdfs"

PROFILE_FOLDER = os.path.join(INPUT_FOLDER, "profiles")
TIMELINE_FOLDER = os.path.join(INPUT_FOLDER, "timelines")

os.makedirs(PROFILE_FOLDER, exist_ok=True)
os.makedirs(TIMELINE_FOLDER, exist_ok=True)


# ============================================================
# RADFORD SECTIONS
# ============================================================

SECTIONS = {
    "General Information",
    "Childhood Information",
    "Cognitive Ability",
    "Work History",
    "Relationships",
    "Triad",
    "Killer Psychological Information",
    "Killer Criminal History (Prior to the series)",
    "Serial Killing",
    "Behavior During Crimes",
    "After Death Behavior",
    "Disposal of Body",
    "Sentencing",
    "References",
}


# ============================================================
# FIELD NAMES
# ============================================================

FIELD_NAMES = [
    "Sex",
    "Race",
    "Number of victims",
    "Country where killing occurred",
    "States where killing occurred",
    "Cities where killing occurred",
    "Type of killer",
    "Height",

    "Date of birth",
    "Location",
    "Birth order",
    "Number of siblings",
    "XYY?",
    "Raised by Mom & Dad…Dad…then Lookout Mountain School for Boys",
    "Raised by Mom & Dad",
    "Birth category",
    "Parent’s marital status",
    "Did serial killer spend time in an orphanage?",
    "Did serial killer spend time in a foster home?",
    "Was serial killer ever raised by a relative?",
    "Did serial killer ever live with adopted family?",
    "Did serial killer live with a step-parent?",
    "Family event",
    "Age of family event",
    "Problems in school?",
    "Teased while in school?",
    "Physically attractive?",
    "Physical defect?",
    "Speech defect?",
    "Head injury?",
    "Physically abused?",
    "Psychologically abused?",
    "Sexually abused?",
    "Father’s occupation",
    "Age when first had intercourse",
    "Mother’s occupation",
    "Father abused drugs/alcohol",
    "Mother abused drugs/alcohol",

    "Highest grade in school",
    "Highest degree",
    "Grades in school",
    "IQ",
    "Source of IQ information",

    "Served in the military?",
    "Branch",
    "Type of discharge",
    "Saw combat duty",
    "Killed enemy during service?",
    "Applied for job as a cop?",
    "Worked in law enforcement?",
    "Fired from jobs?",
    "Types of jobs worked",
    "Employment status during series",

    "Sexual preference",
    "Marital status",
    "Number of children",
    "Lives with his children",
    "Living with",

    "Animal torture",
    "Fire setting",
    "Bed wetting",

    "Abused drugs?",
    "Abused alcohol?",
    "Been to a psychologist (prior to killing)?",
    "Time in forensic hospital (prior to killing)?",
    "Diagnosis",

    "Committed previous crimes?",
    "Spent time in jail?",
    "Spent time in prison?",
    "Killed prior to series? Age?",

    "Number of victims (suspected of)",
    "Number of victims (confessed to)",
    "Number of victims (convicted of)",
    "Victim type",
    "Killer age at start of series",
    "Killer age at end of series",
    "Date of first kill in series",
    "Date of final kill in series",
    "Gender of victims",
    "Race of victims",
    "Age of victims",
    "Type of victim",
    "Method of killing",
    "Weapon",
    "Was gun used?",
    "Type",
    "Did killer have a partner?",
    "Name of partner",
    "Sex of partner",
    "Relationship of partner",
    "Type of serial killer",
    "How close did killer live?",
    "Location of first contact",
    "Location of killing",
    "Killing occurred in home of victim?",
    "Killing occurred in home of killer?",
    "Victim abducted or killed at contact?",

    "Rape?",
    "Tortured victims?",
    "Stalked victims?",
    "Overkill?",
    "Quick & efficient?",
    "Used blindfold?",
    "Bound the victims?",

    "Sex with the body?",
    "Mutilated body?",
    "Ate part of the body?",
    "Drank victim’s blood?",
    "Posed the body?",
    "Took totem – body part",
    "Took totem – personal item",
    "Robbed victim or location",

    "Left at scene, no attempt to hide",
    "Left at scene, hidden",
    "Left at scene, buried",
    "Moved, no attempt to hide",
    "Moved, hidden",
    "Moved, buried",
    "Cut-op and disposed of",
    "Burned body",
    "Dumped body in lake, river, etc.",
    "Moved, took home",

    "Date killer arrested",
    "Date convicted",
    "Sentence",
    "Killer executed?",
    "Was sentenced to death",
    "Did killer plead NGRI?",
    "Was the NGRI plea successful?",
    "Did serial killer confess?",
    "Name and state of prison",
    "Killer committed suicide?",
    "Killer killed in prison?",
    "Date of death",
    "Cause of death",
]

# Longest first so that similar field names don't interfere.
FIELD_NAMES = sorted(FIELD_NAMES, key=len, reverse=True)


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_spaces(text):
    """Collapse repeated whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def extract_pdf_lines(pdf_path):
    """Extract all non-empty text lines from a PDF."""

    lines = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            for line in text.splitlines():

                line = normalize_spaces(line)

                if line:
                    lines.append(line)

    return lines


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_killer_name(lines):
    """
    Extract the killer name and nickname from the first lines.

    Example:

        Dale Wayne Eaton
        “The LIL Miss Killer”

    becomes:

        Dale Wayne Eaton “The LIL Miss Killer”
    """

    if not lines:
        return ""

    # The Radford PDFs normally have:
    #
    # line 1 = name
    # line 2 = nickname
    #
    # We take the first two lines.

    name = lines[0].strip()

    if len(lines) > 1:
        nickname = lines[1].strip()

        # Don't accidentally include the next document heading.
        if nickname and not nickname.lower().startswith(
            ("information", "researched", "date")
        ):
            name = f"{name} {nickname}"

    return normalize_spaces(name)


# ============================================================
# TIMELINE
# ============================================================

def looks_like_date(text):

    text = text.strip()

    patterns = [
        r"^\d{2}/\d{2}/\d{4}$",
        r"^\d{1,2}/\d{1,2}/\d{4}$",
        r"^\d{4}$",
        r"^\d{4}-\d{4}$",
        r"^\d{2}/\d{4}$",
        r"^\d{2}/\d{6}$",
        r"^[A-Za-z]+ \d{4}$",
        r"^[A-Za-z]+ \d{1,2}, \d{4}$",
    ]

    return any(re.match(pattern, text) for pattern in patterns)


def looks_like_age(text):

    text = text.strip()

    return bool(
        re.match(r"^\d{1,3}$", text)
        or re.match(r"^\d{1,3}-\d{1,3}$", text)
    )


def split_timeline_line(line):

    match = re.match(
        r"^(\S+(?:\s+\d{4})?)\s+"
        r"(\d{1,3}(?:-\d{1,3})?)"
        r"(?:\s+(.*))?$",
        line
    )

    if not match:
        return None

    date = match.group(1).strip()
    age = match.group(2).strip()
    event = match.group(3) or ""

    if not looks_like_date(date):
        return None

    if not looks_like_age(age):
        return None

    return date, age, normalize_spaces(event)


def parse_timeline(lines):

    timeline = []

    in_timeline = False
    current_event = None

    for line in lines:

        if line == "Date Age Life Event":
            in_timeline = True
            continue

        if line == "General Information":
            break

        if not in_timeline:
            continue

        parsed = split_timeline_line(line)

        if parsed:

            date, age, event = parsed

            if current_event is not None:
                timeline.append(current_event)

            current_event = {
                "date": date,
                "age": age,
                "life_event": event,
            }

        else:

            # Wrapped line belonging to previous event
            if current_event is not None:
                current_event["life_event"] = normalize_spaces(
                    current_event["life_event"] + " " + line
                )

    if current_event is not None:
        timeline.append(current_event)

    return timeline


# ============================================================
# PROFILE
# ============================================================

def find_section(line):

    if line in SECTIONS:
        return line

    return None


def match_field(line):

    for field in FIELD_NAMES:

        if line == field:
            return field, ""

        if line.startswith(field + " "):

            value = line[len(field):].strip()

            return field, value

    return None


def parse_profile(lines, killer_name):

    profile = []

    current_section = None
    current_field = None
    current_value = None

    in_profile = False

    def save_current():

        nonlocal current_field
        nonlocal current_value

        if current_section and current_field:

            profile.append({
                "section": current_section,
                "field": current_field,
                "value": normalize_spaces(
                    current_value or ""
                ),
            })

        current_field = None
        current_value = None

    for line in lines:

        # ----------------------------------------------------
        # Start profile
        # ----------------------------------------------------

        if line == "General Information":

            save_current()

            in_profile = True
            current_section = "General Information"

            # Add name as first profile row
            profile.append({
                "section": "General Information",
                "field": "name",
                "value": killer_name,
            })

            continue

        if not in_profile:
            continue

        # ----------------------------------------------------
        # New section
        # ----------------------------------------------------

        section = find_section(line)

        if section:

            save_current()

            current_section = section

            continue

        # ----------------------------------------------------
        # New field
        # ----------------------------------------------------

        matched = match_field(line)

        if matched:

            save_current()

            current_field, current_value = matched

            continue

        # ----------------------------------------------------
        # Wrapped continuation of current field
        # ----------------------------------------------------

        if current_field:

            current_value = normalize_spaces(
                (current_value or "") + " " + line
            )

    save_current()

    return profile


# ============================================================
# PROCESS ONE PDF
# ============================================================

def process_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    pdf_name = os.path.splitext(filename)[0]

    print(f"\nProcessing: {filename}")

    try:

        lines = extract_pdf_lines(pdf_path)

        if not lines:
            print("  WARNING: No text extracted")
            return False

        # ----------------------------------------------------
        # Extract name
        # ----------------------------------------------------

        killer_name = extract_killer_name(lines)

        print(f"  Name: {killer_name}")

        # ----------------------------------------------------
        # Timeline
        # ----------------------------------------------------

        timeline = parse_timeline(lines)

        timeline_df = pd.DataFrame(
            timeline,
            columns=[
                "date",
                "age",
                "life_event",
            ]
        )

        # ----------------------------------------------------
        # Profile
        # ----------------------------------------------------

        profile = parse_profile(
            lines,
            killer_name
        )

        profile_df = pd.DataFrame(
            profile,
            columns=[
                "section",
                "field",
                "value",
            ]
        )

        # ----------------------------------------------------
        # Output filename: First_Name_Last_Name
        # Source filename: Last Name, First Name.pdf
        # ----------------------------------------------------

        # Remove .pdf
        name_without_extension = os.path.splitext(filename)[0]

        # Split on the first comma
        if "," in name_without_extension:
            last_name, first_name = name_without_extension.split(",", 1)

            last_name = last_name.strip()
            first_name = first_name.strip()

            output_name = f"{first_name}_{last_name}"

        else:
            # Fallback if a PDF doesn't follow "Last Name, First Name"
            output_name = name_without_extension.replace(" ", "_")

        # Clean characters that aren't suitable for filenames
        output_name = re.sub(r'[<>:"/\\|?*]', "", output_name)

        timeline_path = os.path.join(
            TIMELINE_FOLDER,
            f"{output_name}_timeline.csv"
        )

        profile_path = os.path.join(
            PROFILE_FOLDER,
            f"{output_name}_profile.csv"
        )

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        timeline_df.to_csv(
            timeline_path,
            index=False,
            encoding="utf-8-sig"
        )

        profile_df.to_csv(
            profile_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"  Timeline: {len(timeline_df)} rows")
        print(f"  Profile:  {len(profile_df)} rows")
        print("  SUCCESS")

        return True

    except Exception as e:

        print(f"  ERROR: {e}")

        return False


# ============================================================
# PROCESS ENTIRE FOLDER
# ============================================================

def process_folder():

    pdf_files = [
        f
        for f in os.listdir(INPUT_FOLDER)
        if f.lower().endswith(".pdf")
    ]

    pdf_files.sort()

    print("=" * 60)
    print("RADFORD PDF BATCH PARSER")
    print("=" * 60)

    print(f"Input folder: {INPUT_FOLDER}")
    print(f"PDFs found:   {len(pdf_files)}")

    successful = 0
    failed = 0

    for filename in pdf_files:

        pdf_path = os.path.join(
            INPUT_FOLDER,
            filename
        )

        success = process_pdf(pdf_path)

        if success:
            successful += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print("FINISHED")
    print("=" * 60)

    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Profiles:   {PROFILE_FOLDER}")
    print(f"Timelines:  {TIMELINE_FOLDER}")


# ============================================================
# RUN
# ============================================================

process_folder()