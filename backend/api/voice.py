# """
# API Router for Voice Chat (Sarvam AI Integration).
# Provides endpoints for real-time voice interactions with the AI Honeypot.
# """

# import base64
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from typing import Optional, List, Dict
# from core.voice_engine import voice_engine
# from core.ai import honeypot_ai
# from sqlalchemy.orm import Session
# from core.database import get_db
# from models.database import HoneypotPersona, HoneypotSession, HoneypotMessage

# router = APIRouter(prefix="/voice", tags=["Voice Chat"])


# class VoiceChatRequest(BaseModel):
#     """Request body for a voice chat turn."""
#     audio_base64: str  # Base64-encoded audio from scammer's call
#     persona: str = "Elderly Uncle"
#     language: str = "hi-IN"
#     history: List[Dict[str, str]] = []
#     session_id: Optional[str] = None


# class VoiceChatResponse(BaseModel):
#     """Response body containing AI's voice reply."""
#     scammer_transcript: str
#     ai_response_text: str
#     ai_audio_base64: str
#     audio_format: str
#     language: str
#     persona: str


# class TTSRequest(BaseModel):
#     """Request body for text-to-speech only."""
#     text: str
#     persona: str = "Elderly Uncle"


# class STTRequest(BaseModel):
#     """Request body for speech-to-text only."""
#     audio_base64: str
#     language: str = "hi-IN"


# @router.post("/chat", response_model=VoiceChatResponse)
# async def voice_chat_turn(request: VoiceChatRequest, db: Session = Depends(get_db)):
#     """
#     Complete voice chat turn with optional session persistence.
#     """
#     try:
#         audio_bytes = base64.b64decode(request.audio_base64)
        
#         # 1. Pipeline Execution
#         result = await voice_engine.voice_chat_turn(
#             scammer_audio=audio_bytes,
#             persona=request.persona,
#             ai_generate_fn=honeypot_ai.generate_response,
#             history=request.history,
#         )

#         # 2. Optional Session Persistence
#         if request.session_id:
#             db_session = db.query(HoneypotSession).filter(HoneypotSession.session_id == request.session_id).first()
#             if db_session:
#                 # Log scammer transcription
#                 if result["scammer_transcript"]:
#                     scammer_msg = HoneypotMessage(
#                         session_id=db_session.id, 
#                         role="user", 
#                         content=result["scammer_transcript"]
#                     )
#                     db.add(scammer_msg)
                
#                 # Log AI response
#                 ai_msg = HoneypotMessage(
#                     session_id=db_session.id, 
#                     role="assistant", 
#                     content=result["ai_response_text"]
#                 )
#                 db.add(ai_msg)
#                 db.commit()

#         return VoiceChatResponse(**result)
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return VoiceChatResponse(
#             scammer_transcript="",
#             ai_response_text=f"⚠️ [System Error: Voice Engine backend failure].",
#             ai_audio_base64="",
#             audio_format="wav",
#             language=request.language,
#             persona=request.persona,
#         )


# @router.post("/tts")
# async def text_to_speech(request: TTSRequest):
#     """Convert text to speech using Sarvam Bulbul v3."""
#     try:
#         result = await voice_engine.synthesize_speech(
#             text=request.text,
#             persona=request.persona,
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


# @router.post("/stt")
# async def speech_to_text(request: STTRequest):
#     """Convert speech to text using Sarvam Saaras v3."""
#     try:
#         audio_bytes = base64.b64decode(request.audio_base64)
#         result = await voice_engine.transcribe_audio(
#             audio_bytes=audio_bytes,
#             language=request.language,
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")


# @router.get("/personas")
# async def list_personas(db: Session = Depends(get_db)):
#     """List available voice personas with their language configurations."""
#     personas = db.query(HoneypotPersona).all()
#     if not personas:
#         # Fallback to default if DB is empty
#         return {
#             "personas": [
#                 {
#                     "name": "Sentinel AI",
#                     "language": "hi-IN",
#                     "speaker": "Male",
#                     "pace": 1.0,
#                 }
#             ]
#         }
#     return {"personas": personas}

"""
API Router for Voice Chat (Sarvam AI Integration).
Provides endpoints for real-time voice interactions with the AI Honeypot.
"""

import base64
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from core.voice_engine import voice_engine
from core.ai import honeypot_ai
from core.database import get_db
from models.database import HoneypotPersona, HoneypotSession, HoneypotMessage


router = APIRouter(prefix="/voice", tags=["Voice Chat"])


# ------------------------------------------------------------------
# REQUEST / RESPONSE MODELS
# ------------------------------------------------------------------

class VoiceChatRequest(BaseModel):
    """Request body for a voice chat turn."""
    audio_base64: str
    persona: str = "Elderly Uncle"
    language: str = "hi-IN"
    history: List[Dict[str, str]] = Field(default_factory=list)
    session_id: Optional[str] = None


class VoiceChatResponse(BaseModel):
    """Response body containing AI's voice reply."""
    scammer_transcript: str
    ai_response_text: str
    ai_audio_base64: str
    audio_format: str
    language: str
    persona: str


class TTSRequest(BaseModel):
    """Request body for text-to-speech."""
    text: str
    persona: str = "Elderly Uncle"


class STTRequest(BaseModel):
    """Request body for speech-to-text."""
    audio_base64: str
    language: str = "hi-IN"


# ------------------------------------------------------------------
# VOICE CHAT ENDPOINT
# ------------------------------------------------------------------

@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat_turn(request: VoiceChatRequest, db: Session = Depends(get_db)):
    """
    Complete voice chat turn:
    STT -> AI -> TTS
    """

    if not request.audio_base64:
        raise HTTPException(status_code=400, detail="No audio provided")

    try:
        # Handle "data:audio/wav;base64,XXXXX" style payloads
        audio_str = request.audio_base64.split(",")[-1]

        try:
            # Fix base64 padding if needed
            audio_str += '=' * (-len(audio_str) % 4)
            audio_bytes = base64.b64decode(audio_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 audio")

        # Run full voice pipeline
        result = await voice_engine.voice_chat_turn(
            scammer_audio=audio_bytes,
            persona=request.persona,
            ai_generate_fn=honeypot_ai.generate_response,
            history=request.history,
        )

        # Ensure required keys exist
        required_keys = [
            "scammer_transcript",
            "ai_response_text",
            "ai_audio_base64",
            "audio_format"
        ]

        for key in required_keys:
            if key not in result:
                raise HTTPException(
                    status_code=500,
                    detail=f"Voice engine missing key: {key}"
                )

        # --------------------------------------------------------------
        # Optional DB persistence
        # --------------------------------------------------------------
        if request.session_id:

            db_session = (
                db.query(HoneypotSession)
                .filter(HoneypotSession.session_id == request.session_id)
                .first()
            )

            if db_session:

                if result["scammer_transcript"]:
                    scammer_msg = HoneypotMessage(
                        session_id=db_session.id,
                        role="user",
                        content=result["scammer_transcript"],
                    )
                    db.add(scammer_msg)

                ai_msg = HoneypotMessage(
                    session_id=db_session.id,
                    role="assistant",
                    content=result["ai_response_text"],
                )
                db.add(ai_msg)

                db.commit()

        return VoiceChatResponse(
            scammer_transcript=result["scammer_transcript"],
            ai_response_text=result["ai_response_text"],
            ai_audio_base64=result["ai_audio_base64"],
            audio_format=result["audio_format"],
            language=request.language,
            persona=request.persona,
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Voice chat pipeline failed: {str(e)}"
        )


# ------------------------------------------------------------------
# TEXT TO SPEECH
# ------------------------------------------------------------------

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Sarvam Bulbul v3."""

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        result = await voice_engine.synthesize_speech(
            text=request.text,
            persona=request.persona,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


# ------------------------------------------------------------------
# SPEECH TO TEXT
# ------------------------------------------------------------------

@router.post("/stt")
async def speech_to_text(request: STTRequest):
    """Convert speech to text using Sarvam Saaras v3."""

    if not request.audio_base64:
        raise HTTPException(status_code=400, detail="No audio provided")

    try:
        audio_str = request.audio_base64.split(",")[-1]
        audio_bytes = base64.b64decode(audio_str)

        result = await voice_engine.transcribe_audio(
            audio_bytes=audio_bytes,
            language=request.language,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")


# ------------------------------------------------------------------
# PERSONA LIST
# ------------------------------------------------------------------

@router.get("/personas")
async def list_personas(db: Session = Depends(get_db)):
    """Return available personas."""

    personas = db.query(HoneypotPersona).all()

    if not personas:
        return {
            "personas": [
                {
                    "name": "Sentinel AI",
                    "language": "hi-IN",
                    "speaker": "Male",
                    "pace": 1.0,
                }
            ]
        }

    return {
        "personas": [
            {
                "name": p.name,
                "language": p.language,
                "speaker": p.speaker,
                "pace": p.pace,
            }
            for p in personas
        ]
    }