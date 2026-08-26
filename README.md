# H3 Reference Pipeline

Image-first preparation for Seedance/H3 ads. It uses a local OpenAI-compatible
ChatGPT Web Gateway for Image-2 and stops before paid video generation.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m research_success_ads.browser_ai.gateway_status
python -m research_success_ads.pipeline.prepare_video001 --out outputs/linh_video001
```

Set `CHATGPT_GATEWAY_URL` and `CHATGPT_GATEWAY_IMAGE_MODEL=image-2` in `.env`.
Login/CAPTCHA remains a human step; do not commit `.env` or browser cookies.
The command creates one cached persona identity and three per-shot start frames,
runs local image QC, and writes `creative_plan.json`. Seedance, ElevenLabs,
ComfyUI, and SNS posting are intentionally not called by this lane.
