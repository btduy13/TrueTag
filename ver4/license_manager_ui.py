"""
License Manager UI for TRUETAG v4.0
Giao diện quản lý và tạo license
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import os
import json
from datetime import datetime
from license_generator import LicenseGenerator
from license_server import LicenseServer

class LicenseManagerUI:
    """Giao diện quản lý license"""
    
    def __init__(self, parent=None, data_dir=None):
        self.parent = parent
        self.data_dir = data_dir or os.path.dirname(os.path.abspath(__file__))
        
        # Initialize license generator and server
        self.generator = LicenseGenerator(self.data_dir)
        self.server = LicenseServer(self.data_dir)
        
        # Create main window
        if parent:
            self.window = tb.Toplevel(parent)
        else:
            self.window = tb.Window(themename="united")
        
        self.window.title("TRUETAG License Manager v1.0")
        self.window.geometry("900x700+200+100")
        self.window.resizable(True, True)
        
        # Set icon if available
        icon_path = os.path.join(self.data_dir, 'logo.ico')
        if os.path.exists(icon_path):
            try:
                self.window.iconbitmap(icon_path)
            except:
                pass
        
        # Colors and fonts
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'light': '#F8F9FA',
            'dark': '#343A40',
            'muted': '#6C757D'
        }
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_subtitle = ("Segoe UI", 12, "normal")
        self.font_label = ("Segoe UI", 11, "bold")
        self.font_input = ("Segoe UI", 10, "normal")
        
        # Create UI
        self.create_ui()
        self.load_licenses()
        
        # Make window modal if parent exists
        if parent:
            self.window.transient(parent)
            self.window.grab_set()
    
    def create_ui(self):
        """Tạo giao diện chính"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="TRUETAG License Manager", 
                               font=self.font_title, foreground=self.colors['primary'])
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_create_tab(notebook)
        self.create_manage_tab(notebook)
        self.create_server_tab(notebook)
        self.create_statistics_tab(notebook)
    
    def create_create_tab(self, notebook):
        """Tạo tab tạo license"""
        create_frame = ttk.Frame(notebook, padding=20)
        notebook.add(create_frame, text="Tạo License")
        
        # License type selection
        type_frame = ttk.LabelFrame(create_frame, text="Loại License", padding=15)
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(type_frame, text="License Type:", font=self.font_label).pack(anchor='w')
        
        self.license_type_var = tk.StringVar()
        license_types = self.generator.get_license_types()
        type_combo = ttk.Combobox(type_frame, textvariable=self.license_type_var, 
                                 values=list(license_types.keys()), state="readonly", 
                                 width=30, font=self.font_input)
        type_combo.pack(fill=tk.X, pady=(5, 0))
        type_combo.set("basic")  # Default selection
        
        # License type info
        self.type_info_label = ttk.Label(type_frame, text="", font=self.font_subtitle, 
                                        foreground=self.colors['muted'])
        self.type_info_label.pack(anchor='w', pady=(5, 0))
        
        # Update info when type changes
        type_combo.bind("<<ComboboxSelected>>", self.on_type_change)
        self.on_type_change()  # Initial update
        
        # Customer information
        customer_frame = ttk.LabelFrame(create_frame, text="Thông Tin Khách Hàng", padding=15)
        customer_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Customer name
        ttk.Label(customer_frame, text="Tên Khách Hàng:", font=self.font_label).pack(anchor='w')
        self.customer_name_var = tk.StringVar()
        customer_entry = ttk.Entry(customer_frame, textvariable=self.customer_name_var, 
                                  width=50, font=self.font_input)
        customer_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Customer email
        ttk.Label(customer_frame, text="Email:", font=self.font_label).pack(anchor='w')
        self.customer_email_var = tk.StringVar()
        email_entry = ttk.Entry(customer_frame, textvariable=self.customer_email_var, 
                               width=50, font=self.font_input)
        email_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Custom duration
        duration_frame = ttk.LabelFrame(create_frame, text="Thời Gian (Tùy Chọn)", padding=15)
        duration_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.custom_duration_var = tk.BooleanVar()
        duration_check = ttk.Checkbutton(duration_frame, text="Sử dụng thời gian tùy chỉnh", 
                                        variable=self.custom_duration_var, 
                                        command=self.toggle_custom_duration)
        duration_check.pack(anchor='w')
        
        self.duration_entry = ttk.Entry(duration_frame, width=10, font=self.font_input, state='disabled')
        self.duration_entry.pack(anchor='w', pady=(5, 0))
        ttk.Label(duration_frame, text="ngày", font=self.font_input).pack(anchor='w', pady=(5, 0))
        
        # Notes
        notes_frame = ttk.LabelFrame(create_frame, text="Ghi Chú", padding=15)
        notes_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.notes_text = tk.Text(notes_frame, height=4, width=70, font=self.font_input)
        self.notes_text.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(create_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Tạo License", command=self.create_license, 
                  bootstyle=SUCCESS, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Tạo Hàng Loạt", command=self.create_bulk_licenses, 
                  bootstyle=PRIMARY, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Xóa Form", command=self.clear_form, 
                  bootstyle=SECONDARY, width=15).pack(side=tk.LEFT)
        
        # Result area
        result_frame = ttk.LabelFrame(create_frame, text="Kết Quả", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
            
        self.result_text = tk.Text(result_frame, height=8, font=self.font_input)
        result_text_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_text_scroll.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_manage_tab(self, notebook):
        """Tạo tab quản lý license"""
        manage_frame = ttk.Frame(notebook, padding=20)
        notebook.add(manage_frame, text="Quản Lý License")
        
        # Filters
        filter_frame = ttk.LabelFrame(manage_frame, text="Bộ Lọc", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        filter_inner = ttk.Frame(filter_frame)
        filter_inner.pack(fill=tk.X)
        
        # License type filter
        ttk.Label(filter_inner, text="Loại:", font=self.font_label).grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.filter_type_var = tk.StringVar()
        filter_type_combo = ttk.Combobox(filter_inner, textvariable=self.filter_type_var, 
                                        values=["All"] + list(self.generator.get_license_types().keys()), 
                                        state="readonly", width=15)
        filter_type_combo.set("All")
        filter_type_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Status filter
        ttk.Label(filter_inner, text="Trạng Thái:", font=self.font_label).grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.filter_status_var = tk.StringVar()
        filter_status_combo = ttk.Combobox(filter_inner, textvariable=self.filter_status_var, 
                                          values=["All", "active", "inactive", "expired", "revoked"], 
                                          state="readonly", width=15)
        filter_status_combo.set("All")
        filter_status_combo.grid(row=0, column=3, padx=(0, 20))
        
        # Filter button
        ttk.Button(filter_inner, text="Áp Dụng", command=self.apply_filters, 
                  bootstyle=PRIMARY).grid(row=0, column=4, padx=(10, 0))
        
        # License list
        list_frame = ttk.LabelFrame(manage_frame, text="Danh Sách License", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview for license list
        columns = ("License Key", "Type", "Status", "Created", "Expires", "Uses", "Customer")
        self.license_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        for col in columns:
            self.license_tree.heading(col, text=col)
            if col == "License Key":
                self.license_tree.column(col, width=200)
            elif col in ["Created", "Expires"]:
                self.license_tree.column(col, width=120)
            elif col in ["Type", "Status", "Uses"]:
                self.license_tree.column(col, width=100)
            else:
                self.license_tree.column(col, width=150)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.license_tree.yview)
        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.license_tree.xview)
        self.license_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Pack treeview and scrollbars
        self.license_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # License actions
        action_frame = ttk.Frame(manage_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="Xem Chi Tiết", command=self.view_license_details, 
                  bootstyle=INFO, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Thu Hồi License", command=self.revoke_license, 
                  bootstyle=DANGER, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Khôi Phục License", command=self.unrevoke_license, 
                  bootstyle=SUCCESS, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Thay Đổi Trạng Thái", command=self.change_license_status, 
                  bootstyle=WARNING, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Xuất License", command=self.export_licenses, 
                  bootstyle=SECONDARY, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Nhập License", command=self.import_licenses, 
                  bootstyle=SECONDARY, width=15).pack(side=tk.LEFT)
    
    def create_server_tab(self, notebook):
        """Tạo tab server testing"""
        server_frame = ttk.Frame(notebook, padding=20)
        notebook.add(server_frame, text="Server Testing")
        
        # Server status
        status_frame = ttk.LabelFrame(server_frame, text="Trạng Thái Server", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.server_status_text = tk.Text(status_frame, height=6, font=self.font_input)
        status_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.server_status_text.yview)
        self.server_status_text.configure(yscrollcommand=status_scroll.set)
        
        self.server_status_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Test license validation
        test_frame = ttk.LabelFrame(server_frame, text="Test License Validation", padding=15)
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(test_frame, text="License Key:", font=self.font_label).pack(anchor='w')
        self.test_license_var = tk.StringVar()
        test_license_entry = ttk.Entry(test_frame, textvariable=self.test_license_var, 
                                      width=50, font=self.font_input)
        test_license_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(test_frame, text="Machine ID:", font=self.font_label).pack(anchor='w')
        self.test_machine_var = tk.StringVar()
        test_machine_entry = ttk.Entry(test_frame, textvariable=self.test_machine_var, 
                                      width=50, font=self.font_input)
        test_machine_entry.pack(fill=tk.X, pady=(5, 15))
        
        button_frame = ttk.Frame(test_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Test Validate", command=self.test_validate, 
                  bootstyle=INFO, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Test Activate", command=self.test_activate, 
                  bootstyle=SUCCESS, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Test Info", command=self.test_info, 
                  bootstyle=PRIMARY, width=15).pack(side=tk.LEFT)
        
        # Test results
        result_frame = ttk.LabelFrame(server_frame, text="Kết Quả Test", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.test_result_text = tk.Text(result_frame, height=8, font=self.font_input)
        test_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.test_result_text.yview)
        self.test_result_text.configure(yscrollcommand=test_scroll.set)
        
        self.test_result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        test_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load server status
        self.load_server_status()
    
    def create_statistics_tab(self, notebook):
        """Tạo tab thống kê"""
        stats_frame = ttk.Frame(notebook, padding=20)
        notebook.add(stats_frame, text="Thống Kê")
        
        # Statistics display
        self.stats_text = tk.Text(stats_frame, font=self.font_input, wrap=tk.WORD)
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load statistics
        self.load_statistics()
    
    def on_type_change(self, event=None):
        """Cập nhật thông tin khi thay đổi loại license"""
        try:
            license_type = self.license_type_var.get()
            if license_type:
                type_info = self.generator.get_license_types()[license_type]
                info_text = f"{type_info['description']} - {type_info['duration_days']} days"
                features_text = ", ".join(type_info['features'])
                self.type_info_label.config(text=f"{info_text}\nFeatures: {features_text}")
        except:
            pass
    
    def toggle_custom_duration(self):
        """Toggle custom duration entry"""
        if self.custom_duration_var.get():
            self.duration_entry.config(state='normal')
        else:
            self.duration_entry.config(state='disabled')
    
    def create_license(self):
        """Tạo license mới"""
        try:
            # Get form data
            license_type = self.license_type_var.get()
            customer_name = self.customer_name_var.get().strip()
            customer_email = self.customer_email_var.get().strip()
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            # Validate
            if not license_type:
                messagebox.showerror("Lỗi", "Vui lòng chọn loại license")
                return
            
            # Prepare customer info
            customer_info = {}
            if customer_name:
                customer_info["name"] = customer_name
            if customer_email:
                customer_info["email"] = customer_email
            
            # Get custom duration if enabled
            custom_duration = None
            if self.custom_duration_var.get():
                try:
                    custom_duration = int(self.duration_entry.get())
                    if custom_duration <= 0:
                        raise ValueError()
                except:
                    messagebox.showerror("Lỗi", "Thời gian tùy chỉnh phải là số nguyên dương")
                    return
            
            # Create license
            success, message, license_data = self.generator.create_license(
                license_type, customer_info, custom_duration, notes
            )
            
            if success:
                # Display result
                result_text = f"✅ License tạo thành công!\n\n"
                result_text += f"License Key: {license_data['license_key']}\n"
                result_text += f"Loại: {license_data['license_type']}\n"
                result_text += f"Thời gian: {license_data['duration_days']} ngày\n"
                result_text += f"Ngày hết hạn: {license_data['expiry_date'][:10]}\n"
                result_text += f"Tính năng: {', '.join(license_data['features'])}\n"
                if customer_name:
                    result_text += f"Khách hàng: {customer_name}\n"
                if notes:
                    result_text += f"Ghi chú: {notes}\n"
                
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", result_text)
                
                # Refresh license list
                self.load_licenses()
                
                messagebox.showinfo("Thành Công", "License đã được tạo thành công!")
            else:
                messagebox.showerror("Lỗi", f"Không thể tạo license: {message}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo license: {e}")
    
    def create_bulk_licenses(self):
        """Tạo nhiều license cùng lúc"""
        try:
            # Get count
            count = simpledialog.askinteger("Tạo Hàng Loạt", "Số lượng license cần tạo:", 
                                             minvalue=1, maxvalue=100)
            if not count:
                return
            
            # Get form data
            license_type = self.license_type_var.get()
            customer_name = self.customer_name_var.get().strip()
            customer_email = self.customer_email_var.get().strip()
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            # Validate
            if not license_type:
                messagebox.showerror("Lỗi", "Vui lòng chọn loại license")
                return
            
            # Prepare customer info
            customer_info = {}
            if customer_name:
                customer_info["name"] = customer_name
            if customer_email:
                customer_info["email"] = customer_email
            
            # Create licenses
            created_licenses = self.generator.create_bulk_licenses(
                license_type, count, customer_info, notes
            )
            
            if created_licenses:
                result_text = f"✅ Đã tạo {len(created_licenses)} license thành công!\n\n"
                for i, license_data in enumerate(created_licenses, 1):
                    result_text += f"{i}. {license_data['license_key']}\n"
                
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", result_text)
                
                # Refresh license list
                self.load_licenses()
                
                messagebox.showinfo("Thành Công", f"Đã tạo {len(created_licenses)} license thành công!")
            else:
                messagebox.showerror("Lỗi", "Không thể tạo license nào")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo license hàng loạt: {e}")
    
    def clear_form(self):
        """Xóa form"""
        self.customer_name_var.set("")
        self.customer_email_var.set("")
        self.notes_text.delete("1.0", tk.END)
        self.custom_duration_var.set(False)
        self.duration_entry.config(state='disabled')
        self.result_text.delete("1.0", tk.END)
    
    def load_licenses(self):
        """Load danh sách license"""
        try:
            # Clear existing items
            for item in self.license_tree.get_children():
                self.license_tree.delete(item)
            
            # Get filters
            filter_type = self.filter_type_var.get()
            filter_status = self.filter_status_var.get()
            
            # Apply filters
            license_type = None if filter_type == "All" else filter_type
            status = None if filter_status == "All" else filter_status
            
            # Get licenses
            licenses = self.generator.list_licenses(license_type, status)
            
            # Add to treeview
            for license_data in licenses:
                # Format dates
                created_date = license_data['created_date'][:10] if license_data['created_date'] else ""
                expiry_date = license_data['expiry_date'][:10] if license_data['expiry_date'] else ""
                
                # Format uses
                uses = f"{license_data['current_uses']}/{license_data['max_uses']}"
                
                # Get customer name
                customer_info = license_data.get('customer_info', {})
                customer_name = customer_info.get('name', '')
                
                # Insert row
                self.license_tree.insert("", "end", values=(
                    license_data['license_key'],
                    license_data['license_type'],
                    license_data['status'],
                    created_date,
                    expiry_date,
                    uses,
                    customer_name
                ))
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi load license: {e}")
    
    def apply_filters(self):
        """Áp dụng bộ lọc"""
        self.load_licenses()
    
    def view_license_details(self):
        """Xem chi tiết license"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh Báo", "Vui lòng chọn license để xem chi tiết")
                return
            
            item = self.license_tree.item(selection[0])
            license_key = item['values'][0]
            
            # Get detailed info
            license_info = self.generator.get_license_info(license_key)
            
            # Create details window
            details_window = tb.Toplevel(self.window)
            details_window.title(f"Chi Tiết License: {license_key}")
            details_window.geometry("600x500+300+200")
            details_window.resizable(True, True)
            
            # Make modal
            details_window.transient(self.window)
            details_window.grab_set()
            
            # Details text
            details_text = tk.Text(details_window, font=self.font_input, wrap=tk.WORD)
            details_scroll = ttk.Scrollbar(details_window, orient=tk.VERTICAL, command=details_text.yview)
            details_text.configure(yscrollcommand=details_scroll.set)
            
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
            details_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
            
            # Format details
            details = f"License Key: {license_info['license_key']}\n"
            details += f"Type: {license_info['license_type']}\n"
            details += f"Status: {license_info['status']}\n"
            details += f"Created: {license_info['created_date'][:19]}\n"
            details += f"Expires: {license_info['expiry_date'][:19]}\n"
            details += f"Duration: {license_info['duration_days']} days\n"
            details += f"Uses: {license_info['current_uses']}/{license_info['max_uses']}\n\n"
            
            details += "Features:\n"
            for feature in license_info['features']:
                details += f"  • {feature}\n"
            
            if license_info.get('customer_info'):
                details += "\nCustomer Information:\n"
                for key, value in license_info['customer_info'].items():
                    details += f"  {key}: {value}\n"
            
            if license_info.get('notes'):
                details += f"\nNotes:\n{license_info['notes']}\n"
            
            if license_info.get('activations'):
                details += "\nActivations:\n"
                for i, activation in enumerate(license_info['activations'], 1):
                    details += f"  {i}. Machine: {activation['machine_id']}\n"
                    details += f"     Date: {activation['activation_date'][:19]}\n"
                    if activation.get('customer_name'):
                        details += f"     Customer: {activation['customer_name']}\n"
                    details += "\n"
            
            details_text.insert("1.0", details)
            details_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xem chi tiết: {e}")
    
    def revoke_license(self):
        """Thu hồi license"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh Báo", "Vui lòng chọn license")
                return
            
            item = self.license_tree.item(selection[0])
            license_key = item['values'][0]
            current_status = item['values'][2]
            
            # Check if already revoked
            if current_status == "revoked":
                messagebox.showwarning("Cảnh Báo", "License đã bị thu hồi")
                return
            
            # Create revoke dialog
            revoke_window = tb.Toplevel(self.window)
            revoke_window.title("Thu Hồi License")
            revoke_window.geometry("600x500+300+200")
            revoke_window.resizable(True, True)
            # Set icon if available
            icon_path = os.path.join(self.data_dir, 'logo.ico')
            if os.path.exists(icon_path):
                try:
                    revoke_window.iconbitmap(icon_path)
                except:
                    pass
            
            # Make window modal
            revoke_window.transient(self.window)
            revoke_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(revoke_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Thu Hồi License", font=self.font_title)
            title_label.pack(pady=(0, 20))
            
            # License info
            info_frame = ttk.LabelFrame(main_frame, text="Thông Tin License", padding=15)
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(info_frame, text=f"License Key: {license_key}", font=self.font_label).pack(anchor='w')
            ttk.Label(info_frame, text=f"Trạng thái hiện tại: {current_status}", font=self.font_input).pack(anchor='w', pady=(5, 0))
            
            # Revoke form
            form_frame = ttk.LabelFrame(main_frame, text="Thông Tin Thu Hồi", padding=15)
            form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Admin name
            ttk.Label(form_frame, text="Tên Admin:", font=self.font_label).pack(anchor='w')
            admin_name_var = tk.StringVar()
            admin_entry = ttk.Entry(form_frame, textvariable=admin_name_var, font=self.font_input, width=50)
            admin_entry.pack(fill=tk.X, pady=(5, 10))
            
            # Reason
            ttk.Label(form_frame, text="Lý do thu hồi:", font=self.font_label).pack(anchor='w')
            reason_text = tk.Text(form_frame, height=6, width=70, font=self.font_input)
            reason_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(15, 0))
            
            def confirm_revoke():
                admin_name = admin_name_var.get().strip()
                reason = reason_text.get("1.0", tk.END).strip()
                
                if not admin_name:
                    messagebox.showwarning("Cảnh Báo", "Vui lòng nhập tên admin")
                    return
                
                if not reason:
                    messagebox.showwarning("Cảnh Báo", "Vui lòng nhập lý do thu hồi")
                    return
                
                # Confirm revoke
                result = messagebox.askyesno(
                    "Xác Nhận Thu Hồi",
                    f"Bạn có chắc chắn muốn thu hồi license:\n\n{license_key}\n\nLý do: {reason}\n\nHành động này không thể hoàn tác!"
                )
                
                if result:
                    success, message = self.generator.revoke_license(license_key, reason, admin_name)
                    if success:
                        messagebox.showinfo("Thành Công", message)
                        revoke_window.destroy()
                        self.load_licenses()  # Refresh list
                    else:
                        messagebox.showerror("Lỗi", message)
            
            # Create buttons with proper styling
            revoke_btn = ttk.Button(button_frame, text="Thu Hồi License", command=confirm_revoke, 
                                  bootstyle=DANGER, width=20)
            revoke_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            cancel_btn = ttk.Button(button_frame, text="Hủy", command=revoke_window.destroy, 
                                  bootstyle=SECONDARY, width=20)
            cancel_btn.pack(side=tk.LEFT)
            
            # Ensure buttons are visible
            button_frame.update()
            print(f"Button frame size: {button_frame.winfo_reqwidth()}x{button_frame.winfo_reqheight()}")
            
            # Focus on admin entry
            admin_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thu hồi license: {e}")
    
    def unrevoke_license(self):
        """Khôi phục license đã bị thu hồi"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh Báo", "Vui lòng chọn license")
                return
            
            item = self.license_tree.item(selection[0])
            license_key = item['values'][0]
            current_status = item['values'][2]
            
            # Check if not revoked
            if current_status != "revoked":
                messagebox.showwarning("Cảnh Báo", "License chưa bị thu hồi")
                return
            
            # Create unrevoke dialog
            unrevoke_window = tb.Toplevel(self.window)
            unrevoke_window.title("Khôi Phục License")
            unrevoke_window.geometry("600x500+300+200")
            unrevoke_window.resizable(True, True)
            # Set icon if available
            icon_path = os.path.join(self.data_dir, 'logo.ico')
            if os.path.exists(icon_path):
                try:
                    unrevoke_window.iconbitmap(icon_path)
                except:
                    pass
            
            # Make window modal
            unrevoke_window.transient(self.window)
            unrevoke_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(unrevoke_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Khôi Phục License", font=self.font_title)
            title_label.pack(pady=(0, 20))
            
            # License info
            info_frame = ttk.LabelFrame(main_frame, text="Thông Tin License", padding=15)
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(info_frame, text=f"License Key: {license_key}", font=self.font_label).pack(anchor='w')
            ttk.Label(info_frame, text=f"Trạng thái hiện tại: {current_status}", font=self.font_input).pack(anchor='w', pady=(5, 0))
            
            # Show revoke history
            try:
                license_info = self.generator.get_license_info(license_key)
                revoke_info = license_info.get("revoke_info", {})
                if revoke_info:
                    ttk.Label(info_frame, text=f"Thu hồi bởi: {revoke_info.get('admin_name', 'N/A')}", font=self.font_input).pack(anchor='w', pady=(5, 0))
                    ttk.Label(info_frame, text=f"Ngày thu hồi: {revoke_info.get('revoked_date', 'N/A')[:10]}", font=self.font_input).pack(anchor='w', pady=(5, 0))
                    ttk.Label(info_frame, text=f"Lý do: {revoke_info.get('reason', 'N/A')}", font=self.font_input).pack(anchor='w', pady=(5, 0))
            except:
                pass
            
            # Unrevoke form
            form_frame = ttk.LabelFrame(main_frame, text="Thông Tin Khôi Phục", padding=15)
            form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Admin name
            ttk.Label(form_frame, text="Tên Admin:", font=self.font_label).pack(anchor='w')
            admin_name_var = tk.StringVar()
            admin_entry = ttk.Entry(form_frame, textvariable=admin_name_var, font=self.font_input, width=50)
            admin_entry.pack(fill=tk.X, pady=(5, 10))
            
            # Reason
            ttk.Label(form_frame, text="Lý do khôi phục:", font=self.font_label).pack(anchor='w')
            reason_text = tk.Text(form_frame, height=6, width=70, font=self.font_input)
            reason_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(15, 0))
            
            def confirm_unrevoke():
                admin_name = admin_name_var.get().strip()
                reason = reason_text.get("1.0", tk.END).strip()
                
                if not admin_name:
                    messagebox.showwarning("Cảnh Báo", "Vui lòng nhập tên admin")
                    return
                
                if not reason:
                    messagebox.showwarning("Cảnh Báo", "Vui lòng nhập lý do khôi phục")
                    return
                
                # Confirm unrevoke
                result = messagebox.askyesno(
                    "Xác Nhận Khôi Phục",
                    f"Bạn có chắc chắn muốn khôi phục license:\n\n{license_key}\n\nLý do: {reason}"
                )
                
                if result:
                    success, message = self.generator.unrevoke_license(license_key, admin_name, reason)
                    if success:
                        messagebox.showinfo("Thành Công", message)
                        unrevoke_window.destroy()
                        self.load_licenses()  # Refresh list
                    else:
                        messagebox.showerror("Lỗi", message)
            
            # Create buttons with proper styling
            unrevoke_btn = ttk.Button(button_frame, text="Khôi Phục License", command=confirm_unrevoke, 
                                    bootstyle=SUCCESS, width=20)
            unrevoke_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            cancel_btn = ttk.Button(button_frame, text="Hủy", command=unrevoke_window.destroy, 
                                  bootstyle=SECONDARY, width=20)
            cancel_btn.pack(side=tk.LEFT)
            
            # Ensure buttons are visible
            button_frame.update()
            print(f"Unrevoke button frame size: {button_frame.winfo_reqwidth()}x{button_frame.winfo_reqheight()}")
            
            # Focus on admin entry
            admin_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi khôi phục license: {e}")

    def change_license_status(self):
        """Thay đổi trạng thái license"""
        try:
            selection = self.license_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh Báo", "Vui lòng chọn license")
                return
            
            item = self.license_tree.item(selection[0])
            license_key = item['values'][0]
            current_status = item['values'][2]
            
            # Ask for new status
            new_status = simpledialog.askstring(
                "Thay Đổi Trạng Thái", 
                f"License: {license_key}\nTrạng thái hiện tại: {current_status}\n\nTrạng thái mới:",
                initialvalue=current_status
            )
            
            if new_status and new_status != current_status:
                success, message = self.generator.update_license_status(license_key, new_status)
                if success:
                    messagebox.showinfo("Thành Công", message)
                    self.load_licenses()  # Refresh list
                else:
                    messagebox.showerror("Lỗi", message)
                    
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thay đổi trạng thái: {e}")
    
    def export_licenses(self):
        """Xuất license"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Xuất License",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if file_path:
                exported_path = self.generator.export_licenses(file_path)
                messagebox.showinfo("Thành Công", f"License đã được xuất: {exported_path}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất license: {e}")
    
    def import_licenses(self):
        """Nhập license"""
        try:
            file_path = filedialog.askopenfilename(
                title="Nhập License",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if file_path:
                success, message = self.generator.import_licenses(file_path)
                if success:
                    messagebox.showinfo("Thành Công", message)
                    self.load_licenses()  # Refresh list
                else:
                    messagebox.showerror("Lỗi", message)
                    
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi nhập license: {e}")
    
    def load_server_status(self):
        """Load trạng thái server"""
        try:
            status = self.server.get_server_status()
            
            status_text = f"Server: {status['server_name']}\n"
            status_text += f"Version: {status['version']}\n"
            status_text += f"Status: {status['status']}\n"
            status_text += f"Uptime: {status['uptime']}\n\n"
            
            stats = status['statistics']
            status_text += f"Total Licenses: {stats['total_licenses']}\n"
            status_text += f"Active Licenses: {stats['active_licenses']}\n"
            status_text += f"Expired Licenses: {stats['expired_licenses']}\n"
            status_text += f"Total Generated: {stats['total_generated']}\n"
            status_text += f"Total Activated: {stats['total_activated']}\n"
            
            if stats.get('by_type'):
                status_text += "\nBy Type:\n"
                for license_type, count in stats['by_type'].items():
                    status_text += f"  {license_type}: {count}\n"
            
            self.server_status_text.delete("1.0", tk.END)
            self.server_status_text.insert("1.0", status_text)
            
        except Exception as e:
            self.server_status_text.delete("1.0", tk.END)
            self.server_status_text.insert("1.0", f"Lỗi khi load server status: {e}")
    
    def test_validate(self):
        """Test license validation"""
        try:
            license_key = self.test_license_var.get().strip()
            machine_id = self.test_machine_var.get().strip()
            
            if not license_key:
                messagebox.showwarning("Cảnh Báo", "Vui lòng nhập license key")
                return
            
            # Simulate request
            response = self.server.validate_license_request(license_key, machine_id)
            
            # Display result
            result_text = "=== TEST VALIDATE ===\n\n"
            result_text += f"License Key: {license_key}\n"
            result_text += f"Machine ID: {machine_id or 'None'}\n\n"
            result_text += f"Response:\n{json.dumps(response, indent=2, ensure_ascii=False)}\n\n"
            
            self.test_result_text.insert(tk.END, result_text)
            self.test_result_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi test validate: {e}")
    
    def test_activate(self):
        """Test license activation"""
        try:
            license_key = self.test_license_var.get().strip()
            machine_id = self.test_machine_var.get().strip()
            
            if not license_key or not machine_id:
                messagebox.showwarning("Cảnh Báo", "Vui lòng nhập license key và machine ID")
                return
            
            # Simulate request
            response = self.server.activate_license_request(license_key, machine_id)
            
            # Display result
            result_text = "=== TEST ACTIVATE ===\n\n"
            result_text += f"License Key: {license_key}\n"
            result_text += f"Machine ID: {machine_id}\n\n"
            result_text += f"Response:\n{json.dumps(response, indent=2, ensure_ascii=False)}\n\n"
            
            self.test_result_text.insert(tk.END, result_text)
            self.test_result_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi test activate: {e}")
    
    def test_info(self):
        """Test license info"""
        try:
            license_key = self.test_license_var.get().strip()
            
            if not license_key:
                messagebox.showwarning("Cảnh Báo", "Vui lòng nhập license key")
                return
            
            # Simulate request
            response = self.server.get_license_info_request(license_key)
            
            # Display result
            result_text = "=== TEST INFO ===\n\n"
            result_text += f"License Key: {license_key}\n\n"
            result_text += f"Response:\n{json.dumps(response, indent=2, ensure_ascii=False)}\n\n"
            
            self.test_result_text.insert(tk.END, result_text)
            self.test_result_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi test info: {e}")
    
    def load_statistics(self):
        """Load thống kê"""
        try:
            stats = self.generator.get_statistics()
            
            stats_text = f"=== THỐNG KÊ LICENSE ===\n\n"
            stats_text += f"Tổng số license: {stats['total_licenses']}\n"
            stats_text += f"License đang hoạt động: {stats['active_licenses']}\n"
            stats_text += f"License đã hết hạn: {stats['expired_licenses']}\n"
            stats_text += f"Tổng đã tạo: {stats['total_generated']}\n"
            stats_text += f"Tổng đã kích hoạt: {stats['total_activated']}\n"
            stats_text += f"Cập nhật lần cuối: {stats['last_updated'][:19]}\n\n"
            
            if stats.get('by_type'):
                stats_text += "Phân loại theo type:\n"
                for license_type, count in stats['by_type'].items():
                    stats_text += f"  {license_type}: {count}\n"
            
            # Get license list for detailed stats
            licenses = self.generator.list_licenses()
            if licenses:
                stats_text += f"\nChi tiết license:\n"
                stats_text += f"  - License mới nhất: {licenses[0]['license_key']}\n"
                stats_text += f"  - License cũ nhất: {licenses[-1]['license_key']}\n"
                
                # Count by status
                status_count = {}
                for license_data in licenses:
                    status = license_data['status']
                    status_count[status] = status_count.get(status, 0) + 1
                
                stats_text += f"\nPhân loại theo trạng thái:\n"
                for status, count in status_count.items():
                    stats_text += f"  {status}: {count}\n"
            
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_text)
            
        except Exception as e:
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", f"Lỗi khi load thống kê: {e}")
    
    def run(self):
        """Chạy giao diện"""
        self.window.mainloop()

if __name__ == "__main__":
    app = LicenseManagerUI()
    app.run()
