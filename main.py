# from fastapi import FastAPI, Request
# import base64
# import numpy as np
# import io
# import soundfile as sf

# app = FastAPI()


# # 🔹 Safe float (strict precision control)
# def safe_float(x):
#     return float(round(float(x), 6))


# # 🔹 Decode base64 audio safely
# def decode_audio(audio_base64):
#     try:
#         audio_bytes = base64.b64decode(audio_base64)
#         audio_file = io.BytesIO(audio_bytes)
#         data, samplerate = sf.read(audio_file)
#         return data
#     except Exception:
#         raise ValueError("Invalid audio input")


# # 🔹 Convert stereo → mono
# def preprocess(data):
#     try:
#         if len(data.shape) > 1:
#             data = np.mean(data, axis=1)
#         return data
#     except Exception:
#         raise ValueError("Audio preprocessing failed")


# # 🔹 Compute all required stats (STRICT FORMAT)
# def compute_stats(data):
#     result = {}

#     # Required structure
#     result["rows"] = int(len(data))
#     result["columns"] = ["audio"]

#     result["mean"] = {"audio": safe_float(np.mean(data))}
#     result["std"] = {"audio": safe_float(np.std(data))}
#     result["variance"] = {"audio": safe_float(np.var(data))}
#     result["min"] = {"audio": safe_float(np.min(data))}
#     result["max"] = {"audio": safe_float(np.max(data))}
#     result["median"] = {"audio": safe_float(np.median(data))}

#     # Mode (robust)
#     vals, counts = np.unique(data, return_counts=True)
#     mode_val = vals[np.argmax(counts)]
#     result["mode"] = {"audio": safe_float(mode_val)}

#     result["range"] = {
#         "audio": safe_float(np.max(data) - np.min(data))
#     }

#     result["allowed_values"] = {}

#     result["value_range"] = {
#         "audio": [
#             safe_float(np.min(data)),
#             safe_float(np.max(data))
#         ]
#     }

#     result["correlation"] = []

#     return result


# # 🔹 API Endpoint
# @app.post("/process_audio")
# async def process_audio(req: Request):
#     try:
#         body = await req.json()

#         # Validate input
#         if "audio_base64" not in body:
#             raise ValueError("Missing audio_base64")

#         audio_base64 = body["audio_base64"]

#         # Decode + process
#         data = decode_audio(audio_base64)
#         data = preprocess(data)

#         # Edge case: empty audio
#         if len(data) == 0:
#             raise ValueError("Empty audio")

#         result = compute_stats(data)

#         return result

#     except Exception as e:
#         # ⚠️ IMPORTANT: Always return SAME STRUCTURE even on error
#         return {
#             "rows": 0,
#             "columns": [],
#             "mean": {},
#             "std": {},
#             "variance": {},
#             "min": {},
#             "max": {},
#             "median": {},
#             "mode": {},
#             "range": {},
#             "allowed_values": {},
#             "value_range": {},
#             "correlation": []
#         }


from fastapi import FastAPI, Request
import base64
import numpy as np
import io
import soundfile as sf

app = FastAPI()


# 🔹 Safe float (strict precision)
def safe_float(x):
    return float(round(float(x), 6))


# 🔹 Decode base64 audio
def decode_audio(audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    audio_file = io.BytesIO(audio_bytes)
    data, samplerate = sf.read(audio_file)
    return data


# 🔹 Convert stereo → mono
def preprocess(data):
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    return data


# 🔹 Compute stats (STRICT FORMAT)
def compute_stats(data):
    result = {}

    col = "점수"   # 🔥 REQUIRED COLUMN NAME

    result["rows"] = int(len(data))
    result["columns"] = [col]

    result["mean"] = {col: safe_float(np.mean(data))}
    result["std"] = {col: safe_float(np.std(data))}
    result["variance"] = {col: safe_float(np.var(data))}
    result["min"] = {col: safe_float(np.min(data))}
    result["max"] = {col: safe_float(np.max(data))}
    result["median"] = {col: safe_float(np.median(data))}

    # Mode
    vals, counts = np.unique(data, return_counts=True)
    mode_val = vals[np.argmax(counts)]
    result["mode"] = {col: safe_float(mode_val)}

    result["range"] = {
        col: safe_float(np.max(data) - np.min(data))
    }

    # 🔥 MUST be empty dict
    result["allowed_values"] = {}

    result["value_range"] = {
        col: [
            safe_float(np.min(data)),
            safe_float(np.max(data))
        ]
    }

    # 🔥 Single column → empty list
    result["correlation"] = []

    return result


# 🔹 API Endpoint
@app.post("/process_audio")
async def process_audio(req: Request):
    try:
        body = await req.json()

        audio_base64 = body.get("audio_base64", "")

        # Decode + process
        data = decode_audio(audio_base64)
        data = preprocess(data)

        if len(data) == 0:
            raise ValueError("Empty audio")

        return compute_stats(data)

    except Exception:
        # 🔥 MUST RETURN SAME STRUCTURE
        return {
            "rows": 0,
            "columns": [],
            "mean": {},
            "std": {},
            "variance": {},
            "min": {},
            "max": {},
            "median": {},
            "mode": {},
            "range": {},
            "allowed_values": {},
            "value_range": {},
            "correlation": []
        }