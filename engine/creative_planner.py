from __future__ import annotations
from copy import deepcopy
from typing import Any

RECIPES = ('pattern_interrupt', 'curiosity_gap', 'reaction', 'transformation', 'story_vlog')

def _shots(recipe: str, variant: int) -> list[dict[str, Any]]:
    actions = {
        'pattern_interrupt': ('HR manager waits among empty interview chairs', 'checks phone and sees no applicants', 'support staff enters with a clear job card', 'manager points to the card with renewed confidence'),
        'curiosity_gap': ('job seeker says “today is interview number seven”', 'camera reveals a stack of rejection notices', 'support staff opens a matching job on phone', 'job seeker looks up with relief'),
        'reaction': ('job seeker receives a rejection notification', 'holds the phone toward camera in disbelief', 'support staff explains the next matching step', 'job seeker nods and smiles'),
        'transformation': ('job seeker sits anxious before an interview', 'support staff rehearses one answer with them', 'cut to confident workplace arrival', 'job seeker gives a small confident bow'),
        'story_vlog': ('job seeker wakes and checks job listings', 'walks into an interview and waits', 'support staff guides the next application', 'job seeker leaves for work with confidence'),
    }[recipe]
    cameras = ('locked', 'slow_push_in', 'dolly_right', 'locked')
    shots=[]
    for i,(start,end) in enumerate(((0,3),(3,7),(7,11),(11,15))):
        speaker = ('job_seeker','job_seeker','support_staff','job_seeker')[i]
        shots.append({'id':f's{i+1}','start':start,'end':end,'shot':('wide','medium','medium_closeup','medium_closeup')[i],'camera':cameras[i],'actor_action':actions[i],'dialogue':None,'speaker':speaker,'purpose':('pattern_interrupt','tension','solution','cta')[i]})
    return shots

class CreativePlanner:
    def __init__(self, recipes: list[str] | None = None):
        self.recipes = recipes or list(RECIPES)
    def next_plan(self, offer: dict[str, Any], previous_plans: list[dict[str, Any]], index: int) -> dict[str, Any]:
        recipe = offer.get('recipe_hint') if offer.get('recipe_hint') in self.recipes else self.recipes[index % len(self.recipes)]
        plan = {'recipe_id': f'{recipe}_{index+1:02d}', 'offer_id': offer.get('offer_id','offer_unknown'), 'character_id': offer.get('character_id','jobseeker_01'), 'locale':'ja-JP', 'aspect_ratio':'9:16', 'duration':15, 'variant_index':index+1, 'shots':_shots(recipe,index+1), 'dialogue':offer.get('default_dialogue','')}
        return plan
