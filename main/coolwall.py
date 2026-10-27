"""
The Cool Wall (easter egg, /cool-wall/).

A tribute to the format only: no show names, logos or images. These verdicts
are drafts written to get the page started — edit them so they're yours.
Each item needs a name, a zone key from COOL_WALL_ZONES, a kind and a verdict.
"""

COOL_WALL_ZONES = [
    {"key": "seriously-uncool", "label": "Seriously uncool", "temp": "+38°"},
    {"key": "uncool", "label": "Uncool", "temp": "+21°"},
    {"key": "cool", "label": "Cool", "temp": "+4°"},
    {"key": "sub-zero", "label": "Sub-zero", "temp": "−40°"},
]

COOL_WALL = [
    # Sub-zero
    {"name": "Linux", "zone": "sub-zero", "kind": "System",
     "verdict": "Runs the servers, the routers and, eventually, your life."},
    {"name": "Git", "zone": "sub-zero", "kind": "Tool",
     "verdict": "Remembers everything. Judges quietly."},
    {"name": "Python", "zone": "sub-zero", "kind": "Language",
     "verdict": "Reads like pseudocode. Ships like a product."},

    # Cool
    {"name": "Django", "zone": "cool", "kind": "Framework",
     "verdict": "Batteries included, and they are the good kind."},
    {"name": "PostgreSQL", "zone": "cool", "kind": "Database",
     "verdict": "Has never lost an argument about data integrity."},
    {"name": "Dark mode", "zone": "cool", "kind": "Habit",
     "verdict": "Not a preference. A position."},

    # Uncool
    {"name": "Java", "zone": "uncool", "kind": "Language",
     "verdict": "Utterly dependable. So is a filing cabinet."},
    {"name": "CSS centring", "zone": "uncool", "kind": "Ritual",
     "verdict": "Solved years ago. Still somehow a rite of passage."},
    {"name": "Light theme IDE", "zone": "uncool", "kind": "Habit",
     "verdict": "Brave. Wrong, but brave."},

    # Seriously uncool
    {"name": "Merge conflict at 23:59", "zone": "seriously-uncool", "kind": "Event",
     "verdict": "Deadline-adjacent. Never cool. Not once."},
    {"name": "Inline styles", "zone": "seriously-uncool", "kind": "Habit",
     "verdict": "Everyone has done it. Nobody talks about it."},
    {"name": "Works on my machine", "zone": "seriously-uncool", "kind": "Excuse",
     "verdict": "Not a deployment strategy."},
]
