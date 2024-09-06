import os
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
CLOVA_HOST = os.getenv('CLOVA_HOST')
CLOVA_API_KEY = os.getenv('CLOVA_API_KEY')
CLOVA_API_KEY_PRIMARY = os.getenv('CLOVA_API_KEY_PRIMARY')
CLOVA_REQUEST_ID = os.getenv('CLOVA_REQUEST_ID')


def process_search_results(result_json, naver):
    result_response = []
    for item in result_json['items']:
        item_data = extract_item_data(item)
        blog_result = naver.search_blog_posts(item_data['title'], 1)
        if blog_result:
            item_data['blog'] = process_blog_result(blog_result)
        result_response.append(item_data)
    return result_response

def extract_item_data(item):
    mapx, mapy = scale_down_coordinates(item['mapx'], item['mapy'])
    return {
        "title": item['title'],
        "category": item['category'],
        "mapx": mapx,
        "mapy": mapy,
        "phone": item['telephone'],
        "address": item['address'],
        "link": item['link']
    }

def process_blog_result(blog_result):
    summaries = []
    for cleaned_text in blog_result['blog_text']:
        summary = get_text_summary(cleaned_text)
        summaries.append(summary)
    return {
        "title": blog_result['title'],
        "author": blog_result['blogger_name'],
        "link": blog_result['blog_link'],
        "review_summary": summaries
    }

def get_text_summary(cleaned_text):
    preset_text = [
        {"role": "system", "content": "블로그 글을 입력받아 5문장으로 요약해주는 시스템"},
        {"role": "user", "content": cleaned_text}
    ]
    request_data = {
        'messages': preset_text,
        'topP': 0.9,
        'topK': 50,
        'maxTokens': 256,
        'temperature': 0.7,
        'repeatPenalty': 1.0,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }
    completion_executor = get_completion_executor()
    summary = completion_executor.execute(request_data)
    return ''.join(line.replace('\n', '') for line in summary)

def process_blog_posts(cleaned_texts, topP, topK, maxTokens, temperature, repeatPenalty):
    summaries = []
    if cleaned_texts:
        for cleaned_text in cleaned_texts:
            summary = get_text_summary_with_params(cleaned_text, topP, topK, maxTokens, temperature, repeatPenalty)
            summaries.append(summary)
    return summaries

def get_text_summary_with_params(cleaned_text, topP, topK, maxTokens, temperature, repeatPenalty):
    preset_text = [
        {"role": "system", "content": "블로그 글을 입력받아 요약해주는 시스템"},
        {"role": "user", "content": cleaned_text}
    ]
    request_data = {
        'messages': preset_text,
        'topP': topP,
        'topK': topK,
        'maxTokens': maxTokens,
        'temperature': temperature,
        'repeatPenalty': repeatPenalty,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }
    completion_executor = get_completion_executor()
    return completion_executor.execute(request_data)

