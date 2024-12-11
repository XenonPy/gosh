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

def storeUserInput(input_text):
    config["user_input"] = input_text
    configUpdateMessage(f"User input stored: {input_text}")

def loadUserInput():
    return config.get("user_input", "")

def shell():
    log("Started [green bold]Pyshposh")
    updater_thread = threading.Thread(target=backgroundUpdater, daemon=True)
    updater_thread.start()
    
    user_input_buffer = ""
    inactivity_timer = None

    def reset_inactivity_timer():
        nonlocal inactivity_timer
        if inactivity_timer:
            inactivity_timer.cancel()
        inactivity_timer = threading.Timer(1.0, on_inactivity)
        inactivity_timer.start()

    def on_inactivity():
        nonlocal user_input_buffer
        storeUserInput(user_input_buffer)
        user_input_buffer = ""

    try:
        while True:
            updateConsoleFromConfig(config)
            user_input = loadUserInput()
            command = input(f"{user_input}").strip()
            user_input_buffer = command  # buffer
            reset_inactivity_timer()

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
    except Exception as e:
        printUnknownError(e)
    finally:
        consoleUpdateQueue.put(None)
        updater_thread.join()

if __name__ == "__main__":
    config = loadConfig()
    if config:
        updateConsoleFromConfig(config, start=True)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Pyshposh requires a supported terminal to run correctly.")
        sys.exit(1)
    shell()
