# Video001 image gate

This lane stops after Image-2 start-frame generation. It does not call Seedance,
ElevenLabs, ComfyUI, or any paid API.

```powershell
python -m browser_ai.gateway_status
python -m pipeline.prepare_video001 --out outputs/linh_video001
```

`CHATGPT_GATEWAY_URL` points at the locally running browser gateway. Put the
actual value in `research_success_ads/.env` (never `.env.example`). The default
image model is `image-2`; override it with `CHATGPT_GATEWAY_IMAGE_MODEL` only if
the gateway exposes a different alias.

The first run creates and caches:

* `research_success_ads/personas/linh_01/identity_master.png`
* `outputs/linh_video001/s1_start.png` through `s3_start.png`
* `outputs/linh_video001/creative_plan.json`

If the gateway is not running, the command fails before any paid video request.
