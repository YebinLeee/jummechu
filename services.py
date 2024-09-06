import requests
import json
import math
from bs4 import BeautifulSoup

class NaverAPI:
    BASE_URL = 'https://openapi.naver.com/v1/search/'
    BLOG_URL = BASE_URL + 'blog'
    LOCAL_URL = BASE_URL + 'local'
    BLOG_BASE_URL = 'https://blog.naver.com'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def _get_headers(self):
        return {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret,
            'Content-Type': 'application/json'
        }

    def _make_request(self, url, params):
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making request: {e}")
            return None

    def search_blog_posts(self, query, display=3, start=1):
        params = {'query': query, 'display': display, 'start': start}
        data = self._make_request(self.BLOG_URL, params)
        
        if not data or 'items' not in data:
            return None

        cleaned_texts = []
        for item in data['items']:
            cleaned_text = self._extract_blog_content(item['link'])
            if cleaned_text:
                cleaned_texts.append(cleaned_text)

        return {
            'blog_link': item['link'],
            'blogger_name': item['bloggername'],
            'blog_title': self._clean_title(item['title']),
            'blog_text': cleaned_texts
        }

    def search_local(self, query, display=3, start=1):
        params = {'query': query, 'display': display, 'start': start}
        return self._make_request(self.LOCAL_URL, params)

    def _extract_blog_content(self, link):
        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            iframe_tag = soup.find('iframe', id='mainFrame')
            
            if iframe_tag and 'src' in iframe_tag.attrs:
                iframe_url = self.BLOG_BASE_URL + iframe_tag['src']
                iframe_response = requests.get(iframe_url)
                iframe_response.raise_for_status()
                return self._parse_blog_text(iframe_response.text)
        except requests.RequestException as e:
            print(f"Error extracting blog content: {e}")
        return None

    def _parse_blog_text(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        path_content = soup.find('div', class_='se-main-container')
        if path_content:
            return ' '.join(path_content.get_text(strip=True).split())
        return None

    @staticmethod
    def _clean_title(title):
        return title.replace('<b>', '').replace('</b>', '')

        
class CompletionExecutor:
    def __init__(self):
        self._host = CLOVA_HOST
        self._api_key = CLOVA_API_KEY
        self._api_key_primary_val = CLOVA_API_KEY_PRIMARY
        self._request_id = CLOVA_REQUEST_ID

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        summary_array = []

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001', headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if '"result":"OK"' in line.decode("utf-8"):
                    hcx_data = line.decode("utf-8")
                    data = hcx_data[5:]
                    json_data = json.loads(data)
                    summary_data = json_data['message']['content']
                    summary_array.append(summary_data)

        return summary_array

def get_naver_api():
    return NaverAPI(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)

def get_completion_executor():
    return CompletionExecutor(CLOVA_HOST, CLOVA_API_KEY, CLOVA_API_KEY_PRIMARY, CLOVA_REQUEST_ID)


# Constants for KATEC to WGS84 conversion
EARTH_RADIUS = 6371.00877  # Earth radius in km
GRID_SIZE = 5.0  # Grid size in km
PROJECTION_LAT1, PROJECTION_LAT2 = 30.0, 60.0  # Projection latitudes in degrees
ORIGIN_LON, ORIGIN_LAT = 126.0, 38.0  # Origin longitude and latitude in degrees
ORIGIN_X, ORIGIN_Y = 43, 136  # Origin X and Y coordinates in grid units


def convert_KATEC_to_WGS84(mapx: float, mapy: float) -> Tuple[float, float]:
    """
    Convert KATEC coordinates to WGS84 latitude and longitude.

    Args:
        mapx (float): KATEC X coordinate
        mapy (float): KATEC Y coordinate

    Returns:
        Tuple[float, float]: WGS84 latitude and longitude
    """
    try:
        mapx, mapy = float(mapx), float(mapy)
    except ValueError:
        raise ValueError("Invalid input: mapx and mapy must be convertible to float")

    re = EARTH_RADIUS / GRID_SIZE
    slat1, slat2 = math.radians(PROJECTION_LAT1), math.radians(PROJECTION_LAT2)
    olon, olat = math.radians(ORIGIN_LON), math.radians(ORIGIN_LAT)

    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5))
    sf = math.pow(math.tan(math.pi * 0.25 + slat1 * 0.5), sn) * math.cos(slat1) / sn

    ro = re * sf / math.pow(math.tan(math.pi * 0.25 + olat * 0.5), sn)

    xn, yn = mapx - ORIGIN_X, ro - mapy + ORIGIN_Y
    ra = math.sqrt(xn * xn + yn * yn)
    ra = -ra if sn < 0.0 else ra

    alat = 2.0 * math.atan(math.pow((re * sf / ra), (1.0 / sn))) - math.pi * 0.5
    theta = math.atan2(xn, yn) if abs(yn) > 0.0 else (0.0 if abs(xn) <= 0.0 else (math.pi * 0.5 if xn > 0 else -math.pi * 0.5))

    alon = theta / sn + olon
    lat, lon = math.degrees(alat), math.degrees(alon)

    return lat, lon

def scale_down_coordinates(mapx: int, mapy: int) -> Tuple[float, float]:
    """
    Scale down coordinates assuming they are scaled up by 10^7.

    Args:
        mapx (int): Scaled up X coordinate
        mapy (int): Scaled up Y coordinate

    Returns:
        Tuple[float, float]: Scaled down latitude and longitude
    """
    scale_factor = 1e7
    try:
        latitude = float(mapy) / scale_factor
        longitude = float(mapx) / scale_factor
    except ValueError:
        raise ValueError("Invalid input: mapx and mapy must be convertible to float")

    return latitude, longitud

# 카텍 좌표계 -> WSG84 좌표계 변환
def previous_convert_KATEC_to_WGS84(mapx, mapy):
    # Convert mapx and mapy to float
    mapx = float(mapx)
    mapy = float(mapy)
    print(mapx, mapy)

    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    rs = {}
    
    xn = mapx - XO
    yn = ro - mapy + YO
    ra = math.sqrt(xn * xn + yn * yn)
    if sn < 0.0:
        ra = -ra
    alat = math.pow((re * sf / ra), (1.0 / sn))
    alat = 2.0 * math.atan(alat) - math.pi * 0.5

    if abs(xn) <= 0.0:
        theta = 0.0
    else:
        if abs(yn) <= 0.0:
            theta = math.pi * 0.5
            if xn < 0.0:
                theta = -theta
        else:
            theta = math.atan2(xn, yn)

    alon = theta / sn + olon
    rs['lat'] = alat * RADDEG
    rs['lng'] = alon * RADDEG

    print(rs['lat'], rs['lng'])

    return rs['lat'], rs['lng']

def previous_scale_down_coordinates(mapx, mapy):
    # Assuming the coordinates are scaled up by 10^7
    scale_factor = 10**7

    # Convert the integers to float and scale them down
    latitude = float(mapy) / scale_factor
    longitude = float(mapx) / scale_factor

    return latitude, longitude

