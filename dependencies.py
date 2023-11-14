from fastapi import Request

async def get_current_user(request: Request) -> None:
	uid = request.headers.get('uid')
	if uid == None:
		return None
	user = {'uid': uid, 'name': 'zzy'}
	return user