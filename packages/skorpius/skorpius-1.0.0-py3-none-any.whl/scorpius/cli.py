#!/usr/bin/env python3
"""
Scorpius CLI Entry Point
Main entry point for the scorpius command
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scorpius_ascii import print_header
from rich.console import Console

def main():
    """Main CLI entry point"""
    console = Console()
    
    # Show header
    print_header("compact", console)
    
    console.print("🦂 Scorpius Scanner v1.0.0", style="bold cyan")
    console.print("World's Strongest Smart Contract Security Scanner", style="dim")
    
    console.print("\n🚀 Available Commands:", style="bold")
    console.print("   scorpius scan <contract>     # Scan smart contract")
    console.print("   scorpius train --data <file> # Train on audit data") 
    console.print("   scorpius stats               # Show statistics")
    console.print("   scorpius --help              # Show help")
    
    console.print("\n📚 Documentation: https://docs.scorpius.io", style="blue")
    console.print("🐛 Issues: https://github.com/scorpius-security/scorpius-scanner/issues", style="blue")

if __name__ == "__main__":
    main()