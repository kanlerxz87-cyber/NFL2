import unittest
from collectors.q51.collect import Document,injuries,depth_chart,SafeRedirect

CLUBS=[{'team':'New England Patriots','abbr':'NE','home':'https://www.patriots.com/'},{'team':'Dallas Cowboys','abbr':'DAL','home':'https://www.dallascowboys.com/'}]
ENTRY={'url':'https://www.nfl.com/injuries/league/2026/REG10','retrieved_at':'2026-11-12T00:00:00+00:00','sha256':'test-hash-not-an-official-observation'}

class CollectorTests(unittest.TestCase):
    def test_injury_blank_stays_blank(self):
        d=Document(); d.feed('<h2>Injuries - WEEK 10</h2>Patriots<table><tr><th>Player</th><th>Position</th><th>Injuries</th><th>Practice Status</th><th>Game Status</th></tr><tr><td>Drake Maye</td><td>QB</td><td></td><td>Full Participation in Practice</td><td></td></tr></table>'); d.close()
        row=injuries(d,ENTRY,CLUBS)['rows'][0]; self.assertIsNone(row['injury']); self.assertIsNone(row['game_status']); self.assertEqual(row['team_abbr'],'NE'); self.assertNotEqual(row['practice_status'],row['game_status'])
    def test_unknown_team_not_guessed(self):
        d=Document(); d.feed('<table><tr><th>Player</th><th>Position</th><th>Injuries</th><th>Practice Status</th><th>Game Status</th></tr><tr><td>Test Player</td><td>QB</td><td></td><td>Limited</td><td></td></tr></table>'); d.close()
        row=injuries(d,ENTRY,CLUBS)['rows'][0]; self.assertIsNone(row['team']); self.assertFalse(row['verified'])
    def test_depth_missing_first_string_and_or_preserved(self):
        d=Document(); d.feed('<h1>Unofficial Depth Chart</h1><h2>Offense</h2><table><tr><td>QB</td><td>Starter</td><td>Backup</td><td></td><td>Fourth</td></tr><tr><td>WR</td><td>First OR Other</td><td></td></tr></table>'); d.close()
        rows=depth_chart(d,{**ENTRY,'url':'https://www.patriots.com/team/depth-chart'},CLUBS[0]); self.assertIsNone(rows[0]['slots'][2]['players']); self.assertEqual(rows[0]['slots'][3]['players'],['Fourth']); self.assertEqual(rows[1]['slots'][0]['players'],['First','Other']); self.assertIsNone(rows[0]['confirmed_gameday_lineup']); self.assertEqual(rows[0]['editorial_status'],'club_published_unofficial')
    def test_redirect_allowlist(self):
        h=SafeRedirect({'www.nfl.com'})
        with self.assertRaises(ValueError): h.redirect_request(None,None,302,'',{},'https://example.com/')
    def test_script_capture_for_official_schedule_schema(self):
        d=Document(); d.feed('<script type="application/ld+json">{"test":true}</script>'); d.close(); self.assertEqual(d.scripts[0]['type'],'application/ld+json')

if __name__=='__main__': unittest.main()
