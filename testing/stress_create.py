import random
from datetime import datetime, timedelta
from utils import connect, batch
from tools import create, update, delete, read, search
from pprint import pprint

# Setup environment
conn, cursor, db_meta = connect.get_env()

# Data pools
first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward"]
middle_names = ["James", "Marie", "Lee", "Grace", "Thomas"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
streets = ["123 Main St", "456 Oak Ave", "789 Pine Ln", "321 Maple Dr"]
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
counties = ["Kings", "Cook", "Harris", "Maricopa", "Los Angeles"]
states = ["NY", "CA", "IL", "TX", "AZ"]
zips = ["10001", "90001", "60601", "77001", "85001"]
countries = ["USA"]
email_domains = ["gmail.com", "yahoo.com"]
email_types = ["personal", "work"]
phone_types = ["personal", "work"]
tags = ["legal", "vip", "new", "internal", "follow-up"]
genders = ["male", "female"]
prefixes = ["Mr.", "Ms.", "Dr.", None, None, None]
suffixes = ["Jr.", "Sr.", "III", None, None, None]
entity_types = ["Lead"]
dob_years = [str(y) for y in range(1970, 2000)]

# Notes: Album verses
album_verses = {
    "Believe": [
        "No matter how hard I try, you keep pushing me aside...",
        "After love, after love, after love...",
        "I don’t need you anymore, no I don’t need you anymore..."
    ],
    "Heart of Stone": [
        "Beneath the makeup and behind the smile...",
        "I found someone, who found someone...",
        "Heart of stone, will never break..."
    ],
    "Closer to the Truth": [
        "I walk alone, through a world of lies...",
        "Take it like a man, strong hands, soft heart...",
        "I hope you find it, what you're looking for..."
    ],
    "Living Proof": [
        "When the money's gone, will you be my friend?",
        "A different kind of love, electric in the dark...",
        "Love is the groove, moves you smooth..."
    ],
    "Take Me Home": [
        "Take me home, I want to feel your heartbeat...",
        "Wasn't it good? Wasn't it fine?",
        "Let's turn back time tonight..."
    ],
    "Love Hurts": [
        "Love hurts, love scars, love wounds...",
        "I’ll never stop loving you...",
        "When love calls, will you answer?"
    ],
    "It's a Man's World": [
        "It’s a man’s world, but it wouldn’t be nothing...",
        "Angels running, bringing back your love to me...",
        "The gunman's in the house tonight..."
    ],
    "Dancing Queen": [
        "You can dance, you can jive, having the time of your life...",
        "Friday night and the lights are low...",
        "Dancing queen, feel the beat from the tambourine..."
    ],
    "Black Rose": [
        "Never should've started this fire...",
        "You're always on my mind...",
        "The black rose blooms at midnight..."
    ],
    "Cher": [
        "Bang bang, he shot me down...",
        "I got you babe, I got you babe...",
        "Half-breed, that's all I ever heard..."
    ]
}
subjects = list(album_verses.keys())
bodies = [line for verses in album_verses.values() for line in verses]

# Date generators
def iso_now():
    return datetime.now().strftime("%Y%m%dT%H%M")

def random_iso(start_year=2021, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    rand_date = start + timedelta(days=random.randint(0, delta.days))
    rand_time = timedelta(minutes=random.randint(0, 1439))
    return (rand_date + rand_time).strftime("%Y%m%dT%H%M")

# Build people
group_data = {}
for i in range(3000):
    group_id = f"group_{i+1}"
    person = {
        "Contacts": [],
        "Addresses": [],
        "Email_Addresses": [],
        "Phone_Numbers": [],
        "Notes": [],
        "Tracking": []
    }

    # CONTACTS
    fn = random.choice(first_names)
    mn = random.choice(middle_names)
    ln = random.choice(last_names)
    full = f"{fn} {mn} {ln}"
    person["Contacts"].append([
        "person",                         # entity
        random.choice(prefixes),         # prefix
        fn,                              # first_name
        mn,                              # middle_name
        ln,                              # last_name
        random.choice(suffixes),         # suffix
        full,                            # full_name
        random.choice(genders),          # gender
        random.choice(dob_years),        # date_of_birth
        random.choice(cities),           # location_of_birth
        None                                # ssn
    ])

    # ADDRESSES
    num_addresses = random.randint(1, 2)
    prim_index = random.randint(0, num_addresses - 1)
    for j in range(num_addresses):
        person["Addresses"].append([
            random.choice(streets),     # street
            random.choice(cities),      # city
            random.choice(counties),    # county
            state := random.choice(states),  # state
            random.choice(zips),        # zip
            random.choice(countries),   # country
            "home",                     # address_type
            j == prim_index             # is_primary
        ])

    # EMAILS
    num_emails = random.randint(1, 2)
    prim_index = random.randint(0, num_emails - 1)
    for j in range(num_emails):
        email = f"{fn.lower()}.{ln.lower()}@{random.choice(email_domains)}"
        person["Email_Addresses"].append([
            email,
            random.choice(email_types),
            j == prim_index
        ])

    # PHONES
    num_phones = random.randint(1, 3)
    prim_index = random.randint(0, num_phones - 1)
    area_code = {
        "NY": "212", "CA": "310", "IL": "312", "TX": "713", "AZ": "602"
    }.get(state, "555")
    for j in range(num_phones):
        number = f"{area_code}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        person["Phone_Numbers"].append([
            number,
            random.choice(phone_types),
            j == prim_index
        ])

    # NOTES
    for _ in range(random.randint(1, 3)):
        person["Notes"].append([
            random.choice(subjects),
            random.choice(bodies),
            iso_now()
        ])

    # TRACKING
    person["Tracking"].append([
        random_iso(),
        random.choice(states),
        "Lead",
        random.choice(tags)
    ])

    group_data[group_id] = {
        "table": [
            "Contacts", "Addresses", "Email_Addresses",
            "Phone_Numbers", "Notes", "Tracking"
        ],
        "field": [
            ["entity", "prefix", "first_name", "middle_name", "last_name", "suffix", "full_name",
             "gender", "date_of_birth", "location_of_birth", "social_security_number"],
            ["street", "city", "county", "state", "zip_code", "country", "address_type", "is_primary"],
            ["email_address", "email_type", "is_primary"],
            ["phone_number", "phone_type", "is_primary"],
            ["subject", "body", "created"],
            ["created", "state_filed", "entity_type", "tags"]
        ],
        "value": [
            person["Contacts"],
            person["Addresses"],
            person["Email_Addresses"],
            person["Phone_Numbers"],
            person["Notes"],
            person["Tracking"]
        ]
    }

# Build and send package
package = {
    "batch_1": {
        "process_1": {
            "create": group_data
        }
    }
}

tool_handlers = {
    "create": create.handle,
    "update": update.handle,
    "delete": delete.handle,
    "read": read.handle,
    "search": search.handle
}

print("🚀 Running stress test for CREATE with 3000 people...")
result = batch.handle_batch(package, conn, cursor, db_meta, tool_handlers)

print("\n📦 Batch Result:")
pprint(result)
