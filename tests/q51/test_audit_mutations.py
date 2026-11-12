import json, shutil, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REQUIRED=['standings_2026.json','schedule_week11_2026.json','teams.json','player_leaders_2026.json','team_stats_defense_2026.json','injuries_2026-11-11.json','suggestions.json','questions.json','strategies.json']

class AuditMutationTests(unittest.TestCase):
    def test_evidence_ledger_covers_baseline_factual_errors(self):
        x=json.loads((ROOT/'research/q51/source-evidence.json').read_text())
        ids={f['id'] for f in x['findings']}
        self.assertTrue({f'A-{i:02d}' for i in range(1,7)} <= ids)
        sources={s['id'] for s in x['sources']}
        for f in x['findings']:
            self.assertTrue(f['source_ids'])
            self.assertTrue(set(f['source_ids']) <= sources)

    def test_legacy_validator_misses_factual_mutations(self):
        # Negative control: a presence/completeness validator is not a truth oracle.
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); (t/'scripts').mkdir(); (t/'data').mkdir()
            shutil.copy2(ROOT/'scripts/validate_data.py',t/'scripts/validate_data.py')
            for name in REQUIRED: shutil.copy2(ROOT/'data'/name,t/'data'/name)
            p=t/'data/player_leaders_2026.json'; d=json.loads(p.read_text())
            for row in d['rushing']['rows']:
                if row[0]=='Jaylen Warren': row[3]=7  # official value is 2
            p.write_text(json.dumps(d))
            p=t/'data/schedule_week11_2026.json'; d=json.loads(p.read_text())
            for g in d['games']:
                if g['away']=='MIA' and g['home']=='BUF': g['tv']='CBS'  # dated release says FOX
            p.write_text(json.dumps(d))
            p=t/'data/injuries_2026-11-11.json'; d=json.loads(p.read_text())
            for r in d['key_items']:
                if r['player'].startswith('Puka Nacua'): r['status']='Out (extended)'  # not a formal designation in the cited passage
            p.write_text(json.dumps(d))
            r=subprocess.run(['python3',str(t/'scripts/validate_data.py')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertIn('VALIDATION PASSED',r.stdout)

if __name__=='__main__': unittest.main()
