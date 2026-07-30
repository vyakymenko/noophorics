import json, sys, statistics
sys.path.insert(0,'metrics')
from noophorics import load_probe_measure, to_distribution, agreement_rate
from noophorics.ollama_agent import OllamaAgent
m=load_probe_measure('experiments/E-002-phantom-agreement/probes.json')
spec=open('experiments/E-001-fluency-cost/source-spec.md').read()
sender=OllamaAgent('s', spec, think='medium')
snd={p.id: sender.answer_samples(p, 8) for p in m}
sd=[to_distribution(snd[p.id]) for p in m]
out={}
for words in (30, 70, 150):
    prompt=("You are holding a set of submission-handling rules. A colleague who has never "
            "seen them must decide real cases using only your note. Write the note in "
            "between %d and %d words. Output the note and nothing else."
            % (int(words*0.85), int(words*1.15)))
    brief=sender.compose(prompt, seed=0)
    rcv=OllamaAgent('r', brief, think='medium')
    rd=[to_distribution(rcv.answer_samples(p, 8)) for p in m]
    a=agreement_rate(sd, rd, m.weights)
    smod=[max(sorted(x),key=lambda k:x[k]) for x in sd]
    rmod=[max(sorted(x),key=lambda k:x[k]) for x in rd]
    div=sum(1 for x,y in zip(smod,rmod) if x!=y)
    out[words]={'brief_words':len(brief.split()),'agreement':a,'diverged':div}
    print("  budget ~%3d words -> brief %3d words | agreement %.4f | diverged %2d/33"
          % (words, len(brief.split()), a, div), flush=True)
json.dump(out, open('/private/tmp/claude-501/-Users-vyakymenko-Documents-git-GitHub/3581e811-4fad-4fb7-a9a0-0c1bd7c9c41e/scratchpad/budget.json','w'), indent=1)
