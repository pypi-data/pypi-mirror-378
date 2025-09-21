from rich.console import Console
from rich.table import Table
from rich import box
from InquirerPy import inquirer
import pyperclip

# Project data
projects = [
    {
        "name": "Collab AI Project Platform",
        "github": "https://github.com/pratyushranjn/collab-ai-project-platform",
        "clone": "git clone https://github.com/pratyushranjn/collab-ai-project-platform",
        "color": "bright_blue"
    },
    {
        "name": "NoBrokerBuddy",
        "github": "https://github.com/pratyushranjn/NoBrokerBuddy",
        "clone": "git clone https://github.com/pratyushranjn/NoBrokerBuddy",
        "color": "bright_green"
    },
    {
        "name": "Wavetune Music Player",
        "github": "https://github.com/pratyushranjn/Wavetune-Music-Player",
        "clone": "git clone https://github.com/pratyushranjn/Wavetune-Music-Player",
        "color": "bright_magenta"
    },
    {
        "name": "Newsphere FactChecker",
        "github": "https://github.com/pratyushranjn/Newsphere-FactChecker",
        "clone": "git clone https://github.com/pratyushranjn/Newsphere-FactChecker",
        "color": "bright_cyan"
    }
]

def main():
    console = Console()

    # Display unique portfolio website
    console.print("\n🌐 [bold cyan]Portfolio Website:[/bold cyan] [link=https://its-pratyush.web.app/]https://its-pratyush.web.app/[/link]\n")

    # Display table for other projects with row colors
    table = Table(show_header=True, header_style="bold magenta", box=box.DOUBLE_EDGE)
    table.add_column("Project", style="bold yellow")
    table.add_column("GitHub Link", style="cyan")
    table.add_column("Clone Command", style="green")

    for p in projects:
        table.add_row(p["name"], f"[link={p['github']}]{p['github']}[/link]", p["clone"], style=p["color"])

    console.print(table)

    # Interactive selection
    choices = [p["name"] for p in projects]
    choices.append("q - Quit")  # Option to quit
    selected = inquirer.select(
        message="Select a project to copy its git clone command:",
        choices=choices
    ).execute()

    if selected.startswith("q"):
        console.print("\n👋 Exiting...\n")
        return

    # Copy clone command
    for p in projects:
        if p["name"] == selected:
            pyperclip.copy(p["clone"])
            console.print(f"\n✅ Clone command for [bold yellow]{selected}[/bold yellow] copied to clipboard!\n")
            break

if __name__ == "__main__":
    main()
