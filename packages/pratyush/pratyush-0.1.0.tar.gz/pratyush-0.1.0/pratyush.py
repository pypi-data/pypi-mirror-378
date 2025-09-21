from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
import pyperclip

# Project data
projects = [
    {
        "name": "Portfolio Website",
        "github": "https://its-pratyush.web.app/",
        "clone": "-"
    },
    {
        "name": "Collab AI Project Platform",
        "github": "https://github.com/pratyushranjn/collab-ai-project-platform",
        "clone": "git clone https://github.com/pratyushranjn/collab-ai-project-platform"
    },
    {
        "name": "NoBrokerBuddy",
        "github": "https://github.com/pratyushranjn/NoBrokerBuddy",
        "clone": "git clone https://github.com/pratyushranjn/NoBrokerBuddy"
    },
    {
        "name": "Wavetune Music Player",
        "github": "https://github.com/pratyushranjn/Wavetune-Music-Player",
        "clone": "git clone https://github.com/pratyushranjn/Wavetune-Music-Player"
    },
    {
        "name": "Newsphere FactChecker",
        "github": "https://github.com/pratyushranjn/Newsphere-FactChecker",
        "clone": "git clone https://github.com/pratyushranjn/Newsphere-FactChecker"
    }
]

def main():
    console = Console()
    
    console.print("\n🚀 [bold cyan]Pratyush Projects[/bold cyan]\n")
    
    # Display table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project", style="bold yellow")
    table.add_column("GitHub Link", style="cyan")
    table.add_column("Clone Command", style="green")
    
    for p in projects:
        table.add_row(p["name"], p["github"], p["clone"])
    
    console.print(table)
    
    # Interactive selection (skip portfolio website)
    choices = [p["name"] for p in projects if p["clone"] != "-"]
    selected = inquirer.select(
        message="Select a project to copy its git clone command:",
        choices=choices
    ).execute()
    
    # Copy clone command
    for p in projects:
        if p["name"] == selected:
            pyperclip.copy(p["clone"])
            console.print(f"\n✅ Clone command for [bold yellow]{selected}[/bold yellow] copied to clipboard!\n")
            break

if __name__ == "__main__":
    main()
