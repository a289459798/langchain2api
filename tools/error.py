from fastapi import HTTPException, status

def NoFound(msg: str = '数据不存在'):
	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

def Abort(code: status, msg: str = '数据不存在'):
	raise HTTPException(status_code=code, detail=msg)