from fastapi import Request, HTTPException


class SessionSchema:
    KEY = 'session_id'

    def __init__(self, auto_error: bool = True):
        self.auto_error = auto_error

    def __call__(self, request: Request) -> str | None:
        session_id = request.cookies.get(self.KEY)

        if not session_id:
            if self.auto_error:
                raise HTTPException(status_code=404, detail="Session not found")
            else:
                return None
        return session_id
