"""Transparent paper grading. Market-specific settlement must be supplied."""
from __future__ import annotations
from .odds import american_to_decimal


def grade_single(market, selection, line, actual, american_odds, settlement):
    """Return win/loss/push/void; never infer a book's settlement contract.

    spread: selection home/away; line is the handicap added to that score.
    total: selection over/under; actual is combined regulation+OT points if the
    supplied settlement says overtime counts. moneyline must specify ties.
    """
    if settlement not in {'two_way_push','three_way','void_tie'}: raise ValueError('Explicit supported settlement required')
    if market=='spread':
        if selection not in {'home','away'}: raise ValueError('Invalid spread side')
        adjusted=actual+line
        result='push' if adjusted==0 else 'win' if adjusted>0 else 'loss'
    elif market=='total':
        if selection not in {'over','under'}: raise ValueError('Invalid total side')
        result='push' if actual==line else (('win' if actual>line else 'loss') if selection=='over' else ('win' if actual<line else 'loss'))
    elif market=='moneyline':
        if selection not in {'home','away'} or actual==0 and settlement not in {'three_way','void_tie'}: raise ValueError('Tie settlement required')
        if actual==0: result='push' if settlement=='void_tie' else 'loss'
        else: result='win' if (actual>0)==(selection=='home') else 'loss'
    else: raise ValueError('Unsupported market; player props require their own settlement adapter')
    profit=0.0 if result in {'push','void'} else american_to_decimal(american_odds)-1 if result=='win' else -1.0
    return {'result':result,'profit_units':profit,'stake_units':1.0,'settlement':settlement}


def grade_parlay(legs):
    """Each leg needs an explicit result; void/push reduces the ticket price.

    This is a common paper convention, NOT a universal sportsbook rule.
    A live strategy must provide and test its book-specific contract.
    """
    if not legs: raise ValueError('Empty ticket')
    decimal=1.0; active=0
    for leg in legs:
        result=leg['result']
        if result not in {'win','loss','push','void'}: raise ValueError('Invalid leg result')
        if result=='loss': return {'result':'loss','profit_units':-1.0,'stake_units':1.0,'active_legs':active}
        if result=='win': decimal*=american_to_decimal(leg['american_odds']); active+=1
    if not active: return {'result':'void','profit_units':0.0,'stake_units':1.0,'active_legs':0}
    return {'result':'win','profit_units':decimal-1,'stake_units':1.0,'active_legs':active}
