IDENTITY_MASTER = '''Create ONE single realistic photograph for a fictional Vietnamese social-media character named Linh. 24-year-old Vietnamese woman living in Japan, approachable creator appearance, shoulder-length dark hair, natural skin texture, ordinary smartphone selfie, vertical 9:16. Do not resemble any specific real person. No text, logos, subtitles, collage or multiple images. This is the identity master; keep face, hair and body proportions stable.'''

IDENTITY_MASTER_SHEET = '''Create ONE identity reference photograph for the same fictional Vietnamese woman Linh (24, living in Japan). Show a clean vertical 9:16 full-body portrait, neutral expression, shoulder-length dark hair, consistent body proportions, plain light-gray background, simple neutral clothing. This image is an identity anchor only. No text, logo, collage, split screen, watermark, or readable marks. Do not resemble a real person.'''

CAMERA_PRESETS = {
    'selfie_front': 'front phone-camera selfie, 26mm-equivalent wide angle, close-range edge distortion, holding arm visible, slightly below eye level, everyday background',
    'propped_static': 'phone propped on a counter, slightly low angle tilted upward, lived-in background, subtle surface vibration',
    'phone_raw': 'ungraded phone-camera look, mixed color temperature, slight white-balance drift, mild compression, slightly off-center framing',
}

STORYBOARD_GRID = '''Create ONE single 2x2 storyboard grid image on a vertical 9:16 canvas. Each panel is a separate portrait 9:16 composition, read in order: top-left = S1, top-right = S2, bottom-left = S3, bottom-right = EMPTY neutral gray. Use the attached person only as IDENTITY REFERENCE: preserve face, hairstyle, skin tone and body proportions, but do not copy the reference background or pose. Keep the same person, wardrobe continuity and lighting across S1-S3. S1: {s1}. S2: {s2}. S3: {s3}. Panel borders must be clear and even. Do not put labels, captions, logos, readable text or extra people in panels. Do not make a character sheet or profile portrait; show the specified scene and action in each panel.'''

SHOT_START = '''Generate ONE single realistic vertical 9:16 photograph of the named fictional creator in a REAL SCENE, not a character sheet or profile portrait. IDENTITY LOCK: preserve only the attached person's face, hairstyle, skin tone and body proportions. Do not copy the reference pose or gray studio background. COMPOSITION LOCK: {camera}. SCENE LOCK: {location}. ACTION LOCK at this exact start moment: {action}. WARDROBE LOCK: {wardrobe}. PROP LOCK: {prop}. The action and scene must be visibly present; do not replace them with a neutral standing portrait. One image only, no collage, no split screen, no turnaround sheet, no passport photo, no profile image, no text, subtitles, logos, UI, labels or watermark. This is a start frame for a video.'''

VIDEO001 = [
    {'id':'s1','duration':5,'location':'small ordinary apartment in Japan','camera':'phone on desk, medium locked shot','action':'Linh stands close to the phone and gives one small friendly wave','dialogue_vi':'Xin chào, mình là Linh. Mình 24 tuổi.'},
    {'id':'s2','duration':5,'location':'ordinary Japanese street','camera':'handheld selfie at arm length','action':'Linh walks slowly while holding the phone and shows the street behind her','dialogue_vi':'Mình đang sống ở Nhật. Mình rất thích cuộc sống ở đây.'},
    {'id':'s3','duration':5,'location':'ordinary cafe or apartment','camera':'handheld selfie, chest-up','action':'Linh places the black interview bag beside her and looks into the lens with a slightly worried smile','dialogue_vi':'Và... mình vẫn đang tìm việc. Xem bao giờ mình được nhận nhé.'}
]
