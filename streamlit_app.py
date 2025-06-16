import streamlit as st
from openai import OpenAI
import os

# --- CÁC HÀM HỖ TRỢ ---
def rfile(name_file):
    """Hàm đọc nội dung từ file văn bản một cách an toàn."""
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file `{name_file}`. Vui lòng đảm bảo file này tồn tại.")
        return "" # Trả về chuỗi rỗng nếu file không tồn tại

# --- KIỂM TRA VÀ KHỞI TẠO API KEY ---
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Chưa tìm thấy OpenAI API Key. Vui lòng thêm key vào Streamlit Secrets với tên `OPENAI_API_KEY`.")
    st.stop() # Dừng ứng dụng nếu không có key

# Khởi tạo OpenAI client một lần duy nhất
client = OpenAI(api_key=openai_api_key)

# --- GIAO DIỆN NGƯỜI DÙNG ---
# Hiển thị logo (nếu có)
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)

# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
    unsafe_allow_html=True
)

# --- LOGIC CHATBOT ---

# Khởi tạo session state để lưu trữ tin nhắn
if "messages" not in st.session_state:
    # Tải nội dung từ các file cấu hình. AI sẽ hoạt động dựa trên các file này.
    # Bạn chỉ cần chỉnh sửa file .txt để thay đổi hành vi của AI.
    system_prompt = rfile("01.system_trainning.txt")
    assistant_greeting = rfile("02.assistant.txt")
    
    # Chỉ khởi tạo nếu cả hai file đều có nội dung
    if system_prompt and assistant_greeting:
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": assistant_greeting}
        ]
    else:
        st.session_state.messages = []


# Hiển thị các tin nhắn đã có trong lịch sử (bỏ qua tin nhắn "system")
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Xử lý khi người dùng nhập tin nhắn mới
if prompt := st.chat_input("Nhập nội dung bạn cần tư vấn..."):
    # Thêm tin nhắn của người dùng vào lịch sử và hiển thị nó
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Tạo và hiển thị phản hồi từ AI với hiệu ứng streaming
    with st.chat_message("assistant"):
        try:
            # Lấy tên model từ file cấu hình
            model_name = rfile("module_chatgpt.txt").strip()
            if not model_name:
                st.error("Lỗi: Không tìm thấy tên model trong file `module_chatgpt.txt`.")
                st.stop()

            # Gọi API OpenAI và stream phản hồi
            stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            # Dùng write_stream để hiển thị nội dung trả về theo thời gian thực
            response = st.write_stream(stream)
            
            # Lưu lại toàn bộ phản hồi của AI vào lịch sử
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Đã có lỗi xảy ra khi kết nối tới OpenAI: {e}")