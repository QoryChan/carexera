import streamlit as st
import sqlite3
import os
from PIL import Image
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
from io import BytesIO
from reportlab.lib.pagesizes import inch
from reportlab.lib.utils import ImageReader
from streamlit_lottie import st_lottie

# Page configuration
st.set_page_config(page_title="PPFD", page_icon=":tada:", layout="wide")

# Load Lottie animation
def load_lottieur(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")

# Load images
lottie_coding = load_lottieur("https://lottie.host/f96183f0-299f-42f2-ac4b-441947a9410e/2GD2UFgEGY.json")
img_logocarexera = Image.open("images/LogoCareXera.png")
img_lottie_animation = Image.open("images/carexera.png")
img_contact_form = Image.open("images/test.jpg")
lottie_coding2 = load_lottieur("https://lottie.host/6fae6c05-2885-41b9-9bff-13e2e342cf53/xuE7M1c961.json")
lottie_coding3 = load_lottieur("https://lottie.host/62179403-c4f2-41e8-8ca9-5e0b9661e3d1/Mk93miy5My.json")

# Function to check login credentials
def authenticate(username, password):
    return username == "Admin" and password == "123"

# Function to display an image from a base64-encoded string
def display_image_from_base64(base64_string, caption, width=300):
    try:
        image_data = base64.b64decode(base64_string)
        image_stream = BytesIO(image_data)
        image = Image.open(image_stream)
        st.image(image, caption=caption, width=width, use_column_width=False)
    except Exception as e:
        st.warning(f"Unable to display image: {e}")

# Connect to SQLite database
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Create the users table if it does not exist
c.execute('''
          CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              name TEXT,
              address TEXT,
              email TEXT,
              phone TEXT,
              picture_data TEXT,
              picture_names TEXT
          )
          ''')

# Commit the changes
conn.commit()

# Main Page
with st.container():
    st.image(img_logocarexera, width=300)
    st.subheader("Hi, Welcome :wave:")
    st.title("Personality Prediction System Based on Fingerprint Detection")
    st.write("By using the TinkerTalent system, all the data gathered will be stored on this website. It will be monitored and safely secured")

with st.container():
    st.write("-----")
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("What we do?")
        st.write("We enhanced a Streamlit application by adding a visually appealing design using custom CSS, integrating animations, and organizing images in a three-column layout. The app now includes user authentication, a form for collecting user information, and functionality to upload, store, and display images in an organized manner. We also implemented a search feature for retrieving and managing user data stored in a SQLite database, allowing for efficient user information handling, including the ability to edit or delete entries directly from search results.")
        st.write("To enhance user experience, the application incorporates custom CSS and Lottie animations, creating an engaging and intuitive interface. This ensures that users can navigate the system effortlessly, whether they are uploading data, searching for records, or generating reports.")
        st_lottie(lottie_coding2, width=100, height=100, key="coding")

# Streamlit app
st.title('PPFD')
st.write("Please Enter Valid Username & Password")
# Navigation
menu = ["Login", "Main Menu", "My Projects"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Login":
    st.subheader("Login")
    login_username = st.text_input('Username:')
    login_password = st.text_input('Password:', type='password')
    if st.button('Login'):
        if authenticate(login_username, login_password):
            st.success('Login successful!')
            st.session_state.logged_in = True
        else:
            st.error('Invalid credentials. Please try again.')

if getattr(st.session_state, 'logged_in', False):
    # Main menu
    st.subheader("Main Menu")

    # Log Out button
    if st.button('Log Out'):
        st.session_state.logged_in = False

    # Collect user information
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input('Enter Client ID')
        name = st.text_input('Enter Name')
        address = st.text_input('Enter Address')
        email = st.text_input('Enter Email')
        phone = st.text_input('Enter Phone Number')

    with col2:
        # Allow users to upload unlimited images with the same names
        pictures = st.file_uploader('Upload Images', type=['jpg', 'png', 'jpeg', 'bmp'], accept_multiple_files=True, key="uploader")

    if st.button('Submit') and pictures:
        # Create a folder for each user based on their ID
        user_folder = os.path.join('uploads', user_id)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Save data to the database
        picture_data = []
        picture_names = []
        for picture in pictures:
            original_filename = picture.name  # Use the original file name
            picture_path = os.path.join(user_folder, original_filename)
            with open(picture_path, 'wb') as f:
                f.write(picture.read())
            with open(picture_path, 'rb') as f:
                picture_data.append(base64.b64encode(f.read()).decode("utf-8"))
            picture_names.append(original_filename)

        try:
            c.execute('INSERT INTO users (id, name, address, email, phone, picture_data, picture_names) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (user_id, name, address, email, phone, ','.join(picture_data), ','.join(picture_names)))
            conn.commit()
            st.success('User information saved successfully.')
        except Exception as e:
            st.error(f"Error inserting data into the database: {e}")

    # Search functionality
    search_term = st.text_input('Search by Name or ID')
    if st.button('Search'):
        # Query the database for matching records
        c.execute('SELECT * FROM users WHERE name LIKE ? OR id LIKE ?', (f'%{search_term}%', f'%{search_term}%'))
        results = c.fetchall()

        # Store the results in session state to handle state correctly
        st.session_state.search_results = results

    # Display search results or error message
    if 'search_results' in st.session_state:
        results = st.session_state.search_results
        if results:
            for result in results:
                st.write(f"**ID:** {result[0]}\n**Name:** {result[1]}\n**Address:** {result[2]}\n**Email:** {result[3]}\n**Phone:** {result[4]}")

                # Display images
                if result[5]:
                    picture_data = result[5].split(',')
                    picture_names = result[6].split(',')
                    sorted_images = sorted(zip(picture_names, picture_data))
                    for name, data in sorted_images:
                        display_image_from_base64(data, caption=f'Image: {name}', width=150)  # Adjust the width as needed

                # Add a delete button for each search result
                if st.button(f"Delete {result[0]}", key=f"delete_{result[0]}"):
                    try:
                        c.execute('DELETE FROM users WHERE id = ?', (result[0],))
                        conn.commit()
                        st.success(f"User ID {result[0]} deleted successfully.")
                        # Remove the deleted record from search results in session state
                        st.session_state.search_results = [res for res in results if res[0] != result[0]]
                        break  # Break to avoid changing state during iteration
                    except Exception as e:
                        st.error(f"Error deleting data from the database: {e}")

                # Add an edit button for each search result
                if st.button(f"Edit {result[0]}", key=f"edit_{result[0]}"):
                    st.session_state.editing = result[0]

        else:
            st.error(f"No records found for '{search_term}'. Please try again.")

    # Edit functionality
    if 'editing' in st.session_state:
        edit_id = st.session_state.editing
        st.subheader(f"Editing User ID: {edit_id}")

        # Fetch current data
        c.execute('SELECT * FROM users WHERE id = ?', (edit_id,))
        user_data = c.fetchone()

        if user_data:
            # Pre-fill the form with current data
            edit_name = st.text_input('Edit Name', user_data[1])
            edit_address = st.text_input('Edit Address', user_data[2])
            edit_email = st.text_input('Edit Email', user_data[3])
            edit_phone = st.text_input('Edit Phone Number', user_data[4])

            if st.button('Save Changes'):
                try:
                    c.execute('UPDATE users SET name = ?, address = ?, email = ?, phone = ? WHERE id = ?',
                              (edit_name, edit_address, edit_email, edit_phone, edit_id))
                    conn.commit()
                    st.success('User information updated successfully.')
                    st.session_state.editing = None  # Clear editing state
                except Exception as e:
                    st.error(f"Error updating data in the database: {e}")


# Generate PDF report
st.subheader("Generate PDF Report")
report_user_id = st.text_input("Enter User ID for Report Generation:")
if st.button("Generate Report"):
    # Fetch user data from the database
    c.execute('SELECT * FROM users WHERE id = ?', (report_user_id,))
    user_data = c.fetchone()

    if user_data:
        # Generate PDF
        pdf_filename = f"report_user_{user_data[0]}.pdf"
        pdf_path = os.path.join("reports", pdf_filename)
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        # Write user information to PDF
        c.drawString(inch, 10 * inch, f"User ID: {user_data[0]}")
        c.drawString(inch, 9.5 * inch, f"Name: {user_data[1]}")
        c.drawString(inch, 9 * inch, f"Address: {user_data[2]}")
        c.drawString(inch, 8 * inch, f"Email: {user_data[3]}")
        c.drawString(inch, 7.5 * inch, f"Phone: {user_data[4]}")

        # Display images in the PDF
        if user_data[5]:
            picture_data = user_data[5].split(',')
            picture_names = user_data[6].split(',')
            sorted_images = sorted(zip(picture_names, picture_data))
            y_offset = 7 * inch  # Initial vertical position for images
            max_width = 15 # Maximum width for images
            max_height = 15  # Maximum height for images

            for name, data in sorted_images:
                try:
                    # Convert base64 image data to bytes
                    image_data = base64.b64decode(data)
                    
                    # Open image using PIL
                    img = Image.open(BytesIO(image_data))
                    
                    # Calculate resized dimensions while maintaining aspect ratio
                    img_width, img_height = img.size
                    aspect_ratio = img_height / img_width
                    img_width = min(img_width, max_width)
                    img_height = min(img_height, max_height)
                    if img_width < max_width or img_height < max_height:
                        img_width = max_width
                        img_height = max_height
                    else:
                        img_height = int(img_width * aspect_ratio)
                    
                    # Resize image
                    img = img.resize((img_width, img_height))
                    
                    # Convert image to ReportLab ImageReader format
                    rl_image = ImageReader(img)
                    
                    # Draw image on the canvas
                    c.drawImage(rl_image, inch, y_offset - img_height, width=img_width, height=img_height)
                    
                    # Adjust vertical position for the next image
                    y_offset -= (img_height + 0.5 * inch)
                except Exception as e:
                    st.warning(f"Unable to display image in PDF: {e}")

        # Save PDF
        c.save()

        # Provide download link for the generated PDF
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            st.download_button(label="Download PDF Report", data=pdf_bytes, file_name=pdf_filename, mime="application/pdf")
        st.success(f"PDF Report generated successfully. You can download it above.")
    else:
        st.error(f"No user found with ID: {report_user_id}. Please try again.")

# Close the database connection
conn.close()

# Additional sections (Projects, Contact, etc.)
with st.container():
    st.write("---")
    st.header("About Us")
    st.write("##")
    image_column, text_column = st.columns((1, 2))
    with image_column:
        st.image(img_lottie_animation)
    with text_column:
        st.subheader("WELCOME TO CAREXERA || PREDICT || PREPARE || PRESERVE")
        st.write("CareXera’s Aspiration Is To Provide The Most Affordable Personalized Predictive Genetic Testing And End-To-End Solution For All Healthcare Professionals In Preventing Chronic Diseases Among Corporate Employees And The Public As Well As Enhancing Personalized Childhood Development And Education In Achieving Malaysia’s Sustainable Development Goals (SDG 3 And SDG 4).")
        st.markdown("(https://carexera.com/)")

with st.container():
    image_column, text_column = st.columns((1, 2))
    with image_column:
        st.image(img_contact_form)
    with text_column:
        st.subheader("Introduction To CareXera Health")
        st.write(
            "CareXera Sdn. Bhd., established in August 2021, is the first company in Malaysia that provides DNA and Epigenetics Profiling with Personalized Healthy Lifestyle Coaching program. Our aspiration is to empower the current and future generations by preventing chronic diseases, promoting longevity and enhancing childhood learning through genetic profiling. Meanwhile, our aim is to offer the most affordable predictive tools equipped with personalized end-to-end solutions to help individuals accomplish healthier lifestyles, optimal mental well-being and improvement in work life performance. Hence, we are working in tandem with medical and healthcare professionals to provide personalized predictive, preventive and protective interventional programs, advisory, training, products and services. In addition, we are collaborating with educational institutions to empower parents in enhancing their children’s Talent, IQ, EQ, and Personality by implementing personalized learning and development based on our Child DNA profiling."
        )
        st.markdown("(https://carexera.com/about-us/)")

# Contact
with st.container():
    st.write("---")
    st.header("Contact Us for Assistance with Any Issues")
    st.write("##")

    contact_form = """<form action="https://formsubmit.co/akrambuqhari00@gmail.com" method="POST">
    <input type="hidden" name="_captcha" value="false">
    <input type="text" name="name" placeholder="Your Name" required>
    <input type="email" name="email" placeholder="Your email" required>
    <textarea name="message" placeholder="Your message here" required></textarea>
    <button type="submit">Send</button>
</form>"""

    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown(contact_form, unsafe_allow_html=True)
    with right_column:
        st.empty()




#total client has been entered //dashboard //user can check total_client that has been submitted
#proof of client payment, submitted by practicioner pdf/image
#secure login
#connectivity device
#practicioner validility
#certificate number + @login
#2f2 aunthetication- by email/phonenumber
#fingerprint capture
#login admin module & login practicioner module
#button review information-date/time/status //// forreview(pending)/reviewed /////admin submit/approve button /// store in same database sql /// backup database, temporary checking

#fingerprint checking by admin (accept/denied)#check box 
        #send message(fingerprint error & request replace) to practicioner by email from the website  
        #create pending message
          #submit new data for replace by practicioner(Function on practicioner site to submit/replace data)

          #ADMIN PAGE //// PRACTIONIONER

#DISC Checking fingerprint 6images