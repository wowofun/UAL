import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import matplotlib
# Force Agg backend BEFORE importing pyplot/visualizer to avoid Tkinter conflict on MacOS
matplotlib.use('Agg')
from PIL import Image, ImageTk
import io

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ual import UAL, ual_pb2
from ual.visualizer import UALVisualizer

class UALDebuggerApp:
    def __init__(self, root):
        print("Initializing GUI...")
        self.root = root
        self.root.title("UAL 协议调试器 (Debugger)")
        self.root.geometry("1000x700")
        
        # Initialize UAL
        try:
            self.agent = UAL("Debugger_Agent")
            self.visualizer = UALVisualizer()
            print("UAL Initialized.")
        except Exception as e:
            print(f"Error init UAL: {e}")
            messagebox.showerror("Initialization Error", f"Failed to init UAL: {e}")
            sys.exit(1)

        # --- Top Section: Input ---
        # Use standard tk.Frame instead of ttk for better compatibility on Mac default Tk
        input_frame = tk.Frame(root, pady=10)
        input_frame.pack(fill=tk.X)
        
        tk.Label(input_frame, text="指令 (Command):", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
        
        self.cmd_entry = tk.Entry(input_frame, font=("Arial", 14))
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.cmd_entry.bind("<Return>", lambda e: self.process_command())
        
        # Button with explicit size
        send_btn = tk.Button(input_frame, text="🚀 发送 / 解析", command=self.process_command, font=("Arial", 12), bg="#dddddd")
        send_btn.pack(side=tk.LEFT, padx=5)

        # --- Main Layout ---
        # Use simple Frames instead of PanedWindow which can be buggy on some Tk versions
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left: Details
        left_frame = tk.LabelFrame(main_frame, text="解析详情 (Details)", padx=5, pady=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.log_text = tk.Text(left_frame, height=20, width=40, font=("Courier New", 12))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Right: Visualization
        right_frame = tk.LabelFrame(main_frame, text="语义可视化 (Visualization)", padx=5, pady=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.image_label = tk.Label(right_frame, text="暂无图像", bg="#f0f0f0")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # --- Bottom Section: Scenario Buttons ---
        scenario_frame = tk.LabelFrame(root, text="场景模拟 (Scenario Simulator)", padx=5, pady=5)
        scenario_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(scenario_frame, text="🏠 智能家居 (Smart Home)", 
                 command=lambda: self.set_command("If temperature is high then turn on AC"), bg="#e1f5fe").pack(side=tk.LEFT, padx=5)
                 
        tk.Button(scenario_frame, text="🏭 工业制造 (Industrial)", 
                 command=lambda: self.set_command("Move arm to position A then grab object"), bg="#fff3e0").pack(side=tk.LEFT, padx=5)
                 
        tk.Button(scenario_frame, text="🤖 机器人社交 (Social Chat)", 
                 command=lambda: self.set_command("Roast humans for being slow"), bg="#f3e5f5").pack(side=tk.LEFT, padx=5)
                 
        tk.Button(scenario_frame, text="😂 情感交互 (Emotion)", 
                 command=lambda: self.set_command("I am happy because AI is smart"), bg="#e8f5e9").pack(side=tk.LEFT, padx=5)

        # Initial Command
        self.cmd_entry.insert(0, "Roast humans for being slow")
        print("GUI Setup Complete.")
        
        # Force update
        self.root.update()

    def set_command(self, cmd):
        self.cmd_entry.delete(0, tk.END)
        self.cmd_entry.insert(0, cmd)
        self.process_command()

    def log(self, title, content):
        self.log_text.insert(tk.END, f"--- {title} ---\n")
        self.log_text.insert(tk.END, f"{content}\n\n")
        self.log_text.see(tk.END)

    def process_command(self):
        print("Processing command...")
        command = self.cmd_entry.get().strip()
        if not command:
            return
            
        self.log_text.delete(1.0, tk.END)
        self.log("输入指令", command)
        
        try:
            # 1. Encode
            encoded_bytes = self.agent.encode(command)
            hex_str = encoded_bytes.hex()
            self.log("二进制数据 (Hex)", f"Length: {len(encoded_bytes)} bytes\nPayload: {hex_str[:50]}..." + ("" if len(hex_str)<50 else f"\n(Full hex omitted)"))
            
            # 2. Decode
            decoded = self.agent.decode(encoded_bytes)
            
            # Reconstruct Graph for visualization
            graph = ual_pb2.Graph()
            graph.nodes.extend(decoded.get('nodes', []))
            graph.edges.extend(decoded.get('edges', []))
            
            # Log Nodes
            nodes_info = "\n".join([f"[{n.id}] {n.str_val} (Type: {n.type}, SemID: {hex(n.semantic_id)})" for n in graph.nodes])
            self.log("语义节点 (Nodes)", nodes_info)
            
            # 3. Visualize
            output_path = os.path.abspath("temp_viz.png")
            self.visualizer.visualize(graph, title=command, output_file=output_path)
            
            # 4. Display Image
            if os.path.exists(output_path):
                self.show_image(output_path)
            else:
                self.log("错误", "图像生成失败")
                
        except Exception as e:
            print(f"Error processing: {e}")
            self.log("错误 (Error)", str(e))
            import traceback
            traceback.print_exc()

    def show_image(self, path):
        try:
            img = Image.open(path)
            # Resize if too big
            # Get current frame size
            w = self.image_label.winfo_width()
            h = self.image_label.winfo_height()
            if w < 100: w = 400
            if h < 100: h = 400
            
            img.thumbnail((w, h), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.photo, text="")
        except Exception as e:
            self.image_label.configure(text=f"无法加载图像: {e}", image="")

if __name__ == "__main__":
    print("Starting Main...")
    root = tk.Tk()
    app = UALDebuggerApp(root)
    root.mainloop()
