import webrtcvad

def apply_vad_filter(audio_bytes: bytes, sample_rate: int=16000) -> bytes:
    vad = webrtcvad.Vad()
    vad.set_mode(3) # 3 is the most aggressive setting for filtering out background noise

    frame_duration_ms = 30
    frame_size = int(sample_rate * (frame_duration_ms / 1000) * 2)
    
    clean_audio = bytearray()

    # process the audio in 30ms frames
    for i in range (0, len(audio_bytes)-frame_size + 1, frame_size):
        frame = audio_bytes[i:i+frame_size]
        is_speech = vad.is_speech(frame, sample_rate)
        
        # if the frame is classified as speech, add it to the clean_audio bytearray
        if is_speech:
            clean_audio.extend(frame)
            
    return bytes (clean_audio)