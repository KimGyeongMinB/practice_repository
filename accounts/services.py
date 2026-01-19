from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed

MAX_ATTEMPTS = 5 
BLOCK_TTL = 600 # 10분

# 로그인 횟수 제한
# 5회 틀릴경우 10분 차단
def login_fail(request):
    # 유저의 정보 불러오기
    email = request.data.get("email")
    
    # 로그인 실패 key
    login_block_key = f"login_fail:{email}"
    if login_block_key:
        login_block_count = cache.get(login_block_key, 0) + 1
        print(login_block_count)
    cache.set(login_block_key, login_block_count, BLOCK_TTL)

    # 5회 틀릴시 block 으로 캐시 저장
    if login_block_count >= MAX_ATTEMPTS:
        cache.set(f"login_block:{email}", True, timeout=BLOCK_TTL)

# 로그인 성공시 캐시 삭제
def clear_login_block_cache(email):
    cache.delete(f"login_fail:{email}")
    cache.delete(f"login_block:{email}")

def login_block(request):
    email = request.data.get("email")
    login_block_count = cache.get(f"login_block:{email}")
    
    if login_block_count == True:
        raise AuthenticationFailed("로그인이 잠시 차단되었습니다.")
