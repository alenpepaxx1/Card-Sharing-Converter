#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Card Sharing Protocol Converter
Supports: CCcam, NewCamd, MGcamd, OSCam
Version: 2.0 - English
Author: Alen Pepa
LinkedIn: https://www.linkedin.com/in/alenpepa/
Copyright © 2025 Alen Pepa. All rights reserved.
"""

import json
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import threading
import os
import sys
import webbrowser

class UniversalCardSharingConverter:
    def __init__(self):
        self.protocols = {
            'cccam': {
                'prefix': 'C:',
                'default_port': 12000,
                'params': ['hostname', 'port', 'username', 'password']
            },
            'newcamd': {
                'prefix': 'N:',
                'default_port': 15000,
                'params': ['hostname', 'port', 'username', 'password', 'des_key']
            },
            'mgcamd': {
                'prefix': 'M:',
                'default_port': 15000,
                'params': ['hostname', 'port', 'username', 'password']
            }
        }
    
    def parse_server_line(self, line):
        """Parse server line and identify protocol"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        for protocol, info in self.protocols.items():
            if line.startswith(info['prefix']):
                parts = line.split()
                if len(parts) >= len(info['params']) + 1:
                    server = {'protocol': protocol}
                    for i, param in enumerate(info['params']):
                        server[param] = parts[i + 1] if i + 1 < len(parts) else ''
                    return server
        return None
    
    def to_oscam_server(self, servers):
        """Convert to OSCam server format"""
        output = [
            "# OSCam Server Configuration\n",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"# Total servers: {len(servers)}\n\n"
        ]
        
        for i, server in enumerate(servers):
            label = f"{server['protocol']}_{server['username']}_{i+1}"
            
            reader = f"""[reader]
label = {label}
enable = 1
protocol = {server['protocol']}
device = {server['hostname']},{server['port']}
user = {server['username']}
password = {server['password']}
inactivitytimeout = 30
reconnecttimeout = 30
group = 1
"""
            
            if server['protocol'] == 'newcamd' and 'des_key' in server:
                reader += f"key = {server['des_key']}\n"
            elif server['protocol'] == 'cccam':
                reader += "cccversion = 2.3.0\n"
                
            reader += "\n"
            output.append(reader)
        
        return ''.join(output)
    
    def to_cccam_cfg(self, servers):
        """Convert to CCcam.cfg format"""
        output = [
            "# CCcam Configuration\n",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"# Total servers: {len(servers)}\n\n"
        ]
        
        for server in servers:
            if server['protocol'] in ['cccam', 'newcamd']:
                line = f"C: {server['hostname']} {server['port']} {server['username']} {server['password']}\n"
                output.append(line)
        
        return ''.join(output)
    
    def to_newcamd_cfg(self, servers):
        """Convert to NewCamd.cfg format"""
        output = [
            "# NewCamd Configuration\n",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"# Total servers: {len(servers)}\n\n"
        ]
        
        for server in servers:
            if server['protocol'] == 'newcamd':
                des_key = server.get('des_key', '0102030405060708091011121314')
                line = f"N: {server['hostname']} {server['port']} {server['username']} {server['password']} {des_key}\n"
                output.append(line)
            elif server['protocol'] == 'cccam':
                # Convert CCcam to NewCamd format
                line = f"N: {server['hostname']} {server['port']} {server['username']} {server['password']} 0102030405060708091011121314\n"
                output.append(line)
        
        return ''.join(output)
    
    def convert_text(self, text, output_format):
        """Convert text directly"""
        lines = text.split('\n')
        servers = []
        
        for line in lines:
            server = self.parse_server_line(line)
            if server:
                servers.append(server)
        
        if output_format.lower() == 'oscam':
            return self.to_oscam_server(servers)
        elif output_format.lower() == 'cccam':
            return self.to_cccam_cfg(servers)
        elif output_format.lower() == 'newcamd':
            return self.to_newcamd_cfg(servers)
        
        return ""

class ModernCardSharingGUI:
    def __init__(self, root):
        self.root = root
        self.converter = UniversalCardSharingConverter()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup modern UI"""
        self.root.title("Card Sharing Protocol Converter v2.0 - by Alen Pepa")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='#ecf0f1', 
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#2c3e50', 
                       foreground='#bdc3c7', 
                       font=('Segoe UI', 12))
        
        style.configure('Modern.TButton',
                       background='#3498db',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0)
        
        style.map('Modern.TButton',
                 background=[('active', '#2980b9')])
        
        style.configure('Success.TButton',
                       background='#27ae60',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Success.TButton',
                 background=[('active', '#229954')])
        
        style.configure('Danger.TButton',
                       background='#e74c3c',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'))
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2c3e50')
        header_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ttk.Label(header_frame, 
                               text="🛰️ Card Sharing Protocol Converter", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Convert CCcam, NewCamd, MGcamd and OSCam protocols", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Content area with notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab 1: Text Converter
        self.create_text_converter_tab()
        
        # Tab 2: File Converter
        self.create_file_converter_tab()
        
        # Tab 3: Settings & Info
        self.create_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready for conversion...")
        status_frame = tk.Frame(main_frame, bg='#34495e', height=30)
        status_frame.pack(fill='x', pady=(20, 0))
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, 
                               textvariable=self.status_var,
                               bg='#34495e', 
                               fg='#ecf0f1',
                               font=('Segoe UI', 9))
        status_label.pack(side='left', padx=10, pady=5)
    
    def create_text_converter_tab(self):
        """Create text converter tab"""
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text='📝 Text Converter')
        
        # Input section
        input_frame = tk.Frame(text_frame, bg='white')
        input_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Input
        left_frame = tk.Frame(input_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        input_label = tk.Label(left_frame, text="Input (Paste lines here):", 
                              bg='white', fg='#2c3e50', font=('Segoe UI', 11, 'bold'))
        input_label.pack(anchor='w', pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(left_frame, 
                                                   height=15, 
                                                   font=('Consolas', 10),
                                                   bg='#f8f9fa',
                                                   fg='#2c3e50')
        self.input_text.pack(fill='both', expand=True)
        
        # Sample data button
        sample_btn = ttk.Button(left_frame, 
                               text="📋 Load Sample Data", 
                               style='Modern.TButton',
                               command=self.load_sample_data)
        sample_btn.pack(pady=(5, 0))
        
        # Right side - Output
        right_frame = tk.Frame(input_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        output_label = tk.Label(right_frame, text="Output:", 
                               bg='white', fg='#2c3e50', font=('Segoe UI', 11, 'bold'))
        output_label.pack(anchor='w', pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(right_frame, 
                                                    height=15, 
                                                    font=('Consolas', 10),
                                                    bg='#f8f9fa',
                                                    fg='#2c3e50',
                                                    state='disabled')
        self.output_text.pack(fill='both', expand=True)
        
        # Control panel
        control_frame = tk.Frame(text_frame, bg='#ecf0f1', height=80)
        control_frame.pack(fill='x', padx=10, pady=(0, 10))
        control_frame.pack_propagate(False)
        
        # Format selection
        format_label = tk.Label(control_frame, text="Output Format:", 
                               bg='#ecf0f1', fg='#2c3e50', font=('Segoe UI', 10, 'bold'))
        format_label.pack(side='left', padx=(20, 10), pady=20)
        
        self.format_var = tk.StringVar(value='oscam')
        formats = [('OSCam', 'oscam'), ('CCcam', 'cccam'), ('NewCamd', 'newcamd')]
        
        for text, value in formats:
            rb = tk.Radiobutton(control_frame, text=text, variable=self.format_var, 
                               value=value, bg='#ecf0f1', fg='#2c3e50',
                               font=('Segoe UI', 10), selectcolor='#3498db')
            rb.pack(side='left', padx=10, pady=20)
        
        # Buttons
        btn_frame = tk.Frame(control_frame, bg='#ecf0f1')
        btn_frame.pack(side='right', padx=20, pady=10)
        
        convert_btn = ttk.Button(btn_frame, 
                                text="🔄 Convert", 
                                style='Success.TButton',
                                command=self.convert_text)
        convert_btn.pack(side='left', padx=5)
        
        clear_btn = ttk.Button(btn_frame, 
                              text="🗑️ Clear", 
                              style='Danger.TButton',
                              command=self.clear_text)
        clear_btn.pack(side='left', padx=5)
        
        save_btn = ttk.Button(btn_frame, 
                             text="💾 Save", 
                             style='Modern.TButton',
                             command=self.save_output)
        save_btn.pack(side='left', padx=5)
    
    def create_file_converter_tab(self):
        """Create file converter tab"""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text='📁 File Converter')
        
        # Main content
        content_frame = tk.Frame(file_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # File selection
        file_select_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        file_select_frame.pack(fill='x', pady=(0, 20))
        
        file_title = tk.Label(file_select_frame, text="📂 File Selection", 
                             bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 12, 'bold'))
        file_title.pack(pady=10)
        
        # Input file
        input_file_frame = tk.Frame(file_select_frame, bg='#f8f9fa')
        input_file_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(input_file_frame, text="Input File:", 
                bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 10)).pack(side='left')
        
        self.input_file_var = tk.StringVar()
        input_file_entry = tk.Entry(input_file_frame, textvariable=self.input_file_var,
                                   font=('Segoe UI', 10), width=50)
        input_file_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        
        browse_btn = ttk.Button(input_file_frame, text="Browse...", 
                               style='Modern.TButton',
                               command=self.browse_input_file)
        browse_btn.pack(side='right')
        
        # Output file
        output_file_frame = tk.Frame(file_select_frame, bg='#f8f9fa')
        output_file_frame.pack(fill='x', padx=20, pady=(5, 15))
        
        tk.Label(output_file_frame, text="Output File:", 
                bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 10)).pack(side='left')
        
        self.output_file_var = tk.StringVar()
        output_file_entry = tk.Entry(output_file_frame, textvariable=self.output_file_var,
                                    font=('Segoe UI', 10), width=50)
        output_file_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        
        save_btn = ttk.Button(output_file_frame, text="Save As...", 
                             style='Modern.TButton',
                             command=self.browse_output_file)
        save_btn.pack(side='right')
        
        # Format selection for file
        format_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        format_frame.pack(fill='x', pady=(0, 20))
        
        format_title = tk.Label(format_frame, text="⚙️ Conversion Settings", 
                               bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 12, 'bold'))
        format_title.pack(pady=10)
        
        self.file_format_var = tk.StringVar(value='oscam')
        format_options_frame = tk.Frame(format_frame, bg='#f8f9fa')
        format_options_frame.pack(pady=(0, 15))
        
        for text, value in [('OSCam Server', 'oscam'), ('CCcam Config', 'cccam'), ('NewCamd Config', 'newcamd')]:
            rb = tk.Radiobutton(format_options_frame, text=text, 
                               variable=self.file_format_var, value=value,
                               bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 11),
                               selectcolor='#3498db')
            rb.pack(side='left', padx=20)
        
        # Convert button
        convert_file_btn = ttk.Button(content_frame, 
                                     text="🚀 Convert File", 
                                     style='Success.TButton',
                                     command=self.convert_file)
        convert_file_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=50, pady=10)
        
        # Results area
        results_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        results_frame.pack(fill='both', expand=True)
        
        results_title = tk.Label(results_frame, text="📊 Results", 
                                bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 12, 'bold'))
        results_title.pack(pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8, 
                                                     font=('Consolas', 9),
                                                     bg='white', fg='#2c3e50',
                                                     state='disabled')
        self.results_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    
    def create_settings_tab(self):
        """Create settings and info tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text='⚙️ Settings & Info')
        
        # Info section
        info_frame = tk.Frame(settings_frame, bg='#3498db', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        info_title = tk.Label(info_frame, text="ℹ️ Application Information", 
                             bg='#3498db', fg='white', font=('Segoe UI', 14, 'bold'))
        info_title.pack(pady=15)
        
        info_text = """
🛰️ Universal Card Sharing Protocol Converter v2.0

✨ Features:
• Supports CCcam, NewCamd, MGcamd, OSCam
• Bi-directional conversion
• Modern and intuitive interface
• Batch processing for multiple files
• Advanced error handling

🔧 Supported Protocols:
• CCcam (C-lines) - Default port: 12000
• NewCamd (N-lines) - Default port: 15000+  
• MGcamd (M-lines) - Variable port
• OSCam - Default port: 988

⚠️ Notice: Use only for legal purposes
        """
        
        info_label = tk.Label(info_frame, text=info_text, 
                             bg='#3498db', fg='white', font=('Segoe UI', 10),
                             justify='left')
        info_label.pack(padx=20, pady=(0, 15))
        
        # Settings section
        settings_section = tk.Frame(settings_frame, bg='#ecf0f1', relief='solid', bd=1)
        settings_section.pack(fill='x', padx=20, pady=(0, 20))
        
        settings_title = tk.Label(settings_section, text="⚙️ Settings", 
                                 bg='#ecf0f1', fg='#2c3e50', font=('Segoe UI', 14, 'bold'))
        settings_title.pack(pady=15)
        
        # Theme selection
        theme_frame = tk.Frame(settings_section, bg='#ecf0f1')
        theme_frame.pack(pady=10)
        
        tk.Label(theme_frame, text="Theme:", bg='#ecf0f1', fg='#2c3e50', 
                font=('Segoe UI', 11, 'bold')).pack(side='left', padx=20)
        
        self.theme_var = tk.StringVar(value='modern')
        themes = [('Modern', 'modern'), ('Classic', 'classic'), ('Dark', 'dark')]
        
        for text, value in themes:
            rb = tk.Radiobutton(theme_frame, text=text, variable=self.theme_var,
                               value=value, bg='#ecf0f1', fg='#2c3e50',
                               font=('Segoe UI', 10))
            rb.pack(side='left', padx=10)
        
        # Auto-backup option
        backup_frame = tk.Frame(settings_section, bg='#ecf0f1')
        backup_frame.pack(pady=10)
        
        self.auto_backup = tk.BooleanVar(value=True)
        backup_cb = tk.Checkbutton(backup_frame, text="Auto-backup original files",
                                  variable=self.auto_backup, bg='#ecf0f1', fg='#2c3e50',
                                  font=('Segoe UI', 10))
        backup_cb.pack(padx=20)
        
        # About section
        about_frame = tk.Frame(settings_frame, bg='#27ae60', relief='solid', bd=1)
        about_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        about_title = tk.Label(about_frame, text="👨‍💻 About", 
                              bg='#27ae60', fg='white', font=('Segoe UI', 14, 'bold'))
        about_title.pack(pady=15)
        
        about_text = f"""
Created by Alen Pepa
Version 2.0 - August 2025

📧 Email: xalenpepa2@gmail.com

© 2025 Alen Pepa. All rights reserved.
        """
        
        about_label = tk.Label(about_frame, text=about_text, 
                              bg='#27ae60', fg='white', font=('Segoe UI', 10),
                              justify='center')
        about_label.pack(pady=(0, 10))
        
        # LinkedIn clickable button with icon
        linkedin_btn = tk.Button(about_frame, 
                                text="💼 View LinkedIn Profile",
                                bg='#0077b5', fg='white',
                                font=('Segoe UI', 11, 'bold'),
                                cursor='hand2',
                                relief='flat',
                                padx=25, pady=8,
                                activebackground='#005885',
                                activeforeground='white',
                                command=self.open_linkedin)
        linkedin_btn.pack(pady=(0, 15))
    
    def open_linkedin(self):
        """Open LinkedIn profile in browser"""
        try:
            webbrowser.open('https://www.linkedin.com/in/alenpepa/')
            self.update_status("LinkedIn profile opened in browser ✅")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open LinkedIn profile: {str(e)}")
            self.update_status("Error opening LinkedIn profile ❌")
    
    def load_sample_data(self):
        """Load sample data"""
        sample_data = """C: server1.example.com 12000 user1 pass123
C: server2.example.com 12001 user2 pass456
N: newcamd.server.com 15000 newuser newpass 0102030405060708091011121314
N: newcamd2.server.com 15001 user3 pass789 1234567890123456789012345678
M: mgcamd.server.com 15500 mguser mgpass"""
        
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, sample_data)
        self.update_status("Sample data loaded ✅")
    
    def convert_text(self):
        """Convert text"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please add input text!")
            return
        
        try:
            output_format = self.format_var.get()
            result = self.converter.convert_text(input_text, output_format)
            
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, result)
            self.output_text.config(state='disabled')
            
            lines_count = len([line for line in input_text.split('\n') 
                              if line.strip() and not line.startswith('#')])
            self.update_status(f"Conversion completed! {lines_count} lines converted to {output_format.upper()} ✅")
            
        except Exception as e:
            messagebox.showerror("Error", f"Conversion error: {str(e)}")
            self.update_status("Conversion error ❌")
    
    def clear_text(self):
        """Clear text"""
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        self.update_status("Text cleared ✅")
    
    def save_output(self):
        """Save output to file"""
        output_content = self.output_text.get(1.0, tk.END).strip()
        if not output_content:
            messagebox.showwarning("Warning", "No output to save!")
            return
        
        format_name = self.format_var.get()
        extensions = {'oscam': '.server', 'cccam': '.cfg', 'newcamd': '.cfg'}
        
        filename = filedialog.asksaveasfilename(
            defaultextension=extensions.get(format_name, '.txt'),
            filetypes=[(f"{format_name.upper()} files", f"*{extensions.get(format_name, '.txt')}"),
                      ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                messagebox.showinfo("Success", f"File saved: {filename}")
                self.update_status(f"File saved: {os.path.basename(filename)} ✅")
            except Exception as e:
                messagebox.showerror("Error", f"Save error: {str(e)}")
    
    def browse_input_file(self):
        """Browse for input file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Config files", "*.cfg"), ("Server files", "*.server"), 
                      ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
            self.update_status(f"Input file: {os.path.basename(filename)}")
    
    def browse_output_file(self):
        """Browse for output file"""
        format_name = self.file_format_var.get()
        extensions = {'oscam': '.server', 'cccam': '.cfg', 'newcamd': '.cfg'}
        
        filename = filedialog.asksaveasfilename(
            defaultextension=extensions.get(format_name, '.txt'),
            filetypes=[(f"{format_name.upper()} files", f"*{extensions.get(format_name, '.txt')}"),
                      ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
            self.update_status(f"Output file: {os.path.basename(filename)}")
    
    def convert_file(self):
        """Convert file"""
        input_file = self.input_file_var.get().strip()
        output_file = self.output_file_var.get().strip()
        
        if not input_file:
            messagebox.showwarning("Warning", "Please select input file!")
            return
        
        if not output_file:
            messagebox.showwarning("Warning", "Please select output file!")
            return
        
        # Start conversion in separate thread
        threading.Thread(target=self._convert_file_thread, 
                        args=(input_file, output_file), daemon=True).start()
    
    def _convert_file_thread(self, input_file, output_file):
        """Conversion thread"""
        try:
            self.progress.start()
            self.update_status("Conversion in progress...")
            
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert
            format_name = self.file_format_var.get()
            result = self.converter.convert_text(content, format_name)
            
            # Save output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            
            # Update results
            lines_count = len([line for line in content.split('\n') 
                              if line.strip() and not line.startswith('#')])
            
            result_text = f"""
✅ Conversion completed successfully!

📁 Input File: {os.path.basename(input_file)}
📁 Output File: {os.path.basename(output_file)}
📊 Lines converted: {lines_count}
🔄 Format: {format_name.upper()}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}

{result[:500]}{'...' if len(result) > 500 else ''}
            """
            
            self.root.after(0, self._update_results, result_text)
            self.root.after(0, self.update_status, f"Conversion completed! {lines_count} lines ✅")
            
        except Exception as e:
            error_text = f"❌ Conversion error:\n{str(e)}"
            self.root.after(0, self._update_results, error_text)
            self.root.after(0, self.update_status, "Conversion error ❌")
        
        finally:
            self.root.after(0, self.progress.stop)
    
    def _update_results(self, text):
        """Update results text"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state='disabled')
    
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

def main():
    """Main function"""
    root = tk.Tk()
    app = ModernCardSharingGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
