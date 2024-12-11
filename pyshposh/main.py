import os
import sys
import rich
import tomli
import threading
import time
from queue import Queue

from rich.console import Console
from rich.progress import track

from os import environ
from sys import platform

console = Console()

def print(txt):
    console.print(f"[white]{txt}")

def configUpdateMessage(txt):
    console.print(f"[green bold]📝 Config Update: {txt}")

def errorLine():
    console.rule("[red bold]ERROR")

def log(txt):
    console.log(f"[white]{txt}")

def printError(txt):
    errorLine()
    console.print(f"[red bold]{txt}")

def printUnknownError(txt):
    errorLine()
    console.print(f"[red bold]An unknown error occurred. \n\n{txt}")

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

def updateConsoleFromConfig(data, start=False):
    global console
    newColorSystem = data["dangerous"]["colorScheme"]
    if newColorSystem in ["auto", "standard", "256", "truecolor", "windows"]:
        currentColorSystem = console.color_system
        if newColorSystem != currentColorSystem:
            console = Console(color_system=newColorSystem)
            if not start:
                configUpdateMessage(f"Switched `color_system` to `{newColorSystem}`.")
    else:
        return

def getUser():
    return environ["USERNAME"] if platform.startswith("win") else environ["USER"]

consoleUpdateQueue = Queue()

def backgroundUpdater():
    while True:
        try:
            message = consoleUpdateQueue.get(timeout=0.5)
            if message is None:
                break
            log(message)
        except Exception:
            pass

def shell():
    log("Started [green bold]Pyshposh")
    updater_thread = threading.Thread(target=backgroundUpdater, daemon=True)
    updater_thread.start()
    try:
        while True:
            updateConsoleFromConfig(config)
            try:
                command = input("").strip()
                if command.lower() == "leave":
                    print("Exiting shell...")
                    break
                elif command.lower() == "simtask":
                    consoleUpdateQueue.put("Simulating a 20-second task. Try changing the config.\n")
                    for i in track(range(20), description="Working..."):
                        time.sleep(1)
                    consoleUpdateQueue.put("Task complete!")
                else:
                    log(f"Unknown command: {command}")
            except KeyboardInterrupt:
                print("\nUse [blue]'leave' [white]to quit.")
            except EOFError:
                print("\nExiting [green bold]Pyshposh...")
                break
            except Exception as e:
                printUnknownError(e)
    finally:
        consoleUpdateQueue.put(None)
        updater_thread.join()

if __name__ == "__main__":
    config = loadConfig()
    if config:
        updateConsoleFromConfig(config, start=True)  # Use start=True to suppress initial message
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Pyshposh requires a supported terminal to run correctly.")
        sys.exit(1)
    shell()