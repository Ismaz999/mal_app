import streamlit as st
from io import BytesIO
from PIL import Image
import rembg
from rembg import remove
# from fichier_def_mult import request_anime, extract_id_and_title, get_anime_reviews, analyze_sentiment_and_emotions
from streamlit_option_menu import option_menu
from bs4 import BeautifulSoup
import requests

st.set_page_config(layout="wide", page_title="Image Background Remover 2") # On configure la forme de la page en wide 

st.title('Ma première app Streamlit')
st.write("Hello Upload!")

st.sidebar.title("Options")
st.sidebar.write("## Upload and download :gear:")
st.sidebar.write("## Remove background from your image")
st.sidebar.write(
    ":dog: Try uploading an image to watch the background magically removed. Full quality images can be downloaded from the sidebar."
)

input_utilisateur = st.text_input("Analyse des émotions d'une oeuvre")

# def choix_anime(input_utilisateur):
#     URL = f"https://myanimelist.net/search/all?q={input_utilisateur.replace(' ', '%20')}"
#     rq_list = []
#     recup_page = requests.get(URL)
#     recup_soup = BeautifulSoup(recup_page.content, "html.parser")
#     tag_a = recup_soup.find('a', class_='hoverinfo_trigger')
#     return tag_a

if input_utilisateur:
    URL = f"https://myanimelist.net/search/all?q={input_utilisateur.replace(' ', '%20')}"
    rq_list = []
    recup_page = requests.get(URL)
    recup_soup = BeautifulSoup(recup_page.content, "html.parser")

    tag_a = recup_soup.find('a', class_='hoverinfo_trigger')


    # clean_tag = choix_anime(input_utilisateur)
    if tag_a:
        st.write("Voila le nom de l'anime : ", input_utilisateur)
        # st.write("ca cest bonus : ", tag_a)

        col3, col4= st.columns(2)

        name_tag = tag_a.find('img')
        col3.write(name_tag['alt'])
        img_tag = tag_a.find('img')
        col4.image(img_tag['data-src'])
    else :
        st.write("Aucun anime trouvé")
else:
    st.image("https://i.imgur.com/GL1x4ad.jpeg", caption="En attente d'un anime")

image_upload = st.sidebar.file_uploader("Joindre votre fichier : ", type=["jpg", "png", "jpeg"])

temp_options = ['low', 'medium', 'high', 'naruto']
st.sidebar.header("BONSOIR")
temp = st.sidebar.select_slider("Choose a temperature :", temp_options)

st.write("La température est ", temp)
st.sidebar.header("BONJOUR")

menu = ['viande', 'poisson', 'tomate']


selection_menu = option_menu(
    "Choix du plat", 
    options=menu, 
    icons=[':chicken:',':fish:',':tomato:'],
    menu_icon="cast")

st.selectbox("Menu", options=temp_options)

if selection_menu == "viande":
    st.write(f"Le menu {selection_menu} est un sandwich au poulet")
if selection_menu == "poisson":
    st.write(f"Le menu {selection_menu} est un Filet o fish")
if selection_menu == "tomate":
    st.write(f"pour le menu {selection_menu} ya que du KETCHUP")

def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

if image_upload:

    col1, col2 = st.columns(2)

    image = Image.open(image_upload)
    col1.image(image_upload, caption="L'image avant")

    fixed_image = rembg.remove(image)

    col2.image(fixed_image, caption="L'image détourée")

    downloadable_image = convert_image(fixed_image)
    st.sidebar.download_button("Image détourrée ", downloadable_image, "fichiercaca.png", "image/png")

# if image_upload:
#     image = Image.open(image_upload)
#     fixed = remove(image)
#     downloadable_image = convert_image(fixed)
#     st.download_button(
#         "Download fixed image", downloadable_image, "fixed.png", "image/png"
#     )



# st.title("Hello Upload!")

# # Upload the image
# image_upload = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# # Now, you can download the same file!
# if image_upload:
# 	st.download_button("Download your file here", image_upload, "my_image.png", "image/png")
