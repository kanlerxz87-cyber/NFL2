import math, unittest
from engine.q51.odds import *
from engine.q51.statistics import *
from engine.q51.models import Game,RidgeBaseline
from engine.q51.grading import grade_single,grade_parlay
from engine.q51.validation import evaluate_gates,leaderboard,GATES

class OddsTests(unittest.TestCase):
    def test_american_conversion(self):
        self.assertAlmostEqual(american_to_decimal(-110),1+100/110)
        self.assertAlmostEqual(american_to_decimal(150),2.5)
        self.assertAlmostEqual(implied_probability(-110),110/210)
        self.assertAlmostEqual(probability_to_american(.4),150)
    def test_invalid_american(self):
        for x in (0,99,-99,float('nan'),float('inf')):
            with self.assertRaises(ValueError): american_to_decimal(x)
    def test_devig(self):
        d=devig_multiplicative([-110,-110]); self.assertEqual(d['fair'],[.5,.5]); self.assertAlmostEqual(d['overround'],1/21); self.assertAlmostEqual(d['normalized_margin'],1/22)
    def test_devig_rejects_negative_book(self):
        with self.assertRaises(ValueError): devig_multiplicative([200,200])
    def test_ev_push(self):
        self.assertAlmostEqual(expected_value(.5,2,.1),.1)
        self.assertAlmostEqual(fair_decimal_from_outcomes(.5,.1),1.8)
    def test_kelly_cap_and_no_bet(self):
        self.assertEqual(kelly_fraction(.6,2),.01); self.assertEqual(kelly_fraction(.5,2),0)
    def test_parlay_price_not_probability(self):
        self.assertAlmostEqual(parlay_decimal([100,100]),4)

class StatisticsTests(unittest.TestCase):
    def test_pearson(self):
        self.assertAlmostEqual(pearson([1,2,3],[2,4,6]),1)
        self.assertIsNone(pearson([1,1,1],[1,2,3]))
    def test_phi_joint(self):
        j=joint_metrics([1,1,0,0],[1,1,0,0]); self.assertAlmostEqual(j['phi'],1); self.assertAlmostEqual(j['p_joint'],.5); self.assertAlmostEqual(j['joint_lift'],2)
    def test_cluster_bootstrap_deterministic(self):
        a=cluster_bootstrap_mean([1,2,3,4],['a','a','b','c'],iterations=200,seed=7)
        b=cluster_bootstrap_mean([1,2,3,4],['a','a','b','c'],iterations=200,seed=7)
        self.assertEqual(a,b); self.assertLessEqual(a['lower'],a['estimate']); self.assertGreaterEqual(a['upper'],a['estimate'])
    def test_correlation_interval(self):
        x=list(range(20)); y=[2*v+1 for v in x]
        r=cluster_bootstrap_correlation(x,y,x,iterations=200,seed=7); self.assertAlmostEqual(r['estimate'],1); self.assertEqual(r['clusters'],20)
    def test_small_cluster_withheld(self):
        self.assertIsNone(cluster_bootstrap_mean([1,2],['a','b'])['lower'])
    def test_holm(self):
        self.assertAlmostEqual(holm_adjust([.01,.04,.03])[0],.03); self.assertEqual(holm_adjust([.5,.5]),[1,1])
    def test_scores(self):
        self.assertAlmostEqual(log_loss([.5,.5],[1,0]),math.log(2)); self.assertAlmostEqual(brier([.5,.5],[1,0]),.25)
    def test_drawdown(self):
        self.assertAlmostEqual(max_drawdown([1,-.2,-.3,1]),.5)

class ModelTests(unittest.TestCase):
    def games(self,n=100):
        return [Game(str(i),2025,i//10+1,'A' if i%2 else 'B','B' if i%2 else 'A',24+(i%3),17+(i%2),False,'https://www.nfl.com/games/test',f'2025-10-{i%28+1:02d}T00:00:00Z') for i in range(n)]
    def test_insufficient_data_blocked(self):
        with self.assertRaises(ValueError): RidgeBaseline().fit(self.games(10),['A','B'])
    def test_symmetry_and_no_hfa_neutral(self):
        m=RidgeBaseline(ridge=20).fit(self.games(),['A','B'])
        p=m.predict('A','B',neutral=True); q=m.predict('B','A',neutral=True); self.assertAlmostEqual(p['expected_home_margin'],-q['expected_home_margin']); self.assertAlmostEqual(p['expected_total'],q['expected_total'])
        h=m.predict('A','B'); self.assertNotEqual(h['expected_home_margin'],p['expected_home_margin'])
    def test_future_leakage_rejected(self):
        m=RidgeBaseline().fit(self.games(),['A','B'])
        with self.assertRaises(ValueError): m.predict('A','B',decision_at='2024-01-01T00:00:00Z')
    def test_unofficial_game_rejected(self):
        g=self.games(100); g[0]=Game('x',2025,1,'A','B',20,10,False,'https://example.com','2025-10-01')
        with self.assertRaises(ValueError): RidgeBaseline().fit(g,['A','B'])
    def test_probabilities_sum_to_one(self):
        p=RidgeBaseline().fit(self.games(),['A','B']).predict('A','B'); self.assertAlmostEqual(p['home_win_probability']+p['home_loss_probability']+p['tie_probability'],1)

class GradingTests(unittest.TestCase):
    def test_spread_push(self):
        self.assertEqual(grade_single('spread','home',-3,3,-110,'two_way_push')['result'],'push')
    def test_total(self):
        self.assertEqual(grade_single('total','over',44.5,45,-110,'two_way_push')['result'],'win')
    def test_moneyline_tie(self):
        self.assertEqual(grade_single('moneyline','home',0,0,-110,'void_tie')['result'],'push')
        self.assertEqual(grade_single('moneyline','home',0,0,-110,'three_way')['result'],'loss')
    def test_parlay_void_reduces_price(self):
        legs=[{'result':'win','american_odds':100},{'result':'void','american_odds':100}]
        self.assertAlmostEqual(grade_parlay(legs)['profit_units'],1)
    def test_parlay_loss(self):
        self.assertEqual(grade_parlay([{'result':'loss','american_odds':100}])['profit_units'],-1)

class ValidationTests(unittest.TestCase):
    def test_missing_evidence_fails(self):
        r=evaluate_gates({},{}); self.assertFalse(r['eligible']); self.assertEqual(len(r['gates']),len(GATES)); self.assertFalse(r['real_money_enabled'])
    def test_lucky_roi_cannot_pass_alone(self):
        r=evaluate_gates({},{'settled_tickets':1000,'net_roi_mean':.5}); self.assertFalse(r['eligible'])
    def test_empty_leaderboard(self):
        b=leaderboard([{'id':'x','market':'single','validation':{'eligible':False}}]); self.assertEqual(b['boards']['single'],[])
    def test_real_money_never_ranked(self):
        b=leaderboard([{'id':'x','market':'single','validation':{'eligible':True,'real_money_enabled':True},'metrics':{'clv_mean':1,'proper_score_improvement_mean':1,'net_roi_mean':1}}]); self.assertEqual(b['boards']['single'],[])

if __name__=='__main__': unittest.main()
