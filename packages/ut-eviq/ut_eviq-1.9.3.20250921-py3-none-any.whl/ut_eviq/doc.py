"""
This module provides utility classes for the management of OmniTracker
EcoVadis NHRR (Nachhaltigkeits Risiko Rating) processing for Department UMH
"""
from ut_eviq.rst.taskioc import TaskIoc as EviqRstTaskIoc
from ut_eviq.xls.taskioc import TaskIoc as EviqXlsTaskIoc

from typing import Any
TyDic = dict[Any, Any]


DoDoC = {

    'xls': {
        'xls evupadm': EviqXlsTaskIoc.evupadm,
        'xls evupdel': EviqXlsTaskIoc.evupdel,
        'xls evupreg': EviqXlsTaskIoc.evupreg,
        'xls evdomap': EviqXlsTaskIoc.evdomap,
    },
    'rst': {
        'rst evupadm': EviqRstTaskIoc.evupadm,
        'rst evupdel': EviqRstTaskIoc.evupdel,
        'rst evupreg': EviqRstTaskIoc.evupreg,
        'rst evdoexp': EviqRstTaskIoc.evdoexp,
        'rst evdomap': EviqRstTaskIoc.evdomap,
    },
}
