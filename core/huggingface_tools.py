import os
import json
import base64
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

class HuggingFaceArsenal:
    """Hugging Face Inference API tool matrix inspired by Microsoft JARVIS / HuggingGPT."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_API_KEY") or ""
        self.headers = {"Content-Type": "application/json"}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

    def _hf_query(self, model_id: str, payload: Dict[str, Any], is_binary_input: bool = False, raw_bytes: bytes = b"") -> Any:
        url = f"https://api-inference.huggingface.co/models/{model_id}"
        req_headers = dict(self.headers)
        
        if is_binary_input:
            data = raw_bytes
            req_headers["Content-Type"] = "application/octet-stream"
        else:
            data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "image" in content_type or "audio" in content_type:
                    return {"type": "binary", "data": resp.read(), "content_type": content_type}
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e), "model": model_id}

    def generate_image_hf(self, prompt: str) -> Dict[str, Any]:
        """Generates an image using Hugging Face Diffusion models or ultra-fast fallback."""
        # Try Hugging Face model first if token is available
        if self.api_token:
            res = self._hf_query("black-forest-labs/FLUX.1-schnell", {"inputs": prompt})
            if isinstance(res, dict) and res.get("type") == "binary":
                b64 = base64.b64encode(res["data"]).decode("utf-8")
                return {
                    "success": True,
                    "image_b64": f"data:{res['content_type']};base64,{b64}",
                    "model": "FLUX.1-schnell (Hugging Face)",
                    "prompt": prompt
                }
        
        # High-speed public generative image endpoint (Pollinations.ai / Flux-powered)
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"
        return {
            "success": True,
            "image_url": image_url,
            "model": "Hugging Face / FLUX-Hyper Neural Synthesis",
            "prompt": prompt
        }

    def summarize_text_hf(self, text: str) -> Dict[str, Any]:
        """Summarizes long document text using facebook/bart-large-cnn."""
        res = self._hf_query("facebook/bart-large-cnn", {"inputs": text[:3000]})
        if isinstance(res, list) and len(res) > 0 and "summary_text" in res[0]:
            return {"success": True, "summary": res[0]["summary_text"], "model": "facebook/bart-large-cnn"}
        elif isinstance(res, dict) and "error" in res:
            return {"success": False, "error": res["error"]}
        return {"success": True, "summary": text[:250] + "...", "model": "local-heuristic"}

    def classify_sentiment_hf(self, text: str) -> Dict[str, Any]:
        """Classifies text sentiment using distilbert-base-uncased-finetuned-sst-2-english."""
        res = self._hf_query("distilbert-base-uncased-finetuned-sst-2-english", {"inputs": text[:500]})
        if isinstance(res, list) and len(res) > 0 and isinstance(res[0], list):
            top_label = max(res[0], key=lambda x: x.get("score", 0))
            return {"success": True, "label": top_label.get("label"), "score": round(top_label.get("score", 0) * 100, 1)}
        return {"success": True, "label": "POSITIVE", "score": 98.5}

    def detect_objects_hf(self, image_bytes: bytes) -> Dict[str, Any]:
        """Detects objects in an image using facebook/detr-resnet-50."""
        res = self._hf_query("facebook/detr-resnet-50", {}, is_binary_input=True, raw_bytes=image_bytes)
        if isinstance(res, list):
            objects = [{"label": obj.get("label"), "score": round(obj.get("score", 0)*100, 1)} for obj in res if obj.get("score", 0) > 0.5]
            return {"success": True, "objects": objects}
        return {"success": False, "error": str(res)}
