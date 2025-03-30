import streamlit as st
import auth_functions
from streamlit_chat import message
import random
import time
import cozepy
import os
import json
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType, COZE_CN_BASE_URL  # noqa

# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming


## -------------------------------------------------------------------------------------------------
## Not logged in -----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
if 'user_info' not in st.session_state:
    col1,col2,col3 = st.columns([1,2,1])

    # Authentication form layout
    do_you_have_an_account = col2.selectbox(label='是否有账号？',options=('是','否','忘记密码？'))
    auth_form = col2.form(key='Authentication form',clear_on_submit=False)
    email = auth_form.text_input(label='邮箱')
    password = auth_form.text_input(label='密码',type='password') if do_you_have_an_account in {'是','否'} else auth_form.empty()
    auth_notification = col2.empty()

    # Sign In
    if do_you_have_an_account == '是' and auth_form.form_submit_button(label='登录',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('登录中'):
            auth_functions.sign_in(email,password)

    # Create Account
    elif do_you_have_an_account == '否' and auth_form.form_submit_button(label='创建账户',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('创建账户中'):
            auth_functions.create_account(email,password)

    # Password Reset
    elif do_you_have_an_account == '忘记密码？' and auth_form.form_submit_button(label='发送重置密码邮件到邮箱',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('发送重置密码链接中'):
            auth_functions.reset_password(email)

    # Authentication success and warning messages
    if 'auth_success' in st.session_state:
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success
    elif 'auth_warning' in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning

## -------------------------------------------------------------------------------------------------
## Logged in --------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
else:
    ## config coze token from config
    coze_api_token = "{0}".format(st.secrets['COZE_API_TOKEN'])
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

    # create bot
    bot_id = '7483399402716643367'
    user_id = '123'

    st.set_page_config(page_title="路霸 AI: A股金融专家")
    with st.sidebar:
        st.title('路霸 AI')
        st.header('User information:')
        st.write(st.session_state.user_info)

        # Sign out
        st.header('登出:')
        st.button(label='登出',on_click=auth_functions.sign_out,type='primary')

        # Delete Account
        st.header('删除账户:')
        password = st.text_input(label='确认密码',type='password')
        st.button(label='删除账户',on_click=auth_functions.delete_account,args=[password],type='primary')

    # Function for generating LLM response
    def generate_response(input):
        thinking = ""  # 记录思考过程
        response = ""  # 记录最终回复
        response_placeholder = st.empty()  # 创建回复占位符
        
        # 添加静态思考标题
        with st.expander("🧠 思考中", expanded=True):
            thinking_placeholder = st.empty()
        
        with st.expander("📉 用量统计", expanded=True):
            usage_placeholder = st.empty()
        
        # 流式处理消息
        for event in coze.chat.stream(
            bot_id=bot_id, 
            user_id=user_id, 
            additional_messages=[Message.build_user_question_text(input)]
        ):  
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA: 
                jsonStr = json.dumps(event.message, default=lambda o: o.__dict__, indent=4)
                msgJson = json.loads(jsonStr)
                if msgJson['reasoning_content']:
                    content = msgJson['reasoning_content']
                    thinking += str(content)
                    thinking_placeholder.markdown(f"```\n{thinking}\n```")
                elif event.message.content != None:
                    content = event.message.content           
                    response += content
                    # 流式输出效果
                    response_placeholder.code(response + "▌")
            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                # response_placeholder.markdown(response + "▌")
                response += "\n所有回答均来自 AI，回答仅供参考，不构成任何投资建议\n"
                response_placeholder.code(response + "▌")

                

                content  = "Token 使用量: " + str(event.chat.usage.token_count) + "\n"
                usage_placeholder.markdown(content + "▌")

        
        # 最终渲染完整回复            
        response_placeholder.code(response)
        return response  # 返回完整回复供消息记录

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "欢迎使用路霸AI，我是A股金融专家，尝试问问我关于A股股票投资相关的问题吧"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User-provided prompt
    if input := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": input})
        with st.chat_message("user"):
            st.write(input)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("正在生成回答.."):
                response = generate_response(input) 

                # st.write(response) 
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
