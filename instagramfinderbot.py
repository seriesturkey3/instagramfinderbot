import streamlit as st
import instaloader
import requests
import random
import string
import os
import json
import time
import io
from datetime import datetime
from PIL import Image
import pandas as pd
import base64

# Set page configuration
st.set_page_config(
    page_title="Instagram Bot",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with sea blue accents
def apply_custom_css():
    st.markdown("""
    <style>
    /* Dark theme with sea blue accents */
    .stApp {
        background-color: #121212;
        color: white;
    }
    .stButton>button {
        background-color: #0077B6;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0096c7;
    }
    .stTextInput>div>div>input {
        background-color: #1F1F1F;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #1F1F1F;
        color: white;
    }
    .stSelectbox>div>div>select {
        background-color: #1F1F1F;
        color: white;
    }
    .stHeader {
        color: #0077B6;
    }
    .stSubheader {
        color: #0096c7;
    }
    .profile-card {
        background-color: #1F1F1F;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        padding: 10px;
        color: #0077B6;
        font-size: 0.8rem;
    }
    .highlight {
        color: #0096c7;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F1F1F;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0077B6;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
apply_custom_css()

# Initialize session state variables
if 'instaloader' not in st.session_state:
    # Configure instaloader with proper settings to avoid rate limiting
    st.session_state.instaloader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        max_connection_attempts=3
    )

if 'bulk_results' not in st.session_state:
    st.session_state.bulk_results = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'rate_limit_delay' not in st.session_state:
    st.session_state.rate_limit_delay = 3  # seconds between requests
if 'session_file' not in st.session_state:
    st.session_state.session_file = None
if 'private_login_enabled' not in st.session_state:
    st.session_state.private_login_enabled = False

# Title and description
st.title("Instagram Bot")
st.markdown("A powerful tool for Instagram profile information and username tools")

# Login section in sidebar
with st.sidebar:
    st.header("Instagram API Authentication")
    st.markdown("Login to avoid rate limiting and 401 errors")
    
    # Private login toggle
    st.session_state.private_login_enabled = st.toggle(
        "Enable Private Login Mode", 
        st.session_state.private_login_enabled,
        help="When enabled, your credentials will be securely handled and not displayed"
    )
    
    if st.session_state.private_login_enabled:
        # Private login mode
        st.info("Private login mode is enabled. Your credentials will be securely handled.")
        
        if not st.session_state.logged_in:
            # Username input
            username_input = st.text_input(
                "Instagram Username", 
                key="private_username",
                help="Enter your Instagram username"
            )
            
            # Password input (hidden)
            password_container = st.empty()
            password_input = password_container.text_input(
                "Instagram Password", 
                type="password", 
                key="private_password",
                help="Your password is not stored and only used for authentication"
            )
            
            # Login button
            if st.button("Login Privately", key="private_login_button"):
                if username_input and password_input:
                    try:
                        with st.spinner("Authenticating with Instagram API..."):
                            # Create a new Instaloader instance for this login
                            loader = instaloader.Instaloader(
                                download_pictures=False,
                                download_videos=False,
                                download_video_thumbnails=False,
                                download_geotags=False,
                                download_comments=False,
                                save_metadata=False,
                                compress_json=False,
                                max_connection_attempts=3
                            )
                            
                            # Attempt to login
                            loader.login(username_input, password_input)
                            
                            # If login successful, update the session state
                            st.session_state.instaloader = loader
                            st.session_state.logged_in = True
                            
                            # Clear password from UI for security
                            password_container.empty()
                            
                            # Save session to a temporary file (optional)
                            session_path = "temp_session.session"
                            loader.save_session_to_file(session_path)
                            st.session_state.session_file = session_path
                            
                            st.success(f"Successfully logged in as {username_input}!")
                            st.info("Your session is now active. You can use the app with full API access.")
                    except instaloader.exceptions.BadCredentialsException:
                        st.error("Login failed: Incorrect username or password")
                    except instaloader.exceptions.TwoFactorAuthRequiredException:
                        st.error("Two-factor authentication is enabled on this account. Please use the session file method instead.")
                    except instaloader.exceptions.ConnectionException as e:
                        st.error(f"Connection error: {str(e)}")
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")
                else:
                    st.warning("Please enter both username and password")
        else:
            # Already logged in
            st.success("✅ Privately logged in to Instagram API")
            
            # Logout button
            if st.button("Logout", key="private_logout_button"):
                # Clean up session file if it exists
                if st.session_state.session_file and os.path.exists(st.session_state.session_file):
                    try:
                        os.remove(st.session_state.session_file)
                    except:
                        pass
                
                # Reset session state
                st.session_state.logged_in = False
                st.session_state.instaloader = instaloader.Instaloader(
                    download_pictures=False,
                    download_videos=False,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False
                )
                st.experimental_rerun()
        
        # Advanced login options
        with st.expander("Advanced Login Options"):
            st.markdown("### Session File Login")
            st.info("If you have a saved session file, you can upload it here.")
            
            uploaded_file = st.file_uploader("Upload session file", type=["session"])
            
            if uploaded_file is not None:
                # Save the uploaded file to a temporary location
                with open("temp_session.session", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if st.button("Login with Session File"):
                    try:
                        with st.spinner("Loading session..."):
                            # Get username from session filename
                            filename = uploaded_file.name
                            username = filename.split("_")[1].split(".")[0] if "_" in filename else "user"
                            
                            # Create a new Instaloader instance
                            loader = instaloader.Instaloader(
                                download_pictures=False,
                                download_videos=False,
                                download_video_thumbnails=False,
                                download_geotags=False,
                                download_comments=False,
                                save_metadata=False,
                                compress_json=False
                            )
                            
                            # Load session from file
                            loader.load_session_from_file(username, "temp_session.session")
                            
                            # Update session state
                            st.session_state.instaloader = loader
                            st.session_state.logged_in = True
                            st.session_state.session_file = "temp_session.session"
                            
                            st.success(f"Successfully loaded session for {username}!")
                    except Exception as e:
                        st.error(f"Failed to load session: {str(e)}")
            
            st.markdown("### Cookie Login")
            st.info("For advanced users who know how to extract cookies from their browser.")
            
            sessionid = st.text_input("sessionid cookie", key="sessionid_cookie", type="password")
            
            if st.button("Login with Cookie"):
                if sessionid:
                    try:
                        with st.spinner("Setting up session with cookies..."):
                            # Create a new Instaloader instance
                            loader = instaloader.Instaloader(
                                download_pictures=False,
                                download_videos=False,
                                download_video_thumbnails=False,
                                download_geotags=False,
                                download_comments=False,
                                save_metadata=False,
                                compress_json=False
                            )
                            
                            # Set the cookies in the session
                            loader.context._session.cookies.set("sessionid", sessionid, domain=".instagram.com")
                            
                            # Test if the session is valid
                            test_profile = loader.context.get_id_from_username('instagram')
                            
                            # If we got here without exception, login was successful
                            st.session_state.instaloader = loader
                            st.session_state.logged_in = True
                            
                            st.success("Successfully logged in with cookie!")
                    except Exception as e:
                        st.error(f"Failed to login with cookie: {str(e)}")
                else:
                    st.warning("Please enter the sessionid cookie")
    else:
        # Standard login mode
        if not st.session_state.logged_in:
            username = st.text_input("Instagram Username", key="login_username")
            password = st.text_input("Instagram Password", type="password", key="login_password")
            
            if st.button("Login", key="login_button"):
                if username and password:
                    try:
                        with st.spinner("Logging in..."):
                            st.session_state.instaloader.login(username, password)
                            st.session_state.logged_in = True
                            st.success("Successfully logged in!")
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")
                else:
                    st.warning("Please enter both username and password")
        else:
            st.success("✅ Logged in to Instagram API")
            if st.button("Logout", key="logout_button"):
                st.session_state.logged_in = False
                st.session_state.instaloader = instaloader.Instaloader(
                    download_pictures=False,
                    download_videos=False,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False
                )
                st.experimental_rerun()
    
    # Display login status
    st.markdown("---")
    if st.session_state.logged_in:
        st.success("✅ Authentication Status: Connected to Instagram API")
    else:
        st.error("❌ Authentication Status: Not connected (API access limited)")
    
    # Rate limit settings
    st.subheader("Rate Limit Settings")
    st.session_state.rate_limit_delay = st.slider(
        "Delay between requests (seconds)", 
        min_value=1, 
        max_value=10, 
        value=st.session_state.rate_limit_delay,
        help="Increase this value if you encounter rate limiting issues"
    )

# Create tabs for main functionality
tabs = st.tabs(["Profile Info", "Username Tools", "Bulk Fetching"])

# Function to handle rate limiting and API errors
def rate_limited_request(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        time.sleep(st.session_state.rate_limit_delay)  # Add delay after successful request
        return result, None
    except instaloader.exceptions.ProfileNotExistsException:
        return None, "Profile does not exist"
    except instaloader.exceptions.ConnectionException as e:
        if "429" in str(e):
            return None, "Rate limited. Please try again later or increase the delay between requests."
        elif "401" in str(e):
            return None, "Authentication required. Please log in to continue."
        else:
            return None, f"Connection error: {str(e)}"
    except instaloader.exceptions.InvalidArgumentException as e:
        return None, f"Invalid argument: {str(e)}"
    except instaloader.exceptions.BadCredentialsException:
        return None, "Bad credentials. Please log in again."
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        return None, "Two-factor authentication required. Please use session file or cookies instead."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Profile Info Tab
with tabs[0]:
    st.subheader("Profile Information")
    
    username = st.text_input("Enter Instagram Username", key="profile_username")
    
    if st.button("Fetch Profile", key="fetch_profile_button"):
        if username:
            with st.spinner("Fetching profile information..."):
                if not st.session_state.logged_in:
                    st.warning("You're not logged in. Instagram may limit your requests. Consider logging in for better results.")
                
                profile, error = rate_limited_request(
                    lambda: instaloader.Profile.from_username(st.session_state.instaloader.context, username)
                )
                
                if error:
                    st.error(error)
                elif profile:
                    # Create two columns for layout
                    col1, col2 = st.columns([1, 2])
                    
                    # Display profile picture in the first column
                    with col1:
                        try:
                            response = requests.get(profile.profile_pic_url)
                            img = Image.open(io.BytesIO(response.content))
                            st.image(img, width=200, caption=f"@{profile.username}")
                        except Exception as e:
                            st.error(f"Error loading profile picture: {str(e)}")
                    
                    # Display profile information in the second column
                    with col2:
                        st.markdown(f"<div class='profile-card'>", unsafe_allow_html=True)
                        st.markdown(f"<h3 class='highlight'>@{profile.username}</h3>", unsafe_allow_html=True)
                        st.markdown(f"**Full Name:** {profile.full_name}")
                        
                        if profile.biography:
                            st.markdown("**Biography:**")
                            st.markdown(f"<div style='background-color:#2A2A2A; padding:10px; border-radius:5px;'>{profile.biography}</div>", unsafe_allow_html=True)
                        
                        if profile.external_url:
                            st.markdown(f"**Website:** [{profile.external_url}]({profile.external_url})")
                        
                        # Create metrics for followers, following, and posts
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        metrics_col1.metric("Followers", f"{profile.followers:,}")
                        metrics_col2.metric("Following", f"{profile.followees:,}")
                        metrics_col3.metric("Posts", f"{profile.mediacount:,}")
                        
                        # Additional information
                        info_col1, info_col2 = st.columns(2)
                        info_col1.markdown(f"**Private Account:** {'Yes' if profile.is_private else 'No'}")
                        info_col2.markdown(f"**Verified:** {'Yes' if profile.is_verified else 'No'}")
                        
                        if profile.is_business_account:
                            st.markdown(f"**Business Account:** Yes")
                            if hasattr(profile, 'business_category_name') and profile.business_category_name:
                                st.markdown(f"**Category:** {profile.business_category_name}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter a username")

# Username Tools Tab
with tabs[1]:
    st.subheader("Username Tools")
    
    # Create two columns for layout
    col1, col2 = st.columns(2)
    
    # Username Checker (left column)
    with col1:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.markdown("### Check Username Availability")
        
        check_username = st.text_input("Enter username to check", key="check_username")
        
        if st.button("Check Availability", key="check_button"):
            if check_username:
                with st.spinner("Checking username availability..."):
                    if not st.session_state.logged_in:
                        st.warning("You're not logged in. Instagram may limit your requests. Consider logging in for better results.")
                    
                    profile, error = rate_limited_request(
                        lambda: instaloader.Profile.from_username(st.session_state.instaloader.context, check_username)
                    )
                    
                    if error and "not exist" in error.lower():
                        st.success(f"Username '{check_username}' appears to be available!")
                        st.info("Note: Instagram may still reject this username based on their policies.")
                    elif error and ("rate" in error.lower() or "401" in error):
                        st.error(error)
                    elif profile:
                        st.error(f"Username '{check_username}' is already taken by:")
                        st.markdown(f"**Full Name:** {profile.full_name}")
                        st.markdown(f"**Followers:** {profile.followers:,}")
                        if profile.is_verified:
                            st.markdown("**Account Status:** ✓ Verified")
                    else:
                        st.error("An error occurred while checking username availability.")
            else:
                st.warning("Please enter a username to check")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Username Generator (right column)
    with col2:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.markdown("### Generate Username Suggestions")
        
        base_word = st.text_input("Base Word (optional)", key="base_word")
        num_suggestions = st.slider("Number of Suggestions", min_value=1, max_value=20, value=5)
        
        if st.button("Generate Usernames", key="generate_button"):
            with st.spinner("Generating username suggestions..."):
                # Common suffixes and prefixes
                suffixes = ["_official", "_real", "the_", "_", ".", "__", "official", "real"]
                prefixes = ["the", "real", "official", "its", "im", "i_am"]
                
                suggestions = []
                
                # Generate random usernames
                for _ in range(num_suggestions):
                    if base_word:
                        # Use the base word
                        choice = random.randint(1, 4)
                        if choice == 1:
                            # Add random suffix
                            suffix = random.choice(suffixes)
                            username = base_word + suffix
                        elif choice == 2:
                            # Add random prefix
                            prefix = random.choice(prefixes)
                            username = prefix + "_" + base_word
                        elif choice == 3:
                            # Add random numbers
                            numbers = ''.join(random.choices(string.digits, k=random.randint(2, 4)))
                            username = base_word + numbers
                        else:
                            # Mix of letters and base word
                            letters = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 4)))
                            username = base_word + "_" + letters
                    else:
                        # Generate completely random username
                        length = random.randint(5, 12)
                        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
                    
                    suggestions.append(username)
                
                # Display generated usernames
                st.markdown("#### Generated Usernames:")
                
                # Create a DataFrame for better display
                df = pd.DataFrame({"Username": suggestions})
                
                # Display the DataFrame
                st.dataframe(df, hide_index=True)
                
                # Add a selectbox to choose a username to check
                selected_username = st.selectbox(
                    "Select a username to check availability:",
                    [""] + suggestions
                )
                
                if selected_username and st.button("Check Selected Username"):
                    with st.spinner(f"Checking {selected_username}..."):
                        if not st.session_state.logged_in:
                            st.warning("You're not logged in. Instagram may limit your requests. Consider logging in for better results.")
                        
                        profile, error = rate_limited_request(
                            lambda: instaloader.Profile.from_username(st.session_state.instaloader.context, selected_username)
                        )
                        
                        if error and "not exist" in error.lower():
                            st.success(f"Username '{selected_username}' appears to be available!")
                            st.info("Note: Instagram may still reject this username based on their policies.")
                        elif error and ("rate" in error.lower() or "401" in error):
                            st.error(error)
                        elif profile:
                            st.error(f"Username '{selected_username}' is already taken.")
                        else:
                            st.error("An error occurred while checking username availability.")
        st.markdown("</div>", unsafe_allow_html=True)

# Bulk Fetching Tab
with tabs[2]:
    st.subheader("Bulk Profile Fetching")
    
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("Enter usernames (one per line):")
    
    # Text area for usernames - Fixed the empty label issue
    bulk_usernames = st.text_area("Usernames", height=150, key="bulk_usernames")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Fetch Profiles", key="fetch_bulk_button"):
            usernames = [u.strip() for u in bulk_usernames.split('\n') if u.strip()]
            
            if usernames:
                if not st.session_state.logged_in:
                    st.warning("You're not logged in. Instagram may limit your requests. Consider logging in for better results.")
                
                st.session_state.bulk_results = []
                progress_bar = st.progress(0)
                
                for i, username in enumerate(usernames):
                    with st.spinner(f"Fetching {username}... ({i+1}/{len(usernames)})"):
                        profile, error = rate_limited_request(
                            lambda: instaloader.Profile.from_username(st.session_state.instaloader.context, username)
                        )
                        
                        if profile:
                            # Format profile information
                            info = {
                                "username": profile.username,
                                "full_name": profile.full_name,
                                "followers": profile.followers,
                                "following": profile.followees,
                                "posts": profile.mediacount,
                                "private": profile.is_private,
                                "verified": profile.is_verified,
                                "status": "success"
                            }
                            st.session_state.bulk_results.append(info)
                        else:
                            info = {
                                "username": username,
                                "status": "error",
                                "error": error if error else "Unknown error"
                            }
                            st.session_state.bulk_results.append(info)
                        
                        # Update progress bar
                        progress_bar.progress((i + 1) / len(usernames))
                
                st.success(f"Completed fetching {len(usernames)} profiles!")
            else:
                st.warning("Please enter at least one username")
    
    with col2:
        if st.button("Export Results", key="export_button"):
            if st.session_state.bulk_results:
                # Convert results to DataFrame
                df = pd.DataFrame(st.session_state.bulk_results)
                
                # Convert DataFrame to CSV
                csv = df.to_csv(index=False)
                
                # Create a download button
                b64 = base64.b64encode(csv.encode()).decode()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"instagram_profiles_{timestamp}.csv"
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("No results to export")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display results if available
    if st.session_state.bulk_results:
        st.markdown("### Results")
        
        # Create tabs for different views
        result_tabs = st.tabs(["Table View", "Card View"])
        
        with result_tabs[0]:
            # Table view
            df = pd.DataFrame(st.session_state.bulk_results)
            st.dataframe(df, use_container_width=True)
        
        with result_tabs[1]:
            # Card view
            for result in st.session_state.bulk_results:
                st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                
                if result["status"] == "success":
                    st.markdown(f"<h3 class='highlight'>@{result['username']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"**Full Name:** {result['full_name']}")
                    
                    # Create metrics for followers, following, and posts
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    metrics_col1.metric("Followers", f"{result['followers']:,}")
                    metrics_col2.metric("Following", f"{result['following']:,}")
                    metrics_col3.metric("Posts", f"{result['posts']:,}")
                    
                    # Additional information
                    info_col1, info_col2 = st.columns(2)
                    info_col1.markdown(f"**Private Account:** {'Yes' if result['private'] else 'No'}")
                    info_col2.markdown(f"**Verified:** {'Yes' if result['verified'] else 'No'}")
                
                else:
                    st.markdown(f"<h3>@{result['username']}</h3>", unsafe_allow_html=True)
                    st.error(f"Error: {result['error']}")
                
                st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>Made by [Your Name]</div>", unsafe_allow_html=True)