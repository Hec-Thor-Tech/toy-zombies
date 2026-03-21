import tkinter as tk
from tkinter import messagebox
import os

def guardar_zombie():
    nombre = entry_nombre.get()
    parents = entry_parents.get()
    especie = entry_especie.get()
    poderes = entry_poderes.get()
    ocupacion = entry_ocupacion.get()
    imagen = entry_imagen.get()

    if not nombre or not imagen:
        messagebox.showwarning("Faltan datos", "El nombre y el archivo de imagen son obligatorios.")
        return

    if not imagen.endswith((".webp", ".png", ".jpg", ".gif")):
        imagen += ".webp"

    html_template = f"""
<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 40px;">
  
  <div style="flex: 1; min-width: 300px; background-color: rgba(30, 30, 30, 0.6); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(8px);">
    <img src="../img/{imagen}" alt="{nombre}" style="width: 100%; border-radius: 4px;">
  </div>

  <div style="flex: 1; min-width: 300px; background-color: rgba(30, 30, 30, 0.6); padding: 20px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(8px);">
    <h3 style="text-align: center; margin-top: 0; color: #ff5252; font-weight: bold; margin-bottom: 15px;">Archivo de Entidad</h3>
    
    <div style="border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; background-color: rgba(0, 0, 0, 0.4);">
      <div style="padding: 15px;">
        <p style="margin-bottom: 12px; color: #fff;"><b>Nombre:</b> {nombre}</p>
        <p style="margin-bottom: 12px; color: #fff;"><b>Padres:</b> {parents}</p>
        <p style="margin-bottom: 12px; color: #fff;"><b>Especie:</b> {especie}</p>
        <p style="margin-bottom: 12px; color: #fff;"><b>Poderes:</b> {poderes}</p>
        <p style="margin-bottom: 0; color: #fff;"><b>Ocupación:</b> {ocupacion}</p>
      </div>
    </div>
  </div>

</div>

<hr style="border-color: #444; margin: 40px 0;">
"""

    ruta_archivo = os.path.join("docs", "bestiario.md")
    
    try:
        with open(ruta_archivo, "a", encoding="utf-8") as file:
            file.write(html_template)
        messagebox.showinfo("¡Éxito!", f"¡{nombre} se ha agregado al bestiario!")
        entry_nombre.delete(0, tk.END)
        entry_parents.delete(0, tk.END)
        entry_especie.delete(0, tk.END)
        entry_poderes.delete(0, tk.END)
        entry_ocupacion.delete(0, tk.END)
        entry_imagen.delete(0, tk.END)
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar en bestiario.md\n{e}")

# --- Configuración de la Ventana (Modo Oscuro) ---
root = tk.Tk()
root.title("Terminal de Datos - Toy Zombies")
root.geometry("400x480")
root.configure(bg="#121212")

fuente_label = ("Consolas", 10, "bold")
bg_color = "#121212"
fg_color = "#ff5252"
entry_bg = "#1e1e1e"
entry_fg = "#ffffff"

tk.Label(root, text="AÑADIR NUEVA ENTIDAD", font=("Consolas", 14, "bold"), bg=bg_color, fg=fg_color).pack(pady=15)

def crear_campo(texto):
    tk.Label(root, text=texto, bg=bg_color, fg="#aaaaaa", font=fuente_label).pack(anchor="w", padx=40)
    entry = tk.Entry(root, bg=entry_bg, fg=entry_fg, insertbackground="white", width=40, relief="solid")
    entry.pack(pady=2, padx=40)
    return entry

entry_nombre = crear_campo("Nombre de la entidad:")
entry_parents = crear_campo("Padres (Parents):")
entry_especie = crear_campo("Especie:")
entry_poderes = crear_campo("Poderes / Habilidades:")
entry_ocupacion = crear_campo("Ocupación:")
entry_imagen = crear_campo("Nombre del archivo (ej: bear.webp):")

btn_guardar = tk.Button(root, text="INYECTAR EN BESTIARIO.MD", bg="#440000", fg="#ffffff", 
                        font=("Consolas", 10, "bold"), relief="flat", cursor="hand2", command=guardar_zombie)
btn_guardar.pack(pady=25, ipadx=10, ipady=5)

root.mainloop()