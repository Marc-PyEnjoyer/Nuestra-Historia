from collections import Counter
import os
import re
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Nuestros 4.5 Años Juntos ❤️", page_icon="💖", layout="centered"
)


# --- FUNCIÓN PARA PROCESAR EL CHAT ---
@st.cache_data
def cargar_y_analizar_chat(nombre_archivo):
  total_mensajes = 0
  mensajes_por_persona = Counter()
  multimedia_por_persona = Counter()
  palabras_por_persona = Counter()
  amor_por_persona = Counter()
  mensajes_por_anio = Counter()
  palabras_totales = Counter()

  palabras_amor = ["tamo", "te amo", "bb", "amor", "mor"]

  stop_words = {
      "el",
      "la",
      "los",
      "las",
      "un",
      "una",
      "y",
      "o",
      "a",
      "de",
      "en",
      "que",
      "es",
      "por",
      "con",
      "no",
      "te",
      "lo",
      "le",
      "su",
      "al",
      "como",
      "más",
      "pero",
      "sus",
      "ya",
      "este",
      "sí",
      "porque",
      "esta",
      "entre",
      "cuando",
      "muy",
      "sin",
      "sobre",
      "también",
      "me",
      "hasta",
      "hay",
      "donde",
      "desde",
      "todo",
      "nos",
      "todos",
      "uno",
      "les",
      "ni",
      "yo",
      "mi",
      "tú",
      "ti",
      "tu",
      "para",
      "media",
      "omitted",
  }

  if not os.path.exists(nombre_archivo):
    return None

  with open(nombre_archivo, "r", encoding="utf-8") as archivo:
    for linea in archivo:
      match = re.search(
          r"(\d{2}/\d{2}/\d{4}),\s\d{2}:\d{2}\s-\s([^:]+):\s(.+)", linea
      )

      if match:
        fecha = match.group(1).strip()
        remitente = match.group(2).strip()
        mensaje = match.group(3).strip()
        mensaje_lower = mensaje.lower()

        total_mensajes += 1
        mensajes_por_persona[remitente] += 1

        anio = fecha.split("/")[-1]
        mensajes_por_anio[anio] += 1

        if (
            "media omitted" in mensaje_lower
            or "multimedia omitido" in mensaje_lower
        ):
          multimedia_por_persona[remitente] += 1
        else:
          palabras = re.findall(r"\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{2,}\b", mensaje_lower)
          palabras_por_persona[remitente] += len(palabras)

          for frase in palabras_amor:
            if frase in mensaje_lower:
              amor_por_persona[remitente] += 1

          for palabra in palabras:
            if len(palabra) >= 4 and palabra not in stop_words:
              palabras_totales[palabra] += 1

  return {
      "total_mensajes": total_mensajes,
      "mensajes_por_persona": mensajes_por_persona,
      "multimedia_por_persona": multimedia_por_persona,
      "palabras_por_persona": palabras_por_persona,
      "amor_por_persona": amor_por_persona,
      "mensajes_por_anio": mensajes_por_anio,
      "palabras_totales": palabras_totales,
  }


# --- RUTA DEL ARCHIVO Y PANTALLA DE CARGA ---
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_chat = os.path.join(carpeta_actual, "chat.txt")

with st.spinner("Cargando nuestro amor, un momentito... ✨"):
  datos = cargar_y_analizar_chat(ruta_chat)

if datos is None:
  st.error(
      "❌ No se encontró el archivo 'chat.txt'. Asegúrate de que esté en la"
      " misma carpeta que app.py"
  )
else:
  # Lanza animación de globos al cargar la página
  st.balloons()

  # --- ENCABEZADO ---
  st.title("💖 Nuestra Historia en Números 💖")
  st.subheader("4.5 Años Compartiendo Momentos Juntos ✨")
  st.write("Un resumen interactivo de nuestro chat de WhatsApp.")

  st.divider()

  # --- MÉTRICAS PRINCIPALES ---
  col1, col2 = st.columns(2)
  with col1:
    st.metric(
        label="💬 Mensajes Totales", value=f"{datos['total_mensajes']:,}"
    )
  with col2:
    total_multimedia = sum(datos["multimedia_por_persona"].values())
    st.metric(label="📸 Fotos, Audios y Stickers", value=f"{total_multimedia:,}")

  st.divider()

  # --- MENSAJES POR PERSONA ---
  st.subheader("👥 Mensajes Enviados por Cada Uno")
  df_mensajes = pd.DataFrame(
      list(datos["mensajes_por_persona"].items()),
      columns=["Persona", "Mensajes"],
  )
  st.bar_chart(df_mensajes, x="Persona", y="Mensajes")

  st.divider()

  # --- MUESTRAS DE AFECTO ---
  st.subheader("❤️ Contador de Amor")
  st.caption("Veces que hemos dicho: 'tamo', 'te amo', 'bb', 'amor', 'mor'")
  df_amor = pd.DataFrame(
      list(datos["amor_por_persona"].items()), columns=["Persona", "Veces"]
  )
  st.dataframe(df_amor, use_container_width=True, hide_index=True)

  st.divider()

  # --- EVOLUCIÓN POR AÑO ---
  st.subheader("📅 Evolución de Mensajes por Año")
  df_anio = pd.DataFrame(
      sorted(datos["mensajes_por_anio"].items()), columns=["Año", "Mensajes"]
  )
  st.line_chart(df_anio, x="Año", y="Mensajes")

  st.divider()

  # --- PALABRAS MÁS REPETIDAS ---
  st.subheader("🔥 Nuestras 10 Palabras Más Usadas")
  df_palabras = pd.DataFrame(
      datos["palabras_totales"].most_common(10),
      columns=["Palabra", "Frecuencia"],
  )
  st.dataframe(df_palabras, use_container_width=True, hide_index=True)

  st.success("✨ ¡Feliz 4.5 aniversario, mi amor! ✨")