import tkinter as tk
from tkinter import messagebox
import sqlite3

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True

    def starts_with(self, prefix):
        current = self.root
        for char in prefix:
            if char not in current.children:
                return []
            current = current.children[char]
        return self._elements_with_prefix(current, prefix)

    def _elements_with_prefix(self, node, prefix):
        result = []
        if node.is_end_of_word:
            result.append(prefix)
        for char, child in node.children.items():
            result.extend(self._elements_with_prefix(child, prefix + char))
        return result

class PhoneDirectory:
    def __init__(self):
        self.contacts = {}
        self.trie = Trie()
        self._load_contacts()

    def _load_contacts(self):
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS contacts (name TEXT, phone TEXT)")
        cursor.execute("SELECT name, phone FROM contacts")
        rows = cursor.fetchall()
        for name, phone in rows:
            self.contacts[name] = phone
            self.trie.insert(name)
        conn.close()

    def add_contact(self, name, phone_number):
        if name not in self.contacts:
            self.contacts[name] = phone_number
            self.trie.insert(name)
            conn = sqlite3.connect("contacts.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone_number))
            conn.commit()
            conn.close()
            messagebox.showinfo("Info", f"Contact '{name}' added.")
        else:
            messagebox.showinfo("Error", f"Contact '{name}' already exists.")

    def delete_contact(self, name):
        if name in self.contacts:
            del self.contacts[name]
            conn = sqlite3.connect("contacts.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE name=?", (name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Info", f"Contact '{name}' deleted.")
        else:
            messagebox.showinfo("Error", f"Contact '{name}' does not exist.")

    def search_contact(self, name):
        return self.contacts.get(name, None)

    def suggest_contacts(self, prefix):
        return self.trie.starts_with(prefix)

class PhoneDirectoryApp:
    def __init__(self, root):
        self.directory = PhoneDirectory()
        self.root = root
        self.root.title("Phone Directory")
        self.root.configure(bg="#f0f0f0")
        self.create_widgets()

    def create_widgets(self):
        self.style_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=10)
        self.style_frame.pack(pady=20)

        self.title_label = tk.Label(self.style_frame, text="Phone Directory", font=("Helvetica", 18, "bold"), bg="#e0e0e0")
        self.title_label.pack(pady=10)

        self.add_contact_frame = tk.LabelFrame(self.style_frame, text="Add Contact", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        self.add_contact_frame.pack(pady=10, fill="x")

        tk.Label(self.add_contact_frame, text="Name:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.add_contact_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.add_contact_frame, text="Phone Number:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.phone_entry = tk.Entry(self.add_contact_frame)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        self.add_button = tk.Button(self.add_contact_frame, text="Add Contact", command=self.add_contact, bg="#c0c0c0")
        self.add_button.grid(row=2, columnspan=2, pady=5)

        self.delete_contact_frame = tk.LabelFrame(self.style_frame, text="Delete Contact", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        self.delete_contact_frame.pack(pady=10, fill="x")

        tk.Label(self.delete_contact_frame, text="Name:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.delete_name_entry = tk.Entry(self.delete_contact_frame)
        self.delete_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(self.delete_contact_frame, text="Delete Contact", command=self.delete_contact, bg="#c0c0c0")
        self.delete_button.grid(row=1, columnspan=2, pady=5)

        self.search_contact_frame = tk.LabelFrame(self.style_frame, text="Search Contact", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        self.search_contact_frame.pack(pady=10, fill="x")

        tk.Label(self.search_contact_frame, text="Name:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_name_entry = tk.Entry(self.search_contact_frame)
        self.search_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = tk.Button(self.search_contact_frame, text="Search Contact", command=self.search_contact, bg="#c0c0c0")
        self.search_button.grid(row=1, columnspan=2, pady=5)

        self.search_result_label = tk.Label(self.search_contact_frame, text="", bg="#f0f0f0")
        self.search_result_label.grid(row=2, columnspan=2, pady=5)

        self.suggest_contact_frame = tk.LabelFrame(self.style_frame, text="Suggest Contacts", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        self.suggest_contact_frame.pack(pady=10, fill="x")

        tk.Label(self.suggest_contact_frame, text="Prefix:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.prefix_entry = tk.Entry(self.suggest_contact_frame)
        self.prefix_entry.grid(row=0, column=1, padx=5, pady=5)

        self.suggest_button = tk.Button(self.suggest_contact_frame, text="Suggest Contacts", command=self.suggest_contacts, bg="#c0c0c0")
        self.suggest_button.grid(row=1, columnspan=2, pady=5)

        self.suggest_result_label = tk.Label(self.suggest_contact_frame, text="", bg="#f0f0f0")
        self.suggest_result_label.grid(row=2, columnspan=2, pady=5)

    def add_contact(self):
        name = self.name_entry.get()
        phone_number = self.phone_entry.get()
        if name and phone_number:
            self.directory.add_contact(name, phone_number)
        else:
            messagebox.showinfo("Error", "Please enter both name and phone number.")
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)

    def delete_contact(self):
        name = self.delete_name_entry.get()
        if name:
            self.directory.delete_contact(name)
        else:
            messagebox.showinfo("Error", "Please enter a name.")
        self.delete_name_entry.delete(0, tk.END)

    def search_contact(self):
        name = self.search_name_entry.get()
        if name:
            phone_number = self.directory.search_contact(name)
            if phone_number:
                self.search_result_label.config(text=f"Phone Number: {phone_number}")
            else:
                self.search_result_label.config(text="Contact not found.")
        else:
            messagebox.showinfo("Error", "Please enter a name.")
        self.search_name_entry.delete(0, tk.END)

    def suggest_contacts(self):
        prefix = self.prefix_entry.get()
        if prefix:
            suggestions = self.directory.suggest_contacts(prefix)
            if suggestions:
                self.suggest_result_label.config(text="Suggestions: " + ", ".join(suggestions))
            else:
                self.suggest_result_label.config(text="No suggestions found.")
        else:
            messagebox.showinfo("Error", "Please enter a prefix.")
        self.prefix_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneDirectoryApp(root)
    root.mainloop()
