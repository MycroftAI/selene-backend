from datetime import date
from typing import Tuple, List

from selene.data.account import Agreement, AgreementRepository

terms_of_use_attrs = dict(
    type='Terms of Use',
    version='HolyGrail',
    content='I agree that all the tests I write for this application will be '
            'in the theme of Monty Python and the Holy Grail.  If you do not '
            'agree with these terms, I will be forced to say "Ni!" until such '
            'time as you agree',
    effective_date=date(1975, 3, 14)
)

privacy_policy_attrs = dict(
    type='Privacy Policy',
    version='GoT',
    content='First, shalt thou take out the Holy Pin.  Then shalt thou count'
            'to three.  No more.  No less.  Three shalt be the number thou'
            'shalt count and the number of the counting shall be three.  Four'
            'shalt thou not count, nor either count thou two, excepting that'
            'thou then proceed to three.  Five is right out.  Once the number'
            'three, being the third number, be reached, then lobbest thou'
            'Holy Hand Grenade of Antioch towards thy foe, who, being naughty'
            'in My sight, shall snuff it.',
    effective_date=date(1975, 3, 14)
)


def insert_agreements(db) -> Tuple[Agreement, Agreement]:
    terms_of_use = Agreement(**terms_of_use_attrs)
    privacy_policy = Agreement(**privacy_policy_attrs)
    agreement_repository = AgreementRepository(db)
    terms_of_use.id = agreement_repository.add(terms_of_use)
    privacy_policy.id = agreement_repository.add(privacy_policy)

    return terms_of_use, privacy_policy


def delete_agreements(db, agreements: List[Agreement]):
    for agreement in agreements:
        agreement_repository = AgreementRepository(db)
        agreement_repository.remove(agreement, testing=True)
