import spacy
from spacy.matcher import Matcher

nlp_pl = spacy.load('pl_core_news_sm')
nlp_en = spacy.load('en_core_web_sm')


def parse_voice_command(text,language):
    """
    Analyzes the voice command text to detect intent and entities (in English).
    """
    if not text:
        return {"intent": None, "entities": {}, "original_text": text}
    
    print(f"--- Debug Info ---")
    print(f"Original text: '{text}', Language: {language}")

    if language == "pl-PL":
      nlp = nlp_pl
    else:
      nlp = nlp_en  
    doc = nlp(text.lower()) 
    matcher = Matcher(nlp.vocab)

    # --- Define Patterns 

    # NextSong Intent
    matcher.add("NextSong", [
        [{"LEMMA": "next" }], 
        [{"LEMMA": "skip" }],
        [{"LOWER": {"IN": ["następna", "następny", "kolejna", "kolejny"]}}],
        [{"LOWER":"dalej"}]
    ])
    # PreviousSong Intent
    matcher.add("PreviousSong", [
        [{"LEMMA": "previous"}],
        [{"LEMMA": "back"}],
        [{"LOWER": {"IN": ["poprzednia", "wcześniejsza","wcześniej"]}}],
        [{"LEMMA": "cofnij"}]
    ])

    # AddToQueue Intent 
    matcher.add("AddToQueuePhrase", [
        [{"LOWER": "add"}, {"LOWER": "to"}, {"LOWER": "queue"}],
        [{"LOWER": "add"}, {"LOWER": "to"}, {"LOWER": "the"}, {"LOWER": "queue"}],
        [{"LOWER": "queue"}],
        [{"LOWER": "add"}],
        [{"LOWER": "dodaj"}, {"LOWER": "do"}, {"LOWER": "kolejki"}],
        [{"LOWER": "kolejka"}],
        [{"LOWER": "dodaj"}]

        
    ])
    
    # Play Intent & "by" keyword for artist
    matcher.add("PlayKeyword", [[{"LEMMA": {"IN": ["play", "start", "listen", "put"]}}],
                                [{"LOWER": {"IN": ["puść","graj","zagraj","odtwórz"]}}]]) 
    matcher.add("ByKeyword", [[{"LOWER": {"IN":["by","artist","przez","artysta","artystka"]}}]])

    # --- Find Matches ---
    matches = matcher(doc)
    print(f"Found matches by Matcher: {[(nlp.vocab.strings[m_id], s, e, doc[s:e].text) for m_id, s, e in matches]}")

    # --- Intent and Entity Extraction Logic ---
    detected_intent = None
    entities = {}

    next_song_match = None
    prev_song_match = None
    add_to_queue_match = None 
    play_keyword_match = None 

    # Find first occurrences of key phrases
    for match_id, start, end in matches:
        intent_name = nlp.vocab.strings[match_id]
        if intent_name == "NextSong" and not next_song_match:
            next_song_match = (start, end)
        elif intent_name == "PreviousSong" and not prev_song_match:
            prev_song_match = (start, end)
        elif intent_name == "AddToQueuePhrase" and not add_to_queue_match:
            add_to_queue_match = (start, end)
        elif intent_name == "PlayKeyword" and not play_keyword_match:
            play_keyword_match = (start, end)

    if next_song_match:
        detected_intent = "NextSong"
    elif prev_song_match:
        detected_intent = "PreviousSong"
    elif add_to_queue_match:
        detected_intent = "AddToQueue"
        title_start_idx = add_to_queue_match[1]
        current_by_keyword_match = None
        for match_id_by, start_by, end_by in matches:
            if nlp.vocab.strings[match_id_by] == "ByKeyword" and start_by > add_to_queue_match[0]:
                current_by_keyword_match = (start_by, end_by)
                break 
        
        if current_by_keyword_match:
            by_keyword_start_idx = current_by_keyword_match[0] 
            artist_start_idx = current_by_keyword_match[1]     

            if title_start_idx < by_keyword_start_idx:
                entities["song_title"] = doc[title_start_idx : by_keyword_start_idx].text.strip()
            
            if artist_start_idx < len(doc):
                entities["artist_name"] = doc[artist_start_idx :].text.strip()
        else:
            if title_start_idx < len(doc):
                entities["song_title"] = doc[title_start_idx :].text.strip()
            
    elif play_keyword_match:
        detected_intent = "PlaySong"
        title_start_idx = play_keyword_match[1] 
        current_by_keyword_match = None
        for match_id_by, start_by, end_by in matches:
            if nlp.vocab.strings[match_id_by] == "ByKeyword" and start_by > play_keyword_match[0]:
                current_by_keyword_match = (start_by, end_by)
                break 
        
        if current_by_keyword_match:
            by_keyword_start_idx = current_by_keyword_match[0] 
            artist_start_idx = current_by_keyword_match[1]     

            if title_start_idx < by_keyword_start_idx:
                entities["song_title"] = doc[title_start_idx : by_keyword_start_idx].text.strip()
            
            if artist_start_idx < len(doc):
                entities["artist_name"] = doc[artist_start_idx :].text.strip()
        else: 
            if title_start_idx < len(doc):
                entities["song_title"] = doc[title_start_idx :].text.strip()
    
    
    for key, value in list(entities.items()):
        if value == "":
            entities[key] = None

    print(f"Detected intent: {detected_intent}")
    print(f"Entities: {entities}")
    print(f"--------------------")


    return {
        "intent": detected_intent,
        "entities": entities,
        "original_text": text
    }