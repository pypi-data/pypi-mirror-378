#!/usr/bin/env python3
"""
Scorpius ASCII Art Header
Custom ASCII art for the world's strongest smart contract scanner
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Clean SCORPIUS ASCII Art
SCORPIUS_ASCII = r"""
 _______  _______  _______  _______  _______ _________          _______ 
(  ____ \(  ____ \(  ___  )(  ____ )(  ____ )\__   __/|\     /|(  ____ \
| (    \/| (    \/| (   ) || (    )|| (    )|   ) (   | )   ( || (    \/
| (_____ | |      | |   | || (____)|| (____)|   | |   | |   | || (_____ 
(_____  )| |      | |   | ||     __)|  _____)   | |   | |   | |(_____  )
      ) || |      | |   | || (\ (   | (         | |   | |   | |      ) |
/\____) || (____/\| (___) || ) \ \__| )      ___) (___| (___) |/\____) |
\_______)(_______/(_______)|/   \__/|/       \_______/(_______)\_______)
"""

SCORPIUS_SIMPLE = r"""
 ╔═══════════════════════════════════════════════════════════════╗
 ║  ███████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██╗   ██╗███████╗ ║
 ║  ██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗██║██║   ██║██╔════╝ ║
 ║  ███████╗██║     ██║   ██║██████╔╝██████╔╝██║██║   ██║███████╗ ║
 ║  ╚════██║██║     ██║   ██║██╔══██╗██╔═══╝ ██║██║   ██║╚════██║ ║
 ║  ███████║╚██████╗╚██████╔╝██║  ██║██║     ██║╚██████╔╝███████║ ║
 ║  ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝ ║
 ║                                                                 ║
 ║           🦂 World's Strongest Smart Contract Scanner 🦂        ║
 ╚═══════════════════════════════════════════════════════════════╝
"""

SCORPIUS_COMPACT = r"""
 ███████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██╗   ██╗███████╗
 ██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗██║██║   ██║██╔════╝
 ███████╗██║     ██║   ██║██████╔╝██████╔╝██║██║   ██║███████╗
 ╚════██║██║     ██║   ██║██╔══██╗██╔═══╝ ██║██║   ██║╚════██║
 ███████║╚██████╗╚██████╔╝██║  ██║██║     ██║╚██████╔╝███████║
 ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
 
 🦂 AI-Powered Smart Contract Security Scanner 🦂
"""

SCORPIUS_MINIMAL = r"""
 ███████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██╗   ██╗███████╗
 ███████╗██║     ██║   ██║██████╔╝██████╔╝██║██║   ██║███████╗
 ╚════██║██║     ██║   ██║██╔══██╗██╔═══╝ ██║██║   ██║╚════██║
 ███████║╚██████╗╚██████╔╝██║  ██║██║     ██║╚██████╔╝███████║
 ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
"""

# Alternative Scorpion-themed ASCII
SCORPION_ASCII = r"""
                    ,-.       _,---._ __  / \
                   /  )    .-'       `./ /   \
                  (  (   ,'            `/    /|
                   \  `-"             \'\   / |
                    `.              ,  \ \ /  |
                     /`.          ,'-`----Y   |
                    (            ;        |   '
                    |  ,-.    ,-'         |  /
                    |  | (   |  ███████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██╗   ██╗███████╗
                    )  |  \  `._███████╗██║     ██║   ██║██████╔╝██████╔╝██║██║   ██║███████╗
                    `--'   `--' ╚════██║██║     ██║   ██║██╔══██╗██╔═══╝ ██║██║   ██║╚════██║
                                ███████║╚██████╗╚██████╔╝██║  ██║██║     ██║╚██████╔╝███████║
                                ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
                                
                                🦂 WORLD'S STRONGEST SMART CONTRACT SCANNER 🦂
"""

def print_header(style="full", console=None):
    """Print Scorpius header with specified style"""
    
    if console is None:
        console = Console()
    
    if style == "full":
        ascii_art = SCORPIUS_ASCII
        color = "bright_cyan"
    elif style == "simple":
        ascii_art = SCORPIUS_SIMPLE
        color = "cyan"
    elif style == "compact":
        ascii_art = SCORPIUS_COMPACT
        color = "blue"
    elif style == "minimal":
        ascii_art = SCORPIUS_MINIMAL
        color = "white"
    elif style == "scorpion":
        ascii_art = SCORPION_ASCII
        color = "yellow"
    else:
        ascii_art = SCORPIUS_COMPACT
        color = "cyan"
    
    # Create styled text
    header_text = Text(ascii_art, style=color)
    
    # Print with panel
    console.print(Panel(
        header_text,
        border_style="bright_blue",
        padding=(1, 2)
    ))

def print_version_info(version="1.0.0", console=None):
    """Print version information"""
    
    if console is None:
        console = Console()
    
    version_text = f"Scorpius Scanner v{version}"
    
    console.print(version_text, style="bold green")

def print_quick_start(console=None):
    """Print quick start guide"""
    
    if console is None:
        console = Console()
    
    quick_start = """
🚀 Quick Start:

   scorpius scan contract.sol                    # Scan single contract
   scorpius scan contracts/ --report pdf         # Scan directory, PDF report
   scorpius scan contracts/ --format json        # JSON output
   scorpius train --data audits.csv              # Train on new audit data
   scorpius patterns --export scanner.json       # Export learned patterns
   scorpius api --start                          # Start REST API server
   scorpius --help                               # Show all commands

📚 Documentation: https://docs.scorpius.io
🐛 Issues: https://github.com/scorpius-security/scorpius-scanner/issues
💬 Community: https://discord.gg/scorpius-security
"""
    
    console.print(Panel(
        quick_start.strip(),
        title="[bold blue]Quick Start Guide[/bold blue]",
        border_style="blue"
    ))

if __name__ == "__main__":
    # Demo the ASCII art
    console = Console()
    
    print_header("full", console)
    print_quick_start(console)