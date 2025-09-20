
from __future__ import annotations

import os
import sys
import time
import functools
import inspect
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, Optional

try:
    # Prefer package-local native module
    from . import handit_core_native as _native  # type: ignore
except Exception:
    try:
        # Fallback to top-level module name if installed globally
        import handit_core_native as _native  # type: ignore
    except Exception:  # pragma: no cover - not built yet
        _native = None  # type: ignore


def version() -> str:
    return "1.0.11"  # synced with pyproject.toml


# Async-friendly session state
_active_session_id: ContextVar[Optional[str]] = ContextVar("handit_active_session_id", default=None)

# Global config (merged from env + user)
_config: Dict[str, Any] = {}


def _merge_env_config(user_cfg: Dict[str, Any]) -> Dict[str, Any]:
    env_map = {
        "HANDIT_ENDPOINT": "https://handit-api-oss-299768392189.us-central1.run.app/api/ingest/events",
        "HANDIT_API_KEY": os.getenv("HANDIT_API_KEY"),
        "HANDIT_SAMPLE_RATE": os.getenv("HANDIT_SAMPLE_RATE"),
        "HANDIT_CAPTURE": os.getenv("HANDIT_CAPTURE"),
        "HANDIT_MAX_STR": os.getenv("HANDIT_MAX_STR"),
        "HANDIT_MAX_LOCALS": os.getenv("HANDIT_MAX_LOCALS"),
        "HANDIT_INCLUDE": os.getenv("HANDIT_INCLUDE"),
        "HANDIT_EXCLUDE": os.getenv("HANDIT_EXCLUDE"),
        "HANDIT_REDACT": os.getenv("HANDIT_REDACT"),
        "HANDIT_OTEL": os.getenv("HANDIT_OTEL"),
        "HANDIT_SPOOL_DIR": os.getenv("HANDIT_SPOOL_DIR"),
    }
    merged = {k: v for k, v in env_map.items() if v is not None}
    merged.update(user_cfg)
    return merged


def configure(**kwargs: Any) -> None:
    global _config
    cfg = _merge_env_config(kwargs)
    # Minimal validation
    if "HANDIT_ENDPOINT" in cfg and not isinstance(cfg["HANDIT_ENDPOINT"], str):
        raise ValueError("HANDIT_ENDPOINT must be a string")
    # Coerce numeric caps
    if "HANDIT_MAX_STR" in cfg:
        cfg["HANDIT_MAX_STR"] = int(cfg["HANDIT_MAX_STR"])
    if "HANDIT_MAX_LOCALS" in cfg:
        cfg["HANDIT_MAX_LOCALS"] = int(cfg["HANDIT_MAX_LOCALS"])
    # Propagate HANDIT_* settings into process environment before native Lazy reads them
    for k, v in list(cfg.items()):
        if k.startswith("HANDIT_") and v is not None:
            os.environ[k] = str(v)
    _config = cfg
    
    # Try to patch LangChain models when configure is called
    _auto_patch_on_configure()
    
    # Enable HTTP instrumentation by default
    try:
        from .http_instrumentation import patch_requests, patch_httpx, patch_aiohttp
        patch_requests(); patch_httpx(); patch_aiohttp()
    except Exception as e:
        pass
    
    # Enable Bedrock instrumentation by default
    try:
        from .bedrock_instrumentation import patch_bedrock
        patch_bedrock()
    except Exception as e:
        pass
    
    # Push API settings to native exporter if provided
    try:
        endpoint = cfg.get("HANDIT_ENDPOINT")
        api_key = cfg.get("HANDIT_API_KEY")
        if _native is not None and (endpoint is not None or api_key is not None):
            set_http = getattr(_native, "set_http_config_py", None)
            if callable(set_http):
                set_http(endpoint, api_key)
    except Exception:
        pass


@contextmanager
def session(tag: Optional[str] = None, capture: Optional[str] = None, traceparent: Optional[str] = None, attrs: Optional[Dict[str, str]] = None):
    attrs = attrs or {}
    # Start session via native module and activate native profiler
    if _native is None:
        raise RuntimeError("handit_core native extension not built")
    session_id = _native.start_session_py(tag, attrs, traceparent, None)
    token = _active_session_id.set(session_id)
    _native.start_profiler_py(session_id)
    try:
        yield
    finally:
        try:
            _native.stop_profiler_py()
            _active_session_id.reset(token)
        except Exception:
            # Don't let cleanup errors block execution
            pass


def entrypoint(tag: Optional[str] = None, capture: Optional[str] = None, attrs: Optional[Dict[str, str]] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        # Use functools.wraps but handle forward references from __future__ annotations
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrapper(*args: Any, **kwargs: Any):
                with session(tag=tag, capture=capture, attrs=attrs):
                    result = await fn(*args, **kwargs)
                    return result
            
            # Critical: Preserve signature and resolve forward references for FastAPI
            try:
                # Get the original signature
                original_sig = inspect.signature(fn)
                
                # Try to resolve forward references if __future__ annotations is used
                if hasattr(fn, '__annotations__'):
                    try:
                        # Use typing.get_type_hints to properly resolve forward references
                        import typing
                        fn_module = inspect.getmodule(fn)
                        
                        # get_type_hints resolves ForwardRef automatically
                        resolved_annotations = typing.get_type_hints(fn, globalns=getattr(fn_module, '__dict__', {}) if fn_module else {})
                        awrapper.__annotations__ = resolved_annotations
                    except Exception:
                        # Fallback: keep original annotations
                        awrapper.__annotations__ = getattr(fn, '__annotations__', {})
                
                # Preserve the exact signature
                awrapper.__signature__ = original_sig
                
            except Exception:
                # Fallback: just preserve what we can
                awrapper.__signature__ = inspect.signature(fn)
            
            return awrapper
        else:
            @functools.wraps(fn)
            def wrapper(*args: Any, **kwargs: Any):
                with session(tag=tag, capture=capture, attrs=attrs):
                    return fn(*args, **kwargs)
            
            # Same forward reference resolution for sync functions
            try:
                original_sig = inspect.signature(fn)
                
                if hasattr(fn, '__annotations__'):
                    try:
                        # Use typing.get_type_hints to properly resolve forward references
                        import typing
                        fn_module = inspect.getmodule(fn)
                        
                        # get_type_hints resolves ForwardRef automatically
                        resolved_annotations = typing.get_type_hints(fn, globalns=getattr(fn_module, '__dict__', {}) if fn_module else {})
                        wrapper.__annotations__ = resolved_annotations
                    except Exception:
                        # Fallback: keep original annotations
                        wrapper.__annotations__ = getattr(fn, '__annotations__', {})
                
                wrapper.__signature__ = original_sig
                
            except Exception:
                wrapper.__signature__ = inspect.signature(fn)
            
            return wrapper
    return decorator


# Minimal public API for manual calls from Python for early testing
if _native is not None:
    start_session = _native.start_session_py
    on_call = _native.on_call_py
    on_return = _native.on_return_py
    on_exception = _native.on_exception_py
else:
    def start_session(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_call(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_return(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_exception(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")


# Auto-enable HTTP instrumentation on import for zero-config usage
try:
    from .http_instrumentation import patch_requests, patch_httpx, patch_aiohttp
    patch_requests(); patch_httpx(); patch_aiohttp()
except Exception:
    pass

# Auto-enable OpenAI instrumentation
try:
    from .openai_instrumentation import patch_openai
    patch_openai()
except Exception:
    pass

# Auto-enable Bedrock instrumentation
try:
    from .bedrock_instrumentation import patch_bedrock
    patch_bedrock()
except Exception:
    pass

# Simple direct patching approach - patch after first use
import atexit

def _try_patch_langchain():
    """Try to patch LangChain models if they're available"""
    try:
        # Try to patch ChatOpenAI if it's already imported
        import sys
        if 'langchain_openai' in sys.modules:
            from langchain_openai import ChatOpenAI
            if not hasattr(ChatOpenAI, '_handit_patched'):
                _patch_chatopenai_direct(ChatOpenAI)
        
        # Try to patch other models
        if 'langchain_anthropic' in sys.modules:
            from langchain_anthropic import ChatAnthropic
            if not hasattr(ChatAnthropic, '_handit_patched'):
                _patch_chatanthropic_direct(ChatAnthropic)
        
        # Try to patch Bedrock models
        if 'langchain_aws' in sys.modules:
            from langchain_aws import ChatBedrock
            if not hasattr(ChatBedrock, '_handit_patched'):
                _patch_chatbedrock_direct(ChatBedrock)
                
    except Exception:
        pass

def _patch_chatopenai_direct(ChatOpenAI):
    """Direct patching of ChatOpenAI"""
    try:
        original_ainvoke = ChatOpenAI.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            # Check for active session
            try:
                import handit_core.handit_core_native as native
                session_id = native.get_active_session_id_py()
                if not session_id:
                    return await original_ainvoke(self, input, config, **kwargs)
            except:
                return await original_ainvoke(self, input, config, **kwargs)
            
            # Extract info
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'gpt-3.5-turbo'))
            
            import time, json
            t0_ns = time.time_ns()
            
            # Log call
            try:
                input_str = str(input) if input else ""
                args_preview = {"model": model_name, "input": input_str}
                native.on_call_with_args_py(session_id, "ChatOpenAI.ainvoke", "langchain_openai", "<langchain>", 1, t0_ns, json.dumps(args_preview))
            except:
                pass
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                
                # Log return
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    response_content = result.content if hasattr(result, 'content') and result.content else str(result)
                    return_preview = {"return": response_content}
                    native.on_return_with_preview_py(session_id, "ChatOpenAI.ainvoke", t1_ns, dt_ns, json.dumps(return_preview))
                except:
                    pass
                
                return result
            except Exception as error:
                # Log error
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    error_preview = {"return": f"Error: {str(error)}"}
                    native.on_return_with_preview_py(session_id, "ChatOpenAI.ainvoke", t1_ns, dt_ns, json.dumps(error_preview))
                except:
                    pass
                raise
        
        ChatOpenAI.ainvoke = traced_ainvoke
        ChatOpenAI._handit_patched = True
        
    except Exception as e:
        pass

def _patch_chatanthropic_direct(ChatAnthropic):
    """Direct patching of ChatAnthropic"""
    # Similar implementation for Anthropic
    pass

def _patch_chatbedrock_direct(ChatBedrock):
    """Direct patching of ChatBedrock"""
    try:
        original_ainvoke = ChatBedrock.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            # Check for active session
            try:
                import handit_core.handit_core_native as native
                session_id = native.get_active_session_id_py()
                if not session_id:
                    return await original_ainvoke(self, input, config, **kwargs)
            except:
                return await original_ainvoke(self, input, config, **kwargs)
            
            # Extract info
            model_id = getattr(self, 'model_id', getattr(self, 'model', 'anthropic.claude-3-sonnet-20240229-v1:0'))
            
            import time, json
            t0_ns = time.time_ns()
            
            # Log call
            try:
                input_str = str(input) if input else ""
                args_preview = {"model_id": model_id, "input": input_str}
                native.on_call_with_args_py(session_id, "ChatBedrock.ainvoke", "langchain_aws", "<langchain-bedrock>", 1, t0_ns, json.dumps(args_preview))
            except:
                pass
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                
                # Log return
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    response_content = result.content if hasattr(result, 'content') and result.content else str(result)
                    return_preview = {"return": response_content}
                    native.on_return_with_preview_py(session_id, "ChatBedrock.ainvoke", t1_ns, dt_ns, json.dumps(return_preview))
                except:
                    pass
                
                return result
            except Exception as error:
                # Log error
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    error_preview = {"return": f"Error: {str(error)}"}
                    native.on_return_with_preview_py(session_id, "ChatBedrock.ainvoke", t1_ns, dt_ns, json.dumps(error_preview))
                except:
                    pass
                raise
        
        ChatBedrock.ainvoke = traced_ainvoke
        ChatBedrock._handit_patched = True
        
    except Exception as e:
        pass

# Try patching immediately and on configure
def _auto_patch_on_configure():
    """Auto-patch when configure is called"""
    _try_patch_langchain()

# Also try patching immediately on module load
_try_patch_langchain()

# Enable HTTP instrumentation immediately on import (not just on configure)
try:
    from .http_instrumentation import patch_requests, patch_httpx, patch_aiohttp
    patch_requests(); patch_httpx(); patch_aiohttp()
except Exception as e:
    pass

# Write all buffered events to file at process exit, if enabled
try:
    import atexit
    def _flush_at_exit() -> None:
        try:
            # Only write to file if explicitly enabled via environment variable
            if os.getenv("HANDIT_OUTPUT_FILE") and _native is not None:
                flush = getattr(_native, "flush_events_to_file", None)
                if callable(flush):
                    path = os.getenv("HANDIT_OUTPUT_FILE")
                    flush(path)
        except Exception:
            pass
    atexit.register(_flush_at_exit)
except Exception:
    pass

