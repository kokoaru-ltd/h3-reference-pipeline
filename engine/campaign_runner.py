from __future__ import annotations
import argparse, json
from pathlib import Path
from .creative_planner import CreativePlanner
from .preflight_validator import preflight
from .seedance_prompt_compiler import compile_prompt
from .seedance_adapter import SeedanceAdapter
from .elevenlabs_tts import ElevenLabsTTS
from .final_assembler import FinalAssembler
from .qc_visual import evaluate_clip
from .retry_controller import patch_failed_shots

def run(offer: dict, target: int, out_dir: Path, mode='dry-run') -> dict:
    out_dir.mkdir(parents=True,exist_ok=True); planner=CreativePlanner(); generator=SeedanceAdapter(mode); tts=ElevenLabsTTS(mode); assembler=FinalAssembler(); accepted=[]; history=[]
    for i in range(target):
        plan=planner.next_plan(offer, accepted, i); pf=preflight(plan,offer)
        if pf['status']!='PASS': raise ValueError(pf)
        run_dir=out_dir/f'{i+1:02d}_{plan["recipe_id"]}'; run_dir.mkdir(parents=True,exist_ok=True); (run_dir/'creative_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
        passed=[]; current=plan; shot_records=[]
        for shot in list(plan['shots']):
            attempt=0
            while True:
                compiled=compile_prompt(current,offer); shot_path=run_dir/f'{shot["id"]}_attempt_{attempt+1}.mp4'; generator.generate(compiled,shot,shot_path); qc=evaluate_clip(shot_path,{'duration':float(shot['end'])-float(shot['start']),'shots':[{'id':shot['id'],'start':0,'end':float(shot['end'])-float(shot['start'])}]})
                shot_records.append({'shot_id':shot['id'],'attempt':attempt+1,'qc':qc})
                if qc['status']=='PASS': passed.append(shot_path); break
                attempt+=1
                if attempt<=2: current=patch_failed_shots(current,{'failed_shots':[shot['id']],'reasons':qc['reasons']},attempt); shot=next(s for s in current['shots'] if s['id']==shot['id']); continue
                current=patch_failed_shots(current,{'failed_shots':[shot['id']],'reasons':qc['reasons']},attempt); shot=next(s for s in current['shots'] if s['id']==shot['id']); generator.generate(compile_prompt(current,offer),shot,run_dir/f'{shot["id"]}_fallback.mp4'); passed.append(run_dir/f'{shot["id"]}_fallback.mp4'); break
        segments=offer.get('dialogue_segments') or ([{'speaker':'narrator','text':plan.get('dialogue',''),'start':0,'end':float(plan['duration'])}] if plan.get('dialogue') else [])
        audio=tts.generate_script(segments,run_dir/'voice.mp3',float(plan['duration'])); final=assembler.render(passed,audio,run_dir/'final.mp4'); final_qc=evaluate_clip(final,plan); record={'index':i+1,'recipe_id':plan['recipe_id'],'final':str(final),'final_qc':final_qc,'shots':shot_records,'status':'PASS' if final_qc['status']=='PASS' else 'FAIL'}; (run_dir/'run_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8'); history.append(record)
        if record['status']=='PASS': accepted.append(record)
    summary={'target':target,'pass_count':len(accepted),'status':'PASS' if len(accepted)==target else 'FAIL','runs':history,'mode':mode}; (out_dir/'campaign_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8'); return summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--offer',required=True); ap.add_argument('--count',type=int,default=5); ap.add_argument('--out',default='outputs/campaign'); ap.add_argument('--mode',choices=['dry-run','seedance'],default='dry-run'); a=ap.parse_args(); offer=json.loads(Path(a.offer).read_text(encoding='utf-8')); print(json.dumps(run(offer,a.count,Path(a.out),a.mode),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
