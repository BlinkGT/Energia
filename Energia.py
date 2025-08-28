import streamlit as st
import math
import base64
import json
import hashlib
from datetime import datetime

# --- Constantes ---
TOLERANCIA = 0.05  # tolerancia en la comparación de respuestas (±0.05)
GRAVEDAD = 9.81    # g en m/s^2

# --- Diccionario de imágenes por pregunta ---
# Reemplaza estas rutas por URLs públicas si quieres que se vean desde la web
pregunta_imagenes = {
    0: "images2/1.png",  # Pregunta 1 (Péndulo)
    1: "images2/2.png",  # Pregunta 2 (Plano inclinado)
    2: "images2/3.png",  # Pregunta 3 (Resorte estirado)
    3: "images2/4.jpg",  # Pregunta 4 (Resorte comprimido)
    4: "images2/5.jpg"   # Pregunta 5 (Potencia)
}

# --- Funciones auxiliares ---

def redondear_a_2_decimales(numero):
    """
    Redondea a 2 decimales y devuelve float con 2 decimales.
    Si es None, inf o nan, devuelve None.
    """
    if numero is None:
        return None
    try:
        if math.isinf(numero) or math.isnan(numero):
            return None
    except Exception:
        return None
    try:
        return float(f"{numero:.2f}")
    except (TypeError, ValueError):
        return None


def calcular_respuestas_fisicas(clave):
    """Calcula las respuestas correctas para las 5 preguntas usando la clave ingresada.
    Devuelve un diccionario con las claves 'pregunta1'..'pregunta5'."""
    respuestas = {}

    # Validación básica
    try:
        clave_val = float(clave)
    except Exception:
        clave_val = None

    if clave_val is None or clave_val <= 0:
        for i in range(1, 6):
            respuestas[f'pregunta{i}'] = None
        return respuestas

    # --- Pregunta 1 ---
    # Un péndulo detenido en altura h = clave; al llegar al punto más bajo v = sqrt(2 g h)
    h_q1 = clave_val
    v_q1 = math.sqrt(2 * GRAVEDAD * h_q1)
    respuestas['pregunta1'] = redondear_a_2_decimales(v_q1)

    # --- Pregunta 2 ---
    # Caja de masa m = clave que recorre distancia d = clave en plano sin fricción, ang = 30°
    # Trabajo del peso: W = m * g * sin(theta) * d
    masa_q2 = clave_val
    distancia_q2 = clave_val
    angulo_q2_rad = math.radians(30)
    trabajo_q2 = masa_q2 * GRAVEDAD * math.sin(angulo_q2_rad) * distancia_q2
    respuestas['pregunta2'] = redondear_a_2_decimales(trabajo_q2)

    # --- Pregunta 3 ---
    # Masa m = clave cuelga del resorte y estira Δx = 0.2 m -> equilibrio: k = m g / Δx
    masa_q3 = clave_val
    delta_x_q3 = 0.2
    k_q3 = (masa_q3 * GRAVEDAD) / delta_x_q3
    respuestas['pregunta3'] = redondear_a_2_decimales(k_q3)

    # --- Pregunta 4 ---
    # Caída desde h = 1 m y compresión x = 0.1 m: m g h = 1/2 k x^2 -> k = 2 m g h / x^2
    masa_q4 = clave_val
    h_q4 = 1.0
    x_q4 = 0.1
    k_q4 = (2 * masa_q4 * GRAVEDAD * h_q4) / (x_q4 ** 2)
    respuestas['pregunta4'] = redondear_a_2_decimales(k_q4)

    # --- Pregunta 5 ---
    # Hombre empuja con F = 100 N; rampa con altura h = 10 m y ángulo 25° -> d = h / sin(25°)
    # Potencia = Trabajo / tiempo ; tiempo = clave
    tiempo_q5 = clave_val
    fuerza_q5 = 100.0
    h_q5 = 10.0
    ang_q5_rad = math.radians(25)
    distancia_q5 = h_q5 / math.sin(ang_q5_rad)
    trabajo_q5 = fuerza_q5 * distancia_q5
    potencia_q5 = trabajo_q5 / tiempo_q5
    respuestas['pregunta5'] = redondear_a_2_decimales(potencia_q5)

    return respuestas


def codificar_calificacion(datos_calificacion):
    json_data = json.dumps(datos_calificacion, ensure_ascii=False)
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    return encoded_data


# --- Lógica de la aplicación Streamlit ---
st.title("Comprobación de Energía, Trabajo y Potencia")

# Inicialización del session_state
if 'nombre_alumno' not in st.session_state:
    st.session_state.nombre_alumno = ""
if 'clave_alumno' not in st.session_state:
    st.session_state.clave_alumno = None
if 'preguntas_list' not in st.session_state:
    st.session_state.preguntas_list = []
if 'respuestas_estudiante_guardadas' not in st.session_state:
    st.session_state.respuestas_estudiante_guardadas = []
if 'pregunta_actual_idx' not in st.session_state:
    st.session_state.pregunta_actual_idx = 0
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
if 'examen_finalizado' not in st.session_state:
    st.session_state.examen_finalizado = False
if 'respuestas_correctas_calc' not in st.session_state:
    st.session_state.respuestas_correctas_calc = {}
if 'final_dat_content' not in st.session_state:
    st.session_state.final_dat_content = None
if 'final_filename' not in st.session_state:
    st.session_state.final_filename = None

# --- Pantalla de inicio ---
if not st.session_state.examen_iniciado:
    st.write("¡Bienvenido a la comprobación de Energía, Trabajo y Potencia!")
    nombre_input = st.text_input("Por favor, ingresa tu nombre completo:", key="nombre_entrada")
    clave_input = st.text_input("Ingresa tu número de clave (un número POSITIVO):", key="clave_entrada")

    if st.button("Iniciar Examen"):
        if not nombre_input:
            st.error("Por favor, ingresa tu nombre.")
            st.stop()
        try:
            clave = float(clave_input)
            if clave <= 0:
                st.error("La clave debe ser un número POSITIVO.")
                st.stop()
        except ValueError:
            st.error("Número de clave inválido. Ingresa un número.")
            st.stop()

        st.session_state.nombre_alumno = nombre_input
        st.session_state.clave_alumno = clave
        st.session_state.examen_iniciado = True
        st.session_state.respuestas_correctas_calc = calcular_respuestas_fisicas(clave)

        # Textos de las preguntas (usando la clave ingresada)
        st.session_state.preguntas_list = [
            f"1) Un péndulo se encuentra detenido en su punto más alto a ${clave}$ metros de altura. Cuando se le suelte y llegue a su punto más bajo, encuentre su velocidad en m/s. Solo responde con la cantidad numérica. (2 decimales)",
            f"2) Una caja de masa ${clave}$ kg, se desliza por un plano inclinado sin fricción a $30^\circ$. Si la distancia recorrida sobre el plano es de ${clave}$ m, encuentre el trabajo realizado por el peso en J. Solo responde con la cantidad numérica. (2 decimales)",
            f"3) Se engancha una masa de ${clave}$ kg bajo un resorte y se suelta, de tal manera que este se estira 0.2 m. Encuentre la constante de dicho resorte en N/m. Solo responde con la cantidad numérica. (2 decimales)",
            f"4) Desde una altura de 1 m se deja caer una masa de ${clave}$ kg, como se observa en la figura. Esta masa comprimirá el resorte una distancia de 0.1 m. Encuentre la constante del resorte en N/m. Solo responde con la cantidad numérica. (2 decimales)",
            f"5) El hombre de la figura empuja la caja sobre un plano inclinado sin fricción, a $25^\circ$ y con una altura de 10 m. La fuerza que el hombre ejerce es de 100 N. Si la caja recorre la rampa completa y el tiempo que el hombre tarda en hacerlo es de ${clave} segundos, encuentre la potencia del hombre en W. Solo responde con la cantidad numérica. (2 decimales)"
        ]
        st.rerun()


# --- Pantalla del examen (preguntas) ---
elif st.session_state.examen_iniciado and not st.session_state.examen_finalizado:
    st.header(f"¡Hola, {st.session_state.nombre_alumno}!")
    st.subheader(f"Clave de examen: {st.session_state.clave_alumno}")

    if st.session_state.pregunta_actual_idx < len(st.session_state.preguntas_list):
        pregunta_idx = st.session_state.pregunta_actual_idx
        pregunta_actual_text = st.session_state.preguntas_list[pregunta_idx]
        st.markdown(f"**Pregunta {pregunta_idx + 1} de {len(st.session_state.preguntas_list)}:**")
        st.markdown(pregunta_actual_text)

        # Mostrar imagen asociada (si existe)
        if pregunta_idx in pregunta_imagenes:
            try:
                url_img = pregunta_imagenes[pregunta_idx]
                # Si la ruta NO empieza con http(s) avisamos que es una ruta local
                # if not (str(url_img).lower().startswith("http://") or str(url_img).lower().startswith("https://")):
                   # st.warning(f"Advertencia: La imagen para la pregunta {pregunta_idx + 1} aún utiliza una ruta local ('{url_img}'). Por favor, reemplázala con la URL pública de tu imagen de GitHub para que sea visible en la aplicación web.")
                st.image(url_img, caption=f"Imagen para la Pregunta {pregunta_idx + 1}", use_container_width=True)
                st.markdown("---")
            except Exception as e:
                st.warning(f"Error al cargar la imagen para la pregunta {pregunta_idx + 1}. Asegúrate de que la URL sea correcta y accesible: {e}")

        # Input numérico (una sola respuesta por pregunta)
        respuesta_input = st.text_input("Tu respuesta (ej. 1.00):", key=f"respuesta_{pregunta_idx}")
        st.markdown("---")

        if st.button("Siguiente Pregunta"):
            st.session_state.respuestas_estudiante_guardadas.append({
                "pregunta_idx": pregunta_idx,
                "respuestas_ingresadas": [respuesta_input]
            })
            st.session_state.pregunta_actual_idx += 1
            st.rerun()

    else:
        # Finalizar examen y calificar
        calificacion = 0
        detalles_respuestas = []
        total_preguntas_validas_para_calificar = 0

        for i, respuesta_guardada in enumerate(st.session_state.respuestas_estudiante_guardadas):
            pregunta_idx = respuesta_guardada['pregunta_idx']
            respuestas_usuario_str_list = respuesta_guardada['respuestas_ingresadas']

            respuesta_correcta_actual = st.session_state.respuestas_correctas_calc.get(f'pregunta{pregunta_idx + 1}')

            es_correcta_esta_pregunta = True
            respuestas_usuario_num = []

            if respuesta_correcta_actual is not None:
                if len(respuestas_usuario_str_list) != 1:
                    es_correcta_esta_pregunta = False
                else:
                    try:
                        usuario_val = float(respuestas_usuario_str_list[0])
                        respuestas_usuario_num.append(round(usuario_val, 2))
                        if abs(round(usuario_val, 2) - respuesta_correcta_actual) > TOLERANCIA:
                            es_correcta_esta_pregunta = False
                    except ValueError:
                        es_correcta_esta_pregunta = False

                if es_correcta_esta_pregunta:
                    total_preguntas_validas_para_calificar += 1
            else:
                es_correcta_esta_pregunta = False

            if es_correcta_esta_pregunta:
                calificacion += 1

            respuesta_ingresada_formateada = respuestas_usuario_str_list[0] if respuestas_usuario_str_list else ""

            detalles_respuestas.append({
                "pregunta": st.session_state.preguntas_list[pregunta_idx],
                "respuesta_ingresada": respuesta_ingresada_formateada,
                "respuestas_ingresadas_num": respuestas_usuario_num,
                "respuesta_correcta_esperada": respuesta_correcta_actual,
                "es_correcta": es_correcta_esta_pregunta
            })

        # Preparar datos para el hash y archivo .dat
        datos_para_hash = {
            "nombre_estudiante": st.session_state.nombre_alumno,
            "clave_ingresada": st.session_state.clave_alumno,
            "calificacion_obtenida": calificacion,
            "total_preguntas_examinadas": len(st.session_state.preguntas_list),
            "total_preguntas_validas_para_calificar": total_preguntas_validas_para_calificar,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "respuestas_detalles": detalles_respuestas
        }

        datos_json_str = json.dumps(datos_para_hash, sort_keys=True, ensure_ascii=False)
        hash_sha256 = hashlib.sha256(datos_json_str.encode('utf-8')).hexdigest()

        datos_finales_para_guardar = datos_para_hash.copy()
        datos_finales_para_guardar["hash_sha256_integridad"] = hash_sha256

        st.session_state.final_dat_content = codificar_calificacion(datos_finales_para_guardar)
        nombre_sanitizado = st.session_state.nombre_alumno.replace(' ', '_')
        st.session_state.final_filename = f"calificacion_{nombre_sanitizado}_{st.session_state.clave_alumno}.dat"

        st.session_state.examen_finalizado = True
        st.rerun()


# --- Pantalla examen finalizado ---
elif st.session_state.examen_finalizado:
    st.success(f"¡Gracias por completar el examen, {st.session_state.nombre_alumno}!")
    st.write("Tu examen ha terminado. Por favor, descarga tu archivo de calificación y envíaselo a tu profesor.")

    if st.session_state.final_dat_content and st.session_state.final_filename:
        st.download_button(
            label="Descargar Archivo de Calificación (.dat)",
            data=st.session_state.final_dat_content.encode('utf-8'),
            file_name=st.session_state.final_filename,
            mime="application/octet-stream"
        )
    else:
        st.warning("No se pudo generar el archivo de descarga. Por favor, contacta a tu profesor.")

    st.write("Puedes cerrar esta pestaña del navegador.")
    st.info("Para realizar el examen de nuevo, cierra y vuelve a abrir esta pestaña.")


