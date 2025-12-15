
"""
BlueSky CLI Tool
"""
import os
import sys
import argparse
import inquirer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from .api import BlueSkyAPI
from .utils import console

def interactive_menu():
    console.print(Panel.fit("[bold cyan]BlueSky API Interaction Tool[/bold cyan]", border_style="cyan"))
    
    questions = [
        inquirer.List('action',
            message="What would you like to do?",
            choices=[
                ('View user profile', 'profile'),
                ('Get recent posts', 'posts'),
                ('Get post summary', 'summary'),
                ('Perform vibe check', 'vibe'),
                ('View followers', 'followers'),
                ('View following', 'following'),
                ('Exit', 'exit')
            ],
        )
    ]
    answers = inquirer.prompt(questions)
    if answers['action'] == 'exit':
        sys.exit(0)

    bsky = BlueSkyAPI()
    try:
        bsky.authenticate_bsky()
    except Exception as e:
        console.print(f"[bold red]Authentication failed: {e}[/bold red]")
        console.print("[dim]Please set BSKY_IDENTIFIER and BSKY_PASSWORD in environment or config.[/dim]")
        return

    if answers['action'] == 'profile':
        h = inquirer.text(message="Enter BlueSky handle")
        try:
            profile = bsky.get_profile(h)
            console.print(profile)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            
    elif answers['action'] == 'posts':
        h = inquirer.text(message="Enter BlueSky handle")
        try:
            posts = bsky.get_bsky_posts(h)
            console.print(f"Fetched {len(posts.get('feed', []))} posts")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    elif answers['action'] == 'vibe':
         h = inquirer.text(message="Enter BlueSky handle")
         try:
             posts = bsky.get_bsky_posts(h)
             text = bsky.get_post_content(posts)
             vibe = bsky.vibe_check(text)
             console.print(Panel(vibe, title="Vibe Check"))
         except Exception as e:
             console.print(f"[red]Error: {e}[/red]")
             
    # Implement others as needed, keeping it simple for the refactor

def main():
    parser = argparse.ArgumentParser(description="BlueSky CLI")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if args.interactive:
        while True:
            interactive_menu()
    else:
        # Simple one-shot commands could go here
        interactive_menu() # Default to interactive for now as per original design

if __name__ == "__main__":
    main()
