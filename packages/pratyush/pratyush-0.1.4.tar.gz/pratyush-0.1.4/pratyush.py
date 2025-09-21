__version__ = "0.1.4"

from rich.console import Console
from rich.text import Text
from InquirerPy import inquirer
import webbrowser

projects = [
    {"name": "ᯓ➤ ", "link": "https://its-pratyush.web.app"},
    {"name": "Collab AI Project Platform", "link": "https://github.com/pratyushranjn/collab-ai-project-platform"},
    {"name": "NoBrokerBuddy", "link": "https://github.com/pratyushranjn/NoBrokerBuddy"},
    {"name": "Wavetune Music Player", "link": "https://github.com/pratyushranjn/Wavetune-Music-Player"},
    {"name": "Newsphere FactChecker", "link": "https://github.com/pratyushranjn/Newsphere-FactChecker"}
]

def main():
    console = Console()

    banner = r"""
  ____             _                 
 |  _ \ _ __ __ _| |_ _   _ ___  ___ 
 | |_) | '__/ _` | __| | | / __|/ _ \
 |  __/| | | (_| | |_| |_| \__ \  __/
 |_|   |_|  \__,_|\__|\__,_|___/\___|
"""

    # Build colored text (blue verticals/diagonals, red horizontals, white chars, yellow name)
    text = Text(justify="center")
    for line in banner.splitlines():
        for ch in line:
            if ch in "|/\\":   # verticals & diagonals
                text.append(ch, style="bold bright_blue")
            elif ch in "_-":   # horizontals
                text.append(ch, style="bold bright_red")
            else:              # letters/numbers
                text.append(ch, style="bold white")
        text.append("\n")

    # Print banner
    console.print(text)

    # Display portfolio website separately
    console.print(f"  [bold bright_yellow]{projects[0]['name']}[/bold bright_yellow]: [underline blue]{projects[0]['link']}[/underline blue]\n")

    # Prepare menu for other projects
    choices = [p["name"] for p in projects[1:]] + ["Quit"]

    try:
        selected = inquirer.select(
            message="Select a project to open in your browser:",
            choices=choices,
            cycle=True,
            vi_mode=False
        ).execute()

        if selected == "Quit":
            console.print("\n👋 Exiting...\n")
            return

        for p in projects[1:]:
            if p["name"] == selected:
                console.print(f"\n🔗 Opening [bold bright_yellow]{p['name']}[/bold bright_yellow] in your browser...\n")
                webbrowser.open(p["link"])
                break

    except KeyboardInterrupt:
        console.print("\n👋 Exiting...\n")

if __name__ == "__main__":
    main()

