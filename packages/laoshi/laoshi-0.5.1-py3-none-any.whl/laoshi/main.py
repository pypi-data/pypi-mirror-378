"""Main file from laoshi"""

import click
from click_repl import register_repl
from laoshi.converter import Converter
from laoshi.translator import Translator
from laoshi.flashcardgenerator import FlashCardGenerator
from laoshi.deckmanager import DeckManager

SIMPLIFIED = "simplified"
TRADITIONAL = "traditional"
CHINESE_OPTIONS = [TRADITIONAL, SIMPLIFIED, "pinyin"]


@click.group()
def cli_group():
    """cli application to learn chinese."""


@cli_group.command(help="Convert characters")
@click.option(
    "-t",
    "--to",
    default="pinyin",
    type=click.Choice(CHINESE_OPTIONS),
)
@click.argument("word")
def cc(to: str, word: str):
    """Change character function"""
    match to:
        case "traditional":
            click.echo(Converter.to_traditional(word))
        case "simplified":
            click.echo(Converter.to_simplified(word))
        case "pinyin":
            click.echo(Converter.to_pinyin(word))


@cli_group.command(help="Translate a phrase")
@click.option(
    "-t",
    "--to",
    default="en",
)
@click.option("--pinyin", "-p", is_flag=True)
@click.argument("phrase")
def translate(to: str, pinyin: bool, phrase: str):
    """Translate a phrase"""
    translation = Translator().translate(phrase, dest=to)
    if pinyin:
        translation = translation + f" ({Converter.to_pinyin(phrase)})"
    click.echo(translation)


@cli_group.group()
def manage_deck():
    """Manage deck subcommand"""


@manage_deck.command()
@click.option(
    "-c",
    "--character",
    default="simplified",
    type=click.Choice([SIMPLIFIED, TRADITIONAL]),
)
@click.argument("deck_name")
@click.argument("seed")
def create_deck(character: str, deck_name: str, seed: str):
    """Create a deck command from one seed word or phrase"""
    with FlashCardGenerator() as generator:
        flashcard = generator.create_flashcard(character, seed)
        DeckManager(deck_name).create_deck(flashcard)


@manage_deck.command()
@click.option(
    "-c",
    "--character",
    default="simplified",
    type=click.Choice([SIMPLIFIED, TRADITIONAL]),
)
@click.argument("deck_name")
@click.argument("word")
def add_note(character: str, deck_name: str, word: str):
    """add a note to an Anki deck with a word"""
    with FlashCardGenerator() as generator:
        flashcard = generator.create_flashcard(character, word)
        DeckManager(deck_name).add_note(flashcard)


@manage_deck.command()
@click.option(
    "-c",
    "--character",
    default="simplified",
    type=click.Choice([SIMPLIFIED, TRADITIONAL]),
)
@click.option(
    "--delimiter",
    default="\n",
)
@click.argument("deck_name")
@click.argument(
    "file_path",
    type=click.Path(exists=True, readable=True),
)
def add_note_from_file(character: str, delimiter: str, deck_name: str, file_path: str):
    """
    Add multiple notes to an Anki deck from a file containing words.

    Each word in the file will be converted to a flashcard and added to
    the specified deck. Words should be separated by the specified delimiter.

    Examples:
        laoshi manage-deck add-note-from-file my-deck words.txt
        laoshi manage-deck add-note-from-file -c traditional my-deck words.txt
        laoshi manage-deck add-note-from-file --delimiter ',' my-deck words.csv
    """
    try:
        # Read words from file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            words = [word.strip() for word in content.split(delimiter) if word.strip()]

        if not words:
            click.echo("No valid words found in the file.")
            return

        click.echo(f"Found {len(words)} words to process...")

        success_count = 0
        failed_words = []

        with FlashCardGenerator() as generator:
            deck_manager = DeckManager(deck_name)

            with click.progressbar(words, label="Adding notes") as bar:
                for word in bar:
                    try:
                        flashcard = generator.create_flashcard(character, word)
                        deck_manager.add_note(flashcard)
                        success_count += 1
                    except Exception as e:
                        failed_words.append((word, str(e)))
                        continue

        # Report results
        click.echo(
            f"\n✓ Successfully added {success_count} notes to deck '{deck_name}'"
        )

        if failed_words:
            click.echo(f"✗ Failed to add {len(failed_words)} notes:")
            for word, error in failed_words:
                click.echo(f"  - '{word}': {error}")

    except FileNotFoundError:
        click.echo(f"Error: File '{file_path}' not found.", err=True)
        raise click.Abort()
    except PermissionError:
        click.echo(f"Error: No permission to read file '{file_path}'.", err=True)
        raise click.Abort()
    except UnicodeDecodeError:
        click.echo(
            f"Error: Could not decode file '{file_path}'. Try specifying encoding.",
            err=True,
        )
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        raise click.Abort()


register_repl(cli_group)

if __name__ == "__main__":
    cli_group()
