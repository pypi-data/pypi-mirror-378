#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import time
import json

class CurlLoopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Curl Loop Runner")
        self.root.geometry("800x600")
        
        self.is_running = False
        self.thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Sleep time input
        ttk.Label(main_frame, text="Sleep Time (seconds):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.sleep_time = tk.StringVar(value="5")
        sleep_entry = ttk.Entry(main_frame, textvariable=self.sleep_time, width=10)
        sleep_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Curl command input
        ttk.Label(main_frame, text="Curl Command:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.curl_command = scrolledtext.ScrolledText(main_frame, height=4, wrap=tk.WORD)
        self.curl_command.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        self.curl_command.insert("1.0", "curl -X GET https://api.github.com")
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_loop)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_loop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = ttk.Label(button_frame, text="Status: Stopped", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Response display
        ttk.Label(main_frame, text="Response:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        response_frame = ttk.Frame(main_frame)
        response_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD)
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status code display
        self.status_code_label = ttk.Label(main_frame, text="Status Code: N/A", font=("TkDefaultFont", 10, "bold"))
        self.status_code_label.grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        
        # Last update time
        self.last_update_label = ttk.Label(main_frame, text="Last Update: Never")
        self.last_update_label.grid(row=7, column=0, sticky=tk.W, pady=(5, 0))
        
    def start_loop(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running", foreground="green")
            
            self.thread = threading.Thread(target=self.run_curl_loop, daemon=True)
            self.thread.start()
    
    def stop_loop(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def run_curl_loop(self):
        while self.is_running:
            try:
                # Get the curl command
                curl_cmd = self.curl_command.get("1.0", tk.END).strip()
                
                if not curl_cmd:
                    self.update_response("Error: No curl command provided", "N/A")
                    time.sleep(1)
                    continue
                
                # Add -w option to get HTTP status code
                if "-w" not in curl_cmd:
                    curl_cmd += ' -w "\\n__STATUS_CODE__:%{http_code}"'
                
                # Add -s to silence progress
                if "-s" not in curl_cmd:
                    curl_cmd = curl_cmd.replace("curl", "curl -s", 1)
                
                # Execute curl command
                result = subprocess.run(
                    curl_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output = result.stdout
                
                # Extract status code if we added it
                status_code = "N/A"
                if "__STATUS_CODE__:" in output:
                    parts = output.rsplit("__STATUS_CODE__:", 1)
                    if len(parts) == 2:
                        output = parts[0]
                        status_code = parts[1].strip()
                
                # Try to pretty print JSON
                try:
                    json_data = json.loads(output)
                    formatted_output = json.dumps(json_data, indent=2)
                except:
                    formatted_output = output
                
                # Update UI
                self.update_response(formatted_output, status_code)
                
                # Sleep for specified time
                sleep_time = float(self.sleep_time.get() or 5)
                time.sleep(sleep_time)
                
            except subprocess.TimeoutExpired:
                self.update_response("Error: Request timed out (30 seconds)", "Timeout")
                time.sleep(1)
            except Exception as e:
                self.update_response(f"Error: {str(e)}", "Error")
                time.sleep(1)
    
    def update_response(self, response, status_code):
        def update():
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert("1.0", response)
            
            if status_code == "200":
                self.status_code_label.config(text=f"Status Code: {status_code}", foreground="green")
            elif status_code in ["N/A", "Error", "Timeout"]:
                self.status_code_label.config(text=f"Status Code: {status_code}", foreground="red")
            else:
                self.status_code_label.config(text=f"Status Code: {status_code}", foreground="orange")
            
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.last_update_label.config(text=f"Last Update: {current_time}")
        
        self.root.after(0, update)

def main():
    root = tk.Tk()
    app = CurlLoopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()