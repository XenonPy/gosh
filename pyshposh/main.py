import os
import sys
import tomli
import asyncio
import aiofiles
from rich.console import Console
from rich.progress import track
from os import environ
from sys import platform

console = Console()

def clear_console():
    """Clear the console output."""
    console.print("\033[H\033[J", end="")

# async def async_input(prompt):
#     """Asynchronous input with proper handling."""
#     buffer = []
#     clear_console()
#     console.print(f"{prompt}{''.join(buffer)}", end='', style="white")

#     while True:
#         try:
#             char = await asyncio.to_thread(sys.stdin.read, 1)
#             if char == '\n':
#                 console.print()  # Move to the next line
#                 return ''.join(buffer).strip()
#             elif char == '\b':
#                 if buffer:
#                     buffer.pop()  # Handle backspace
#                     clear_console()
#                     console.print(f"{prompt}{''.join(buffer)}", end='', style="white")
#             else:
#                 buffer.append(char)
#                 console.print(char, end='', style="white")
#         except asyncio.CancelledError:
#             break
#         except Exception as e:
#             printError(f"Error reading input: {e}")

def print(txt):
    console.print(f"[white]{txt}")

def input(prompt):
    return console.input(f"[white]{prompt}")

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
    console.print(f"[red bold]An unknown error occurred.\n\n{txt}")

def printWarning(txt):
    console.print(f"[yellow italic]Warning: [bold]{txt}")

async def loadConfig():
    try:
        async with aiofiles.open("./.pyshposh", "rb") as f:
            config = tomli.loads((await f.read()).decode())
        return config
    except tomli.TOMLDecodeError:
        printError("Error decoding .pyshposh config")
    except FileNotFoundError:
        printWarning("Configuration file not found")
    except Exception as e:
        printUnknownError(e)

async def updateConsoleFromConfig(data, start=False):
    global console
    newColorSystem = data.get("dangerous", {}).get("colorScheme", None)
    if newColorSystem in ["auto", "standard", "256", "truecolor", "windows"]:
        currentColorSystem = console.color_system
        if newColorSystem != currentColorSystem:
            console = Console(color_system=newColorSystem)
            if not start:
                configUpdateMessage(f"Switched `color_system` to `{newColorSystem}`.")
    else:
        return

def getUser():
    return environ.get("USERNAME", "unknown") if platform.startswith("win") else environ.get("USER", "unknown")

async def simulate_task():
    print("Simulating a 20-second task. Try changing the config.\n")
    for _ in track(range(20), description="Working..."):
        await asyncio.sleep(1)
    print("Task complete!")

async def shell(config):
    await updateConsoleFromConfig(config)
    log("Started [green bold]Pyshposh")

    try:
        while True:
            await updateConsoleFromConfig(config)
            command = input(f"[green bold]{getUser()}@{os.uname().nodename} [blue bold]{os.getcwd()} [white]# ")

            if command.lower() == "leave":
                print("Exiting shell...")
                break
            elif command.lower() == "simtask":
                await simulate_task()
            else:
                log(f"Unknown command: {command}")
    except KeyboardInterrupt:
        print("\nUse [blue]'leave' [white]to quit.")
    except EOFError:
        print("\nExiting [green bold]Pyshposh...")
    except Exception as e:
        printUnknownError(e)

async def config_watcher():
    """Watch and update config only if changes occur."""
    last_config = None
    while True:
        config = await loadConfig()
        if config != last_config:
            last_config = config
            if config:
                await updateConsoleFromConfig(config)
        await asyncio.sleep(1)  # Increase interval to avoid excessive checks

async def main():
    config = await loadConfig()
    if config:
        await updateConsoleFromConfig(config, start=True)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Pyshposh requires a supported terminal to run correctly.")
        sys.exit(1)

    config_task = asyncio.create_task(config_watcher())
    shell_task = asyncio.create_task(shell(config))

    await asyncio.gather(config_task, shell_task)

if __name__ == "__main__":
    asyncio.run(main())
