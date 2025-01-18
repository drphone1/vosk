import os
import wave
import logging
import json
from vosk import Model, KaldiRecognizer
from colorama import Fore, Style, init  # For colored text
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.console import Console
from rich.live import Live

# Initialize colorama
init(autoreset=True)

# Set Vosk log level to WARNING to hide unnecessary logs
logging.getLogger("vosk").setLevel(logging.WARNING)

def print_step(message, color=Fore.WHITE):
    """Print a step message with color."""
    print(f"{color}✨ {message}{Style.RESET_ALL}")

def transcribe_audio(model_path, audio_file, output_json="output.json", output_txt="output.txt"):
    """Transcribe an audio file to text and save the output in both JSON and plain text formats."""
    
    # Check if the model exists
    print_step("Checking Persian model...", Fore.MAGENTA)
    if not os.path.exists(model_path):
        print_step(f"❌ Persian model not found at {model_path}!", Fore.RED)
        exit(1)
    
    # Load the model
    print_step("Loading Persian model...", Fore.BLUE)
    model = Model(model_path)
    print_step("✅ Persian model loaded successfully.", Fore.GREEN)
    
    # Check if the audio file exists
    print_step("Checking audio file...", Fore.CYAN)
    if not os.path.exists(audio_file):
        print_step(f"❌ Audio file not found at {audio_file}!", Fore.RED)
        exit(1)
    
    # Open the audio file
    print_step("Opening audio file...", Fore.YELLOW)
    try:
        wf = wave.open(audio_file, "rb")
    except Exception as e:
        print_step(f"❌ Error opening audio file: {e}", Fore.RED)
        exit(1)
    print_step("✅ Audio file opened successfully.", Fore.GREEN)
    
    # Validate audio file specifications
    print_step("Validating audio file specifications...", Fore.LIGHTBLUE_EX)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
        print_step("❌ Audio file must be mono, 16-bit, and have a sample rate of 8000 or 16000 Hz!", Fore.RED)
        exit(1)
    print_step("✅ Audio file specifications validated.", Fore.GREEN)
    
    # Initialize the recognizer
    print_step("Initializing recognizer...", Fore.LIGHTMAGENTA_EX)
    recognizer = KaldiRecognizer(model, wf.getframerate())
    print_step("✅ Recognizer initialized successfully.", Fore.GREEN)
    
    # Calculate total frames for progress bar
    total_frames = wf.getnframes()
    frames_processed = 0
    chunk_size = 4000  # Size of each chunk to process
    
    # Initialize Rich console and progress bar
    console = Console()
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    )
    
    # Create a table for progress metrics
    table = Table(title="Audio Processing Progress", width=50)
    table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    # Start audio-to-text conversion
    print_step("Starting audio-to-text conversion...", Fore.LIGHTCYAN_EX)
    results = []
    with Live(console=console, refresh_per_second=10) as live:
        task = progress.add_task("[cyan]Processing audio...", total=total_frames)
        while True:
            data = wf.readframes(chunk_size)
            frames_processed += len(data)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                results.append(json.loads(result))  # Store result as a dictionary
            
            # Update progress bar
            progress.update(task, advance=len(data))
            
            # Update the table with progress metrics
            speed = progress.tasks[task].speed or 0  # Processing speed (frames per second)
            time_remaining = progress.tasks[task].time_remaining or 0  # Remaining time
            table.rows = [
                ("Frames Processed", f"{frames_processed:,}"),
                ("Total Frames", f"{total_frames:,}"),
                ("Processing Speed", f"{speed:,.2f} frames/s"),
                ("Time Remaining", f"{time_remaining:.2f} seconds"),
            ]
            
            # Display the table and progress bar
            live.update(table)
            live.update(progress)
    
    # Get the final result
    final_result = recognizer.FinalResult()
    results.append(json.loads(final_result))  # Store final result as a dictionary
    
    # Close the audio file
    print_step("Closing audio file...", Fore.LIGHTRED_EX)
    wf.close()
    print_step("✅ Audio file closed successfully.", Fore.GREEN)
    
    # Save the transcription to the output files
    print_step("Saving transcription results...", Fore.LIGHTGREEN_EX)
    try:
        # Save as JSON
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print_step(f"✅ Transcription saved successfully to {output_json}.", Fore.GREEN)
        
        # Save as plain text
        with open(output_txt, "w", encoding="utf-8") as f:
            for result in results:
                if "text" in result:
                    f.write(result["text"] + "\n")
        print_step(f"✅ Transcription saved successfully to {output_txt}.", Fore.GREEN)
    except Exception as e:
        print_step(f"❌ Error saving transcription: {e}", Fore.RED)
    
    # Display the transcription result
    print_step("Transcription result:", Fore.LIGHTBLUE_EX)
    for result in results:
        if "text" in result:
            print(Fore.LIGHTCYAN_EX + result["text"])

# Path to the Persian model
model_path = r"E:\1 python\voice to text\vosk-model-fa-0.42\vosk-model-fa-0.42"  # Update this path

# Get the audio file path from the user
while True:
    audio_file = input("Please enter the path to your audio file: ").strip()  # Get the audio file path
    if os.path.exists(audio_file):  # Check if the file exists
        break
    else:
        print(Fore.RED + "❌ Audio file not found! Please enter a valid path.")

# Output file paths
output_json = "output.json"  # JSON output
output_txt = "output.txt"    # Plain text output

# Start the transcription process
transcribe_audio(model_path, audio_file, output_json, output_txt)

# Wait for the user to press Enter before exiting
input("\nPress Enter to exit...")