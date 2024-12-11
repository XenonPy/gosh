import os
import sys
import rich
import tomli

from rich.console import Console

from os import environ
from sys import platform

console = Console()

def print(txt):
    console.print(f"[white]{txt}")

def errorLine():
    console.rule("[red bold]ERROR")

def log(txt):
    console.log(f"[white]{txt}")

def printError(txt):
    errorLine()
    console.print(f"[red bold]{txt}")

def printUnknownError(txt):
    errorLine()
    console.print(f"[red bold]An unknown error occured. \n\n{txt}")

def printWarning(txt):
    console.print(f"[yellow italic]Warning: [bold]{txt}")

def loadConfig():
    try:
        with open("./.pyshposh", "rb") as f:
            config = tomli.load(f)
        return config
    except tomli.TOMLDecodeError:
        printError("Error when decoding .pyshposh config")
    except FileNotFoundError:
        printWarning("Configuration file not found")
    except Exception as e:
        printUnknownError(e)

def getUser():
    return environ["USERNAME"] if platform.startswith("win") else environ["USER"]

def shell():
    log("Started [green bold]Pyshposh")

    while True:
        try:
            command = input("").strip()

            if command.lower() == "leave":
                print("Exiting shell...")
                break

        except KeyboardInterrupt:
            print("\nUse [blue]'leave' [white]to quit.")
        except EOFError:
            print("\nExiting [green bold]Pyshposh...")
            break
        except Exception as e:
            printUnknownError(e)

if __name__ == "__main__":
    loadConfig()
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Pyshposh requires a supported terminal to run correctly.")
        sys.exit(1)
    shell()
