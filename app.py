import streamlit as st
import openai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import requests
from io import BytesIO
from st_social_media_links import SocialMediaIcons

# Función para generar la receta usando OpenAI
def generar_receta(ingredientes):
    prompt = f"Eres un chef profesional. Crea una receta con estos ingredientes: {ingredientes}."
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# Función para generar imagen con DALL-E
def generar_imagen(ingredientes):
    # Modificamos el prompt para especificar un plato elegante con una bebida
    prompt_img = f"Un plato elegante servido con los siguientes ingredientes: {ingredientes}, acompañado de una bebida sofisticada, en un ambiente gourmet."
    response_img = openai.Image.create(prompt=prompt_img, n=1, size="1024x1024")
    image_url = response_img['data'][0]['url']
    image_response = requests.get(image_url)
    return Image.open(BytesIO(image_response.content))

# Función para crear el PDF
def crear_pdf(nombre_plato, receta, image=None):
    pdf_output = BytesIO()
    pdf = canvas.Canvas(pdf_output, pagesize=letter)
    pdf.setTitle(nombre_plato)

    # Título y receta
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(300, 750, nombre_plato)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 700, "Receta:")

    # Dividir la receta en líneas y agregarla al PDF
    y = 680
    for linea in receta.split('\n'):
        pdf.drawString(50, y, linea)
        y -= 20
        if y < 100:  # Nueva página si es necesario
            pdf.showPage()
            y = 750

    # Añadir imagen si existe
    if image:
        image = image.resize((250, 250))  # Redimensionar la imagen a un tamaño más pequeño
        pdf.drawImage(ImageReader(image), 150, 400, width=250, height=250)  # Tamaño ajustado a 250x250

    pdf.showPage()
    pdf.save()
    pdf_output.seek(0)
    return pdf_output

# Interfaz en Streamlit
# URL de la imagen
image_url = "https://cdn.cpdonline.co.uk/wp-content/uploads/2023/04/28123407/Experienced-chef-de-partie-1200x350.jpg"
image_response = requests.get(image_url)
image = Image.open(BytesIO(image_response.content))

# Mostrar la imagen antes del título
st.image(image, caption=' ', use_column_width=True)

st.title('Recomendador de Recetas con IA')

api_key = st.text_input('Introduce tu clave de API de OpenAI', type='password')
if api_key:
    openai.api_key = api_key

    ingredientes = st.text_area('Introduce los ingredientes que tienes disponibles (separados por comas):')
    
    if st.button('Generar Receta') and ingredientes:
        try:
            receta = generar_receta(ingredientes)
            st.markdown("### Receta generada:")
            st.write(receta)
            
            imagen = generar_imagen(ingredientes)
            st.image(imagen, caption='Imagen generada del plato', use_column_width=True)
            
            nombre_plato = "Receta generada con GPT-4"
            pdf_output = crear_pdf(nombre_plato, receta, image=imagen)
            
            st.download_button(
                label="Descargar Receta en PDF",
                data=pdf_output,
                file_name="receta.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar la receta: {str(e)}")
else:
    st.info('Por favor, ingresa tu clave de API para utilizar esta aplicación.')

# Pie de página con información del desarrollador y logos de redes sociales
st.markdown("""
---
**Desarrollador:** Edwin Quintero Alzate
**Email:** egqa1975@gmail.com
""")

social_media_links = [
    "https://www.facebook.com/edwin.quinteroalzate",
    "https://www.linkedin.com/in/edwinquintero0329/",
    "https://github.com/Edwin1719"]

social_media_icons = SocialMediaIcons(social_media_links)
social_media_icons.render()