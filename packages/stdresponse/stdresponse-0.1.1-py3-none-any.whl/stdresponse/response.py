import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List, Union

class StandardResponse:
    @staticmethod
    def _get_timestamp() -> str:
        return datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def _get_request_id(request_id: Optional[str]) -> str:
        return request_id if request_id else str(uuid.uuid4())

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Request successful.",
        status_code: int = 200,
        request_id: Optional[str] = None,
        meta : Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:

        _meta = {
                "timestamp": StandardResponse._get_timestamp(),
                "requestId": StandardResponse._get_request_id(request_id)
            }
        if meta:
            _meta.extend(meta)
            
        return {
            "success": True,
            "status_code": status_code,
            "message": message,
            "data": data,
            "error": None,
            "meta": _meta
        }

    @staticmethod
    def error(
        message: str = "An error occurred.",
        status_code: int = 400,
        error_type: Optional[str] = None,
        error_details: Optional[List[Dict[str, str]]] = None,
        request_id: Optional[str] = None,
        meta : Optional[Dict[str,str]] = None
    ) -> Dict[str, Any]:

        _meta = {
                "timestamp": StandardResponse._get_timestamp(),
                "requestId": StandardResponse._get_request_id(request_id)
            }
        if meta:
            _meta.extend(meta)

        return {
            "success": False,
            "status_code": status_code,
            "message": message,
            "data": None,
            "error": {
                "type": error_type or "GENERAL_ERROR",
                "details": error_details or []
            },
            "meta" : _meta
        }