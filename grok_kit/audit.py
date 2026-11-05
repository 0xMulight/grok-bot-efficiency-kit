"""Offline, assumption-based Routine call counter. No access to Grok billing."""
from __future__ import annotations
import json
import math
from pathlib import Path
from .core import KitError


def audit_routines(doc:dict)->dict:
    rows=doc.get('routines')
    if not isinstance(rows,list):
        raise KitError('JSON must contain routines list')
    out=[]; total_old=total_proposed=0
    for row in rows:
        if not isinstance(row,dict) or 'name' not in row:
            raise KitError('Every routine needs a name')
        name=str(row['name'])[:120]
        if not row.get('enabled',True):
            out.append({'name':name,'enabled':False,'note':'Paused; baseline is zero'})
            continue
        cadence=float(row.get('interval_minutes',0))
        hours=float(row.get('active_hours_per_day',24))
        triggers=row.get('estimated_events_per_day',None)
        if not (cadence>=5 and cadence<=10080 and 0<hours<=24):
            raise KitError(f'Invalid interval/hours for {name}')
        baseline=math.ceil(hours*60/cadence)*7
        proposal=None
        if triggers is not None:
            ev=float(triggers)
            if not (0<=ev<=1000):
                raise KitError(f'Invalid expected events for {name}')
            proposal=math.ceil(ev*7)
        total_old+=baseline
        if proposal is not None:
            total_proposed+=proposal
        out.append({'name':name,'enabled':True,'scheduled_calls_per_week':baseline,
                    'estimated_triggered_calls_per_week':proposal,
                    'estimated_calls_avoided_per_week':max(0,baseline-proposal) if proposal is not None else None,
                    'recommendation':('Consider webhook + local filters' if proposal is not None and proposal<baseline else
                                      'Keep schedule or collect event frequency before changing')})
    return {'routines':out,'weekly_scheduled_calls':total_old,
            'weekly_estimated_triggered_calls_for_modeled_items':total_proposed,
            'basis':'User-provided schedule and event estimates; not actual Grok usage or token accounting',
            'no_changes_made':True}


def audit_file(path:str)->dict:
    try:
        doc=json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError) as e:
        raise KitError('Cannot parse routines JSON: '+str(e)) from e
    return audit_routines(doc)
