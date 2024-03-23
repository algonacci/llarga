import streamlit as stimport hmacimport pandas as pdimport sysimport gcimport timefrom helper.modelling import initialize# session intializationif 'model' in globals():    model.close_connection()    del model.llm    del model    gc.collect()# passworddef check_password():    """Returns `True` if the user had the correct password."""    global user    def password_entered():        """Checks whether a password entered by the user is correct."""        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):            st.session_state["password_correct"] = True            del st.session_state["password"]  # Don't store the password.        else:            st.session_state["password_correct"] = False    # Return True if the password is validated.    if st.session_state.get("password_correct", False):        return True    # user name    def record_user():        f = open("metadata/user.txt", "w")        f.write(st.session_state["user"])        f.close()            st.text_input(        "Your name", type="default", on_change=record_user, key="user"    )    # Show input for password.    st.text_input(        "Password", type="password", on_change=password_entered, key="password"    )    if "password_correct" in st.session_state:        st.error("Password incorrect")    return Falseif not check_password():    st.stop()  # Do not continue if check_password is not True.# app setupst.title("UNCTAD LLM")# Styles sheetswith open( "styles/style.css" ) as css:    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)    user_avatar = "\N{grinning face}" #st.image("styles/assistant_avatar.png")assistant_avatar = "\N{Robot Face}"#st.image("styles/user_avatar.png")# Initialize chat historyif "messages" not in st.session_state:    st.session_state.messages = []# Display chat messages from history on app rerunfor message in st.session_state.messages:    with st.chat_message(message["role"]):        st.markdown(message["content"])# LLM set up# parameters/authenticationllm_dict = pd.read_csv("metadata/llm_list.csv")corpora_dict = pd.read_csv("metadata/corpora_list.csv")db_info = pd.read_csv("metadata/db_creds.csv")# model paramssimilarity_top_k = 4n_gpu_layers = 100temperature = 0.0max_new_tokens = 512context_window = 3900chunk_overlap = 200chunk_size = 512memory_limit = 1500system_prompt = ""paragraph_separator = "\n\n\n"separator = " "use_chat_engine = Truereset_chat_engine = Falsedb_name = "vector_db"rerun_populate_db = Falseclear_database = Falsewith st.spinner('Initializing...'):    #st.session_state["model"], st.session_state["which_llm"], st.session_state["which_corpus"] = initialize(    model, which_llm, which_corpus = initialize(        which_llm_local="mistral-docsgpt",        which_corpus_local='oda',        n_gpu_layers=n_gpu_layers,        temperature=temperature,        max_new_tokens=max_new_tokens,        context_window=context_window,        chunk_overlap=chunk_overlap,        chunk_size=chunk_size,        paragraph_separator=paragraph_separator,        separator=separator,        system_prompt=system_prompt,        rerun_populate_db=rerun_populate_db,        clear_database_local=clear_database,        corpora_dict=corpora_dict,        llm_dict=llm_dict,        db_name=db_name,        db_info=db_info,    )# Accept user inputif prompt := st.chat_input(f'Query {which_llm} contextualized on {which_corpus}'):    # Display user message in chat message container    with st.chat_message("user", avatar=user_avatar):        st.markdown(prompt)    # Add user message to chat history    st.session_state.messages.append({"role": "user", "content": prompt})        if prompt.lower() == "reset":        if model.chat_engine is not None:            model.chat_engine.reset()        with st.chat_message("assistant", avatar=assistant_avatar):            st.markdown("Model context reset!")                elif prompt.lower() == "clear":        if 'model' in globals():            if which_corpus is not None:                model.close_connection()            del model.llm            del model            gc.collect()        with st.chat_message("assistant", avatar=assistant_avatar):            st.markdown("Model cleared from memory!")        else:        response = model.gen_response(            st.session_state.messages[-1]["content"].replace("cite your sources", "").replace("Cite your sources", ""),            similarity_top_k=similarity_top_k,            use_chat_engine=use_chat_engine,            reset_chat_engine=reset_chat_engine        )        response = response["response"]        # Display assistant response in chat message container        with st.chat_message("assistant", avatar=assistant_avatar):            st.markdown(response)            #streaming: st.write_stream(response_generator())        # Add assistant response to chat history        st.session_state.messages.append({"role": "assistant", "content": response})