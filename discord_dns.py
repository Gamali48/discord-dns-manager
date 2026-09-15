import ctypes
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser


def is_admin():
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False


def run_as_admin():
  if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()


def get_active_interface_name():
  try:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            (
                "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select"
                " -ExpandProperty Name"
            ),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    interfaces = result.stdout.strip().split("\n")
    if interfaces and interfaces[0]:
      return interfaces[0].strip()
  except:
    pass
  return None


class DNSApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Discord & DNS Yönetici")
    self.root.geometry("380x320")
    self.root.config(bg="#1e1e1e")
    self.root.resizable(False, False)

    # Başlık
    title_label = tk.Label(
        root,
        text="Özel Bağlantı Paneli",
        font=("Segoe UI", 14, "bold"),
        fg="#ffffff",
        bg="#1e1e1e",
    )
    title_label.pack(pady=15)

    # Durum Göstergesi
    self.status_label = tk.Label(
        root,
        text="Durum: Bekleniyor...",
        font=("Segoe UI", 10),
        fg="#aaaaaa",
        bg="#1e1e1e",
    )
    self.status_label.pack(pady=5)

    # DNS Aç Butonu
    self.btn_on = tk.Button(
        root,
        text="🟢 DNS Aktif Et (Cloudflare)",
        font=("Segoe UI", 10, "bold"),
        bg="#2d7d46",
        fg="white",
        activebackground="#389e5d",
        activeforeground="white",
        relief="flat",
        width=28,
        height=2,
        command=lambda: threading.Thread(target=self.enable_dns).start(),
    )
    self.btn_on.pack(pady=8)

    # DNS Kapat Butonu
    self.btn_off = tk.Button(
        root,
        text="🔴 DNS Kapat (Varsayılan / Otomatik)",
        font=("Segoe UI", 10, "bold"),
        bg="#a83232",
        fg="white",
        activebackground="#c73e3e",
        activeforeground="white",
        relief="flat",
        width=28,
        height=2,
        command=lambda: threading.Thread(target=self.disable_dns).start(),
    )
    self.btn_off.pack(pady=8)

    # Discord İndir Butonu
    self.btn_discord = tk.Button(
        root,
        text="📥 Discord İndirme Sayfasını Aç",
        font=("Segoe UI", 10, "bold"),
        bg="#5865F2",
        fg="white",
        activebackground="#7289da",
        activeforeground="white",
        relief="flat",
        width=28,
        height=2,
        command=self.open_discord_site,
    )
    self.btn_discord.pack(pady=8)

  def enable_dns(self):
    adapter = get_active_interface_name()
    if not adapter:
      messagebox.showerror("Hata", "Aktif internet adaptörü bulunamadı!")
      return

    self.status_label.config(text="Durum: DNS güncelleniyor...", fg="#f1c40f")
    cmd_primary = f'netsh interface ip set dns name="{adapter}" static 1.1.1.1'
    cmd_secondary = (
        f'netsh interface ip add dns name="{adapter}" 1.0.0.1 index=2'
    )
    subprocess.run(cmd_primary, shell=True)
    subprocess.run(cmd_secondary, shell=True)

    # DNS önbelleğini temizle
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)

    self.status_label.config(
        text="Durum: DNS Aktif (Cloudflare)", fg="#2ecc71"
    )
    messagebox.showinfo(
        "Başarılı", "DNS ayarları başarıyla Cloudflare olarak değiştirildi!"
    )

  def disable_dns(self):
    adapter = get_active_interface_name()
    if not adapter:
      messagebox.showerror("Hata", "Aktif internet adaptörü bulunamadı!")
      return

    self.status_label.config(text="Durum: DNS sıfırlanıyor...", fg="#f1c40f")
    cmd = f'netsh interface ip set dns name="{adapter}" source=dhcp'
    subprocess.run(cmd, shell=True)
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)

    self.status_label.config(
        text="Durum: DNS Varsayılana Döndü", fg="#e74c3c"
    )
    messagebox.showinfo(
        "Başarılı", "DNS ayarları otomatik (DHCP) moda döndürüldü."
    )

  def open_discord_site(self):
    # Tarayıcıda doğrudan Discord indirme sayfasını açar (DNS aktif olduğu için engelsiz açılır)
    webbrowser.open("https://discord.com/download")
    self.status_label.config(text="Durum: Tarayıcı açıldı", fg="#3498db")


if __name__ == "__main__":
  run_as_admin()
  root = tk.Tk()
  app = DNSApp(root)
  root.mainloop()