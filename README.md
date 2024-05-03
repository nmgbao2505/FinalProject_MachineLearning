# FinalProject_MachineLearning

- Tên chức năng: Xử lý hình ảnh và Tạo câu chuyện
    - Mô tả chức năng: Sau khi đăng tải hình ảnh lên trang web, tôi sẽ cho bạn 1 câu có thể gọi là tiêu đề để tóm tắt nội dung của hình ảnh được đăng tải. Kèm theo đó là lựa chọn có thể xem câu tiêu đề ấy bằng tiếng anh. Bên cạnh đó, dựa vào tiêu đề, tôi có thể phát triển ra 1 câu chuyện nhỏ để mô tả rõ hơn về hình ảnh. Cuối cùng là tính năng có thể phát hiện các object có trên bức hình.
    - Tên file chạy chức năng: app.py









- MBart là một mô hình máy học dựa trên kiến trúc Transformer, được đào tạo để xử lý nhiều ngôn ngữ cùng một lúc. Nó được huấn luyện với một loạt các ngôn ngữ và có khả năng dịch một câu từ một ngôn ngữ nguồn sang một ngôn ngữ đích mà không cần thông tin về cặp ngôn ngữ cụ thể. Trong model đã sử dụng để dịch văn bản từ tiếng Anh sang tiếng Việt.
- LangChain là một thư viện Python được tạo ra để tạo ra các câu chuyện hoặc văn bản mới dựa trên các kịch bản cụ thể. Nó sử dụng các mô hình ngôn ngữ để dự đoán và tạo ra các đoạn văn bản mới dựa trên các kịch bản được cung cấp.
- Sử dụng HuggingFace Hub để tải xuống một mô hình ngôn ngữ đã được đào tạo và sử dụng nó để tạo ra câu chuyện từ các kịch bản đã cho.
- Sử dụng mô hình "Salesforce/blip-image-captioning-base" chuyển đổi hình ảnh thành văn bản.
- DetrImageProcessor là một lớp trong transformers dùng để xử lý ảnh trước khi đưa vào mô hình DETR. Nó cung cấp các phương thức để chuyển đổi ảnh thành dạng mà mô hình DETR có thể chấp nhận, bao gồm việc chuẩn hóa ảnh và chuyển đổi ảnh thành tensor. 
- DetrForObjectDetection là một lớp trong transformers dùng để tải và sử dụng mô hình DETR cho nhiệm vụ phát hiện đối tượng. Lớp này cung cấp các phương thức để tải mô hình DETR đã được huấn luyện từ thư viện Hugging Face và sử dụng nó để phát hiện các đối tượng trong ảnh. Nó cũng cung cấp các phương thức để thực hiện xử lý kết quả phát hiện, chẳng hạn như chuyển đổi đầu ra của mô hình thành đối tượng có thể đọc được dễ dàng hơn.