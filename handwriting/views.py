from django.shortcuts import render

# Create your views here.
import base64
import io
from django.http import JsonResponse
from PIL import Image
import openai 

from django.views.decorators.csrf import csrf_exempt
import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
        
@csrf_exempt  # CSRF 인증을 건너뛰기 위해 사용 (개발 환경에서만 사용)
def send_drawing(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')

            if image_data:
                # 이미지 데이터에서 Base64 부분 추출
                image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)

                # 이미지 열기
                image = Image.open(io.BytesIO(image_bytes))

                image.show()

                # 이미지를 임시 파일로 저장
                temp_image_path = 'temp_image.png'
                image.save(temp_image_path)

                # 이미지를 base64로 인코딩
                base64_image = encode_image(temp_image_path)

                # OpenAI API 호출
                response = openai.ChatCompletion.create(
                    model="gpt-4o",  # 사용할 모델 이름
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
                        {"role": "user", "content": [
                            {"type": "text", "text": "이 이미지를 수식으로 변환해줘"},  # 사용자 질문
                            {"type": "image_url", "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"}
                            }
                        ]}
                    ],
                    temperature=0.0,
                )

                # 응답 반환
                latex_result = response.choices[0].message.content
                return JsonResponse({'latex': latex_result})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  # 예외 발생 시 500 오류 반환

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def index(request):
    return render(request, 'index.html')

# # OpenAI API 키 설정 (환경 변수로 설정하는 것이 안전함)
# openai.api_key = 'aaa'  # 여기에 OpenAI API 키를 입력하세요.

@csrf_exempt  # CSRF 예외 처리
def convert_to_latex(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paths = data.get('paths', [])  # 필기 좌표 데이터 받음

        # 필기 좌표를 처리하여 텍스트로 변환하는 과정이 필요할 수 있음
        # 여기서는 단순하게 좌표 데이터 자체를 텍스트로 가정
        handwriting_text = convert_paths_to_text(paths)

        # GPT를 사용해 텍스트를 LaTeX으로 변환
        response = openai.Completion.create(
            model="text-davinci-003",  # 원하는 GPT 모델 선택
            prompt=f"Convert the following handwriting to LaTeX: {handwriting_text}",
            max_tokens=100,
            temperature=0
        )

        latex_result = response.choices[0].text.strip()

        return JsonResponse({'latex': latex_result})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def convert_paths_to_text(paths):
    """
    좌표 데이터를 텍스트로 변환하는 함수.
    이 부분은 실제로는 좌표를 텍스트나 수식으로 변환하는 로직이 필요할 수 있습니다.
    현재는 예시로 좌표 데이터를 단순 문자열로 반환합니다.
    """
    return "This is a sample handwriting text based on paths."