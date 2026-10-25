# import pickle
# import requests
# import streamlit as st
# from dotenv import load_dotenv
# from help_man import ChatPipeline  # needed so pickle can find the class

# load_dotenv()

# st.set_page_config(page_title="Bot Tester", page_icon="💬")
# st.title("💬 Bot Tester")

# # ---------- sidebar ----------
# with st.sidebar:
#     mode = st.radio("Test via", ["Direct pkl", "FastAPI endpoint"])
#     api_url = st.text_input("API URL", "http://localhost:8000/chat",
#                             disabled=(mode == "Direct pkl"))
#     if st.button("Clear chat"):
#         st.session_state.history = []
#         st.rerun()
#     show_debug = st.checkbox("Show history payload")


# # ---------- load pipeline once ----------
# @st.cache_resource
# def load_pipeline(path="chat_pipeline.pkl"):
#     with open(path, "rb") as f:
#         return pickle.load(f)


# # ---------- state ----------
# if "history" not in st.session_state:
#     st.session_state.history = []  # [{"role": "user"|"ai", "text": str}]

# # ---------- render past messages ----------
# for m in st.session_state.history:
#     with st.chat_message("user" if m["role"] == "user" else "assistant"):
#         st.markdown(m["text"])

# # ---------- handle new input ----------
# if prompt := st.chat_input("Type a message..."):
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 if mode == "Direct pkl":
#                     pipe = load_pipeline()
#                     reply, new_history = pipe.run(prompt, st.session_state.history)
#                 else:
#                     r = requests.post(
#                         api_url,
#                         json={"message": prompt, "history": st.session_state.history},
#                         timeout=60,
#                     )
#                     r.raise_for_status()
#                     data = r.json()
#                     reply, new_history = data["reply"], data["history"]

#                 st.markdown(reply)
#                 st.session_state.history = new_history
#             except Exception as e:
#                 st.error(f"Error: {e}")

# if show_debug:
#     st.sidebar.json(st.session_state.history)



import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Bot Tester", page_icon="💬")
st.title("💬 Bot Tester")

# ---------- sidebar ----------
with st.sidebar:
    api_url = st.text_input("API URL", os.getenv("API_URL", "http://localhost:8000/chat"))
    api_key = st.text_input("API Key", os.getenv("API_KEY", ""), type="password")
    if st.button("Clear chat"):
        st.session_state.history = []
        st.rerun()
    show_debug = st.checkbox("Show history payload")

# ---------- state ----------
if "history" not in st.session_state:
    st.session_state.history = []  # [{"role": "user"|"ai", "text": str}]

# ---------- render past messages ----------
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["text"])

# ---------- handle new input ----------
if prompt := st.chat_input("Type a message..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("Enter an API key in the sidebar (or set API_KEY in .env).")
        else:
            with st.spinner("Thinking..."):
                try:
                    r = requests.post(
                        api_url,
                        json={"message": prompt, "history": st.session_state.history},
                        headers={"X-API-Key": api_key},
                        timeout=60,
                    )
                    if r.status_code in (401, 403):
                        st.error("Invalid or missing API key.")
                    else:
                        r.raise_for_status()
                        data = r.json()
                        st.markdown(data["reply"])
                        st.session_state.history = data["history"]
                except Exception as e:
                    st.error(f"Error: {e}")

if show_debug:
    st.sidebar.json(st.session_state.history)