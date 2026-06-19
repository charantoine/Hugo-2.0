"""
LLM client — Mistral self-hosted (Ollama/llama.cpp). CPU-only, no OpenAI.
"""
import json
import logging
from typing import Dict, List, Optional, Tuple
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _stream_single_chunk(text: str):
    clean = (text or "").strip()
    if clean:
        yield clean


def complete_ollama(
    prompt: str,
    system: str = "",
    max_tokens: int = 256,
    messages: Optional[List[dict]] = None,
) -> Tuple[str, Dict]:
    base = getattr(settings, "LLM_BASE_URL", "http://localhost:11434")
    model = getattr(settings, "LLM_MODEL", "mistral")
    url = "%s/api/generate" % base.rstrip("/")
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system or None,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        text = (data.get("response") or "").strip()
        meta = {
            "provider": "ollama",
            "model_used": model,
            "request_payload": payload,
            "raw_response": data,
        }
        return text, meta
    except Exception as e:
        logger.warning("llm_request_failed", extra={"error": str(e)})
        return "", {
            "provider": "ollama",
            "error": str(e),
            "request_payload": payload,
        }

def complete_ovh(
    prompt: str,
    system: str = "",
    max_tokens: int = 256,
    tutor_prompt=None,
    messages: Optional[List[dict]] = None,
) -> Tuple[str, Dict]:
    if not getattr(settings, "ENABLE_EXTERNAL_LLM", False):
        # POC: external LLM désactivé
        logger.warning("llm_external_disabled")
        return "", {"provider": "ovh_ai", "error": "external_llm_disabled"}
    base_url = getattr(settings, "OVH_AI_BASE_URL", "").rstrip("/")
    # Fallback model from settings
    model = getattr(settings, "OVH_AI_MODEL", "")
    # If a TutorPrompt is provided and linked to an OvhLlm, prefer its code
    if tutor_prompt is not None:
        try:
            ovh_llm = getattr(tutor_prompt, "ovh_llm", None)
            ovh_code = getattr(ovh_llm, "code", None) if ovh_llm is not None else None
            if ovh_code:
                model = ovh_code
        except Exception:
            # If anything goes wrong, keep the fallback model from settings
            logger.warning("llm_ovh_model_from_tutorprompt_failed")
    token = getattr(settings, "OVH_AI_TOKEN", "")
    if not base_url or not model or not token:
        logger.warning("llm_ovh_missing_config")
        return "", {
            "provider": "ovh_ai",
            "error": "missing_config",
            "base_url": base_url,
            "model": model,
        }
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if messages is not None:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "messages": messages,
        }
    else:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system or ""},
                {"role": "user", "content": prompt},
            ],
        }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        text = (data.get("choices", [{}])[0].get("message", {}).get("content", "") or "").strip()
        meta = {
            "provider": "ovh_ai",
            "model_used": model,
            "request_payload": payload,
            "raw_response": data,
        }
        return text, meta
    except Exception as e:
        logger.warning("llm_ovh_request_failed", extra={"error": str(e)})
        return "", {
            "provider": "ovh_ai",
            "error": str(e),
            "request_payload": payload,
        }


def stream_ovh(
    prompt: str,
    system: str = "",
    max_tokens: int = 256,
    tutor_prompt=None,
    messages: Optional[List[dict]] = None,
) -> Tuple[object, Dict]:
    if not getattr(settings, "ENABLE_EXTERNAL_LLM", False):
        logger.warning("llm_external_disabled")
        meta = {"provider": "ovh_ai", "error": "external_llm_disabled"}
        meta["full_text"] = ""
        return _stream_single_chunk(""), meta

    base_url = getattr(settings, "OVH_AI_BASE_URL", "").rstrip("/")
    model = getattr(settings, "OVH_AI_MODEL", "")
    if tutor_prompt is not None:
        try:
            ovh_llm = getattr(tutor_prompt, "ovh_llm", None)
            ovh_code = getattr(ovh_llm, "code", None) if ovh_llm is not None else None
            if ovh_code:
                model = ovh_code
        except Exception:
            logger.warning("llm_ovh_model_from_tutorprompt_failed")

    token = getattr(settings, "OVH_AI_TOKEN", "")
    if not base_url or not model or not token:
        logger.warning("llm_ovh_missing_config")
        meta = {
            "provider": "ovh_ai",
            "error": "missing_config",
            "base_url": base_url,
            "model": model,
        }
        meta["full_text"] = ""
        return _stream_single_chunk(""), meta

    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream",
    }
    if messages is not None:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "stream": True,
            "messages": messages,
        }
    else:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "stream": True,
            "messages": [
                {"role": "system", "content": system or ""},
                {"role": "user", "content": prompt},
            ],
        }

    meta = {
        "provider": "ovh_ai",
        "model_used": model,
        "request_payload": payload,
        "raw_response": {"stream": True, "events_count": 0},
        "full_text": "",
    }

    def iterator():
        chunks: List[str] = []
        finish_reason = None
        event_count = 0
        response_id = None
        try:
            with requests.post(url, json=payload, headers=headers, timeout=(30, 300), stream=True) as response:
                response.raise_for_status()
                response.encoding = "utf-8"
                for raw_line in response.iter_lines(decode_unicode=False):
                    if raw_line is None:
                        continue
                    try:
                        line = raw_line.decode("utf-8").strip()
                    except UnicodeDecodeError:
                        line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if not data_str:
                        continue
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    event_count += 1
                    response_id = response_id or data.get("id")
                    choice = (data.get("choices") or [{}])[0]
                    delta = choice.get("delta") or {}
                    chunk = delta.get("content") or ""
                    if chunk:
                        chunks.append(chunk)
                        yield chunk
                    if choice.get("finish_reason"):
                        finish_reason = choice.get("finish_reason")
            meta["full_text"] = "".join(chunks).strip()
            meta["raw_response"] = {
                "stream": True,
                "response_id": response_id,
                "events_count": event_count,
                "finish_reason": finish_reason,
            }
        except Exception as e:
            logger.warning("llm_ovh_stream_failed", extra={"error": str(e)})
            meta["error"] = str(e)
            meta["full_text"] = "".join(chunks).strip()
            meta["raw_response"] = {
                "stream": True,
                "response_id": response_id,
                "events_count": event_count,
                "finish_reason": finish_reason,
            }

    return iterator(), meta

def complete_with_provider(
    prompt: str,
    system: str = "",
    max_tokens: int = 256,
    provider: str = "ollama",
    tutor_prompt=None,
    messages: Optional[List[dict]] = None,
) -> Tuple[str, Dict]:
    provider = (provider or "ollama").lower()
    if provider == "ovh_ai":
        return complete_ovh(prompt, system, max_tokens, tutor_prompt=tutor_prompt, messages=messages)
    # For Ollama (non-chat endpoint), we currently ignore `messages` and keep behaviour unchanged.
    return complete_ollama(prompt, system, max_tokens)


def stream_with_provider(
    prompt: str,
    system: str = "",
    max_tokens: int = 256,
    provider: str = "ollama",
    tutor_prompt=None,
    messages: Optional[List[dict]] = None,
) -> Tuple[object, Dict]:
    provider = (provider or "ollama").lower()
    if provider == "ovh_ai":
        return stream_ovh(prompt, system, max_tokens, tutor_prompt=tutor_prompt, messages=messages)

    text, meta = complete_ollama(prompt, system, max_tokens, messages=messages)
    meta["full_text"] = text
    return _stream_single_chunk(text), meta

def complete(prompt: str, system: str = "", max_tokens: int = 256, tutor_prompt=None) -> Tuple[str, Dict]:
    default_provider = getattr(settings, "LLM_PROVIDER_DEFAULT", "ollama")
    return complete_with_provider(prompt, system, max_tokens, provider=default_provider, tutor_prompt=tutor_prompt)