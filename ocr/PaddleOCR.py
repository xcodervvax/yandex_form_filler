# https://huggingface.co/PaddlePaddle/en_PP-OCRv5_mobile_rec

from paddleocr import PaddleOCR  

ocr = PaddleOCR(
    text_recognition_model_name="en_PP-OCRv5_mobile_rec",
    use_doc_orientation_classify=False, # Use use_doc_orientation_classify to enable/disable document orientation classification model
    use_doc_unwarping=False, # Use use_doc_unwarping to enable/disable document unwarping module
    use_textline_orientation=True, # Use use_textline_orientation to enable/disable textline orientation classification model
    device="gpu:0", # Use device to specify GPU for model inference
)
# result = ocr.predict("https://cdn-uploads.huggingface.co/production/uploads/681c1ecd9539bdde5ae1733c/6KQKOS42DKVEUnrticvhd.png")
result = ocr.predict("router.jpeg")
for res in result:  
    res.print()  
    res.save_to_img("output")  
    res.save_to_json("output")
